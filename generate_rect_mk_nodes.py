"""
Generate rectangular mk nodes for k=2,3,4.
Starting matrix: [n+k, 0, n, 0] (R0 = C0 + k, R0 > C0 by k).
Chain dependency: m2 depends on square+p1+m1, m3 on +m2, m4 on +m3.

Key fix: terminal nodes with no possible moves (e.g. [n,0,0,0], [0,0,n,0])
are treated as Win points (isWin=True), same as [0,0,0,0].
These arise when all move conditions fail:
  - e step:  R0 >= 1 and C0 >= 1
  - r step:  R1 >= 1 and C0 >= 1
  - c step:  R0 >= 1 and C1 >= 1
If none apply, the node is a true terminal and wins like [0,0,0,0].
"""
import json
from collections import deque


def adjust_matrix(M):
    a, c = M[0]  # R0, R1
    b, d = M[1]  # C0, C1
    c = min(c, b)
    d = min(d, a)
    return [[a, c], [b, d]]


def matrix_to_flat(M):
    return [M[0][0], M[0][1], M[1][0], M[1][1]]


def has_any_moves(flat):
    """Return True if any move (e, r, c) is possible from this matrix state."""
    R0, R1, C0, C1 = flat
    if R0 >= 1 and C0 >= 1: return True   # e step
    if R1 >= 1 and C0 >= 1: return True   # r step
    if R0 >= 1 and C1 >= 1: return True   # c step
    return False


def find_position(flat, square_nodes_by_matrix):
    """
    Position by bracketing square nodes with same R0, C0, sorted by R1+C1.
    Returns (n_pos, x, y).
    """
    R0, R1, C0, C1 = flat
    target_sum = R1 + C1

    matching = []
    for sq_flat, sq_node in square_nodes_by_matrix.items():
        sq_R0, sq_R1, sq_C0, sq_C1 = sq_flat
        if sq_R0 == R0 and sq_C0 == C0:
            matching.append({
                "sum": sq_R1 + sq_C1,
                "n": sq_node["n"],
                "x": sq_node["x"],
                "y": sq_node["y"],
            })

    if not matching:
        return (R0 + R1 + C0 + C1) / 2.0, 0, 0

    matching.sort(key=lambda m: m["sum"])

    lower = upper = None
    for m in matching:
        if m["sum"] < target_sum:
            lower = m
        elif upper is None:
            upper = m

    if lower and upper:
        return (lower["n"] + upper["n"]) / 2.0, lower["x"], lower["y"]
    elif lower:
        return lower["n"] + 0.5, lower["x"], lower["y"]
    else:
        return matching[0]["n"] - 0.5, matching[0]["x"], matching[0]["y"]


def generate_rect_mk(k, max_n, known_by_matrix, square_nodes_by_matrix, prefix):
    """
    Generate rect nodes for asymmetry offset k, starting from [n+k, 0, n, 0].
    known_by_matrix: all previously known nodes (square + p1 + m1 + earlier mk).
    prefix: 'm2', 'm3', or 'm4'.
    """
    rect_nodes = {}   # (R0,R1,C0,C1) -> node dict

    for n in range(1, max_n + 1):
        start_matrix = [n + k, 0, n, 0]
        start_key = tuple(start_matrix)
        max_e = (n + 1) // 2   # same rule as p1 / m1

        if start_key in known_by_matrix or start_key in rect_nodes:
            continue

        n_pos, x_pos, y_pos = find_position(start_matrix, square_nodes_by_matrix)
        node_id = f"Rect_{prefix}_{start_matrix[0]}_{start_matrix[1]}_{start_matrix[2]}_{start_matrix[3]}"
        rect_nodes[start_key] = {
            "id": node_id, "n": n_pos, "t": 0,
            "x": x_pos, "y": y_pos,
            "matrix": start_matrix, "nextNodes": [],
            "isWin": None, "grundy": None, "nodeType": f"rect_{prefix}"
        }

        queue = deque([(start_matrix, 0)])
        visited = {start_key}

        while queue:
            current_flat, e_depth = queue.popleft()
            current_key = tuple(current_flat)

            if current_key in known_by_matrix:
                current_id = known_by_matrix[current_key]["id"]
            elif current_key in rect_nodes:
                current_id = rect_nodes[current_key]["id"]
            else:
                continue

            R0, R1, C0, C1 = current_flat
            a, c, b, d = R0, R1, C0, C1

            children = []
            if a >= 1 and b >= 1:
                children.append((matrix_to_flat(adjust_matrix([[a-1, c+1], [b-1, d+1]])), e_depth + 1))
            if c >= 1 and b >= 1:
                children.append((matrix_to_flat(adjust_matrix([[a, c-1], [b-1, d+1]])), e_depth))
            if a >= 1 and d >= 1:
                children.append((matrix_to_flat(adjust_matrix([[a-1, c+1], [b, d-1]])), e_depth))

            for child_flat, child_e_depth in children:
                child_key = tuple(child_flat)

                if child_e_depth > max_e:
                    continue

                is_terminal = False
                if child_key in known_by_matrix:
                    child_id = known_by_matrix[child_key]["id"]
                    is_terminal = True
                elif child_key in rect_nodes:
                    child_id = rect_nodes[child_key]["id"]
                else:
                    child_flat_list = list(child_flat)
                    n_pos2, x_pos2, y_pos2 = find_position(child_flat_list, square_nodes_by_matrix)
                    child_id = f"Rect_{prefix}_{child_flat[0]}_{child_flat[1]}_{child_flat[2]}_{child_flat[3]}"
                    rect_nodes[child_key] = {
                        "id": child_id, "n": n_pos2, "t": child_e_depth,
                        "x": x_pos2, "y": y_pos2,
                        "matrix": child_flat_list, "nextNodes": [],
                        "isWin": None, "grundy": None, "nodeType": f"rect_{prefix}"
                    }

                if current_key in rect_nodes:
                    if child_id not in rect_nodes[current_key]["nextNodes"]:
                        rect_nodes[current_key]["nextNodes"].append(child_id)

                if not is_terminal and child_key not in visited:
                    visited.add(child_key)
                    queue.append((list(child_flat), child_e_depth))

    return list(rect_nodes.values())


def compute_win_loss(rect_nodes, known_by_id):
    """
    Retrograde analysis (Kahn topological sort).
    - True terminal (no moves possible) -> isWin = True  (like [0,0,0,0])
    - Artificially cut-off node (has moves but empty nextNodes) -> isWin = False
    - isWin = True if any child.isWin == False
    - isWin = False if all children.isWin == True (or empty)
    """
    rect_map = {n["id"]: n for n in rect_nodes}
    pending_children = {n["id"]: 0 for n in rect_nodes}
    parents_of = {n["id"]: [] for n in rect_nodes}

    for node in rect_nodes:
        for child_id in node["nextNodes"]:
            if child_id in rect_map:
                pending_children[node["id"]] += 1
                parents_of[child_id].append(node["id"])

    queue = deque(nid for nid, cnt in pending_children.items() if cnt == 0)
    resolved = 0

    while queue:
        nid = queue.popleft()
        node = rect_map[nid]
        resolved += 1

        if not node["nextNodes"]:
            # True terminal (no legal moves) wins like [0,0,0,0]
            # Artificially cut-off nodes (has possible moves but e_depth exceeded) lose
            node["isWin"] = not has_any_moves(node["matrix"])
        else:
            win = False
            for child_id in node["nextNodes"]:
                if child_id in rect_map:
                    child_win = rect_map[child_id]["isWin"]
                else:
                    child_node = known_by_id.get(child_id)
                    child_win = child_node["isWin"] if child_node else None
                if child_win is False:
                    win = True
                    break
            node["isWin"] = win

        for parent_id in parents_of.get(nid, []):
            pending_children[parent_id] -= 1
            if pending_children[parent_id] == 0:
                queue.append(parent_id)

    unresolved = [nid for nid, cnt in pending_children.items() if cnt > 0]
    if unresolved:
        print(f"  警告：{len(unresolved)} 個節點未解析 (可能有環): {unresolved[:5]}")
    else:
        print(f"  所有 {resolved} 個節點已計算 isWin")


if __name__ == "__main__":
    max_n = 8

    with open("src/data.json", "r", encoding="utf-8") as f:
        square_data = json.load(f)
    with open("src/rect_p1_data.json", "r", encoding="utf-8") as f:
        p1_data = json.load(f)
    with open("src/rect_m1_data.json", "r", encoding="utf-8") as f:
        m1_data = json.load(f)

    square_nodes_by_matrix = {tuple(n["matrix"]): n for n in square_data}
    known_by_matrix = {tuple(n["matrix"]): n for n in square_data + p1_data + m1_data}
    known_by_id = {n["id"]: n for n in square_data + p1_data + m1_data}

    for k, prefix in [(2, "m2"), (3, "m3"), (4, "m4")]:
        print(f"\n=== 生成 rect_{prefix} 節點 (k={k}, 起點 [n+{k},0,n,0]) ===")
        mk_data = generate_rect_mk(k, max_n, known_by_matrix, square_nodes_by_matrix, prefix)
        compute_win_loss(mk_data, known_by_id)

        # 顯示終端節點詳情
        terminals = [n for n in mk_data if not n["nextNodes"]]
        true_terminals = [n for n in terminals if not has_any_moves(n["matrix"])]
        print(f"  終端節點: {len(terminals)} 個, 其中真實終點（無合法移動）: {len(true_terminals)} 個")
        for t in true_terminals:
            print(f"    {t['id']} matrix={t['matrix']} isWin={t['isWin']}")

        out_path = f"src/rect_{prefix}_data.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(mk_data, f, ensure_ascii=False, indent=2)

        wins = sum(1 for n in mk_data if n["isWin"] is True)
        losses = sum(1 for n in mk_data if n["isWin"] is False)
        unknowns = sum(1 for n in mk_data if n["isWin"] is None)
        print(f"產生 {len(mk_data)} 個節點 -> {out_path}")
        print(f"  Win: {wins}, Lose: {losses}, Unknown: {unknowns}")

        # 加入 known，供後續 k 使用
        for node in mk_data:
            key = tuple(node["matrix"])
            if key not in known_by_matrix:
                known_by_matrix[key] = node
                known_by_id[node["id"]] = node
