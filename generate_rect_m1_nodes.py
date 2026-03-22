"""
Generate rectangular m1 nodes: starting from [n+1, 0, n, 0] (R0=n+1, C0=n).
Mirror of p1 nodes. Duplicate detection against square AND p1 nodes.
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


def matrix_to_id(R0, R1, C0, C1):
    """New universal ID: {rows}x{cols}_{R1}_{C1}"""
    return f"{R0+R1}x{C0+C1}_{R1}_{C1}"


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
        row_total = R0 + R1
        col_total = C0 + C1
        return (row_total + col_total) / 2.0, 0, 0

    matching.sort(key=lambda m: m["sum"])

    lower = None
    upper = None
    for m in matching:
        if m["sum"] < target_sum:
            lower = m
        else:
            if upper is None:
                upper = m

    if lower is not None and upper is not None:
        n_pos = (lower["n"] + upper["n"]) / 2.0
        return n_pos, lower["x"], lower["y"]
    elif lower is not None:
        return lower["n"] + 0.5, lower["x"], lower["y"]
    else:
        closest = matching[0]
        return closest["n"] - 0.5, closest["x"], closest["y"]


def generate_rect_m1(max_n=8):
    with open("src/data.json", "r", encoding="utf-8") as f:
        square_data = json.load(f)
    with open("src/rect_p1_data.json", "r", encoding="utf-8") as f:
        p1_data = json.load(f)

    # All known matrices (square + p1) for duplicate detection
    square_nodes_by_matrix = {}
    square_nodes_by_id = {}
    for node in square_data:
        key = tuple(node["matrix"])
        square_nodes_by_matrix[key] = node
        square_nodes_by_id[node["id"]] = node

    p1_nodes_by_matrix = {}
    p1_nodes_by_id = {}
    for node in p1_data:
        key = tuple(node["matrix"])
        p1_nodes_by_matrix[key] = node
        p1_nodes_by_id[node["id"]] = node

    known_by_matrix = {**square_nodes_by_matrix, **p1_nodes_by_matrix}
    known_by_id = {**square_nodes_by_id, **p1_nodes_by_id}

    rect_nodes = {}   # key: (R0,R1,C0,C1) -> node dict

    for n in range(1, max_n + 1):
        start_matrix = [n + 1, 0, n, 0]
        start_key = tuple(start_matrix)
        max_e = (n + 1) // 2  # floor((n+1)/2), same rule as p1

        # Skip if already known
        if start_key in known_by_matrix:
            continue
        if start_key in rect_nodes:
            continue

        # Build starting node
        n_pos, x_pos, y_pos = find_position(start_matrix, square_nodes_by_matrix)
        R0, R1, C0, C1 = start_matrix
        node_id = matrix_to_id(R0, R1, C0, C1)
        rect_nodes[start_key] = {
            "id": node_id,
            "legacyId": f"Rect_m1_{R0}_{R1}_{C0}_{C1}",
            "tier": R0 + C0,
            "n": n_pos,
            "t": 0,
            "x": x_pos,
            "y": y_pos,
            "matrix": start_matrix,
            "nextNodes": [],
            "isWin": None,
            "grundy": None,
            "nodeType": "rect_m1"
        }

        queue = deque([(start_matrix, 0)])
        visited = {start_key}

        while queue:
            current_flat, e_depth = queue.popleft()
            current_key = tuple(current_flat)

            if current_key in square_nodes_by_matrix:
                current_id = square_nodes_by_matrix[current_key]["id"]
            elif current_key in p1_nodes_by_matrix:
                current_id = p1_nodes_by_matrix[current_key]["id"]
            elif current_key in rect_nodes:
                current_id = rect_nodes[current_key]["id"]
            else:
                continue

            R0, R1, C0, C1 = current_flat
            a, c = R0, R1
            b, d = C0, C1

            children = []
            if a >= 1 and b >= 1:
                M_e = adjust_matrix([[a - 1, c + 1], [b - 1, d + 1]])
                children.append((matrix_to_flat(M_e), e_depth + 1))
            if c >= 1 and b >= 1:
                M_r = adjust_matrix([[a, c - 1], [b - 1, d + 1]])
                children.append((matrix_to_flat(M_r), e_depth))
            if a >= 1 and d >= 1:
                M_c = adjust_matrix([[a - 1, c + 1], [b, d - 1]])
                children.append((matrix_to_flat(M_c), e_depth))

            for child_flat, child_e_depth in children:
                child_key = tuple(child_flat)

                if child_e_depth > max_e:
                    continue

                child_id = None
                is_terminal = False

                if child_key in square_nodes_by_matrix:
                    child_id = square_nodes_by_matrix[child_key]["id"]
                    is_terminal = True
                elif child_key in p1_nodes_by_matrix:
                    child_id = p1_nodes_by_matrix[child_key]["id"]
                    is_terminal = True
                elif child_key in rect_nodes:
                    child_id = rect_nodes[child_key]["id"]
                else:
                    child_flat_list = list(child_flat)
                    n_pos2, x_pos2, y_pos2 = find_position(child_flat_list, square_nodes_by_matrix)
                    cR0, cR1, cC0, cC1 = child_flat
                    child_id = matrix_to_id(cR0, cR1, cC0, cC1)
                    rect_nodes[child_key] = {
                        "id": child_id,
                        "legacyId": f"Rect_m1_{cR0}_{cR1}_{cC0}_{cC1}",
                        "tier": cR0 + cC0,
                        "n": n_pos2,
                        "t": child_e_depth,
                        "x": x_pos2,
                        "y": y_pos2,
                        "matrix": child_flat_list,
                        "nextNodes": [],
                        "isWin": None,
                        "grundy": None,
                        "nodeType": "rect_m1"
                    }

                if current_key in rect_nodes:
                    if child_id not in rect_nodes[current_key]["nextNodes"]:
                        rect_nodes[current_key]["nextNodes"].append(child_id)

                if not is_terminal and child_key not in visited:
                    visited.add(child_key)
                    queue.append((list(child_flat), child_e_depth))

    return list(rect_nodes.values())


def compute_win_loss(rect_nodes, known_by_id):
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

        win = False
        for child_id in node["nextNodes"]:
            if child_id in rect_map:
                child_win = rect_map[child_id]["isWin"]
            elif child_id in known_by_id:
                child_win = known_by_id[child_id]["isWin"]
            else:
                child_win = None

            if child_win is False:
                win = True
                break

        node["isWin"] = False if not node["nextNodes"] else win

        for parent_id in parents_of[nid]:
            pending_children[parent_id] -= 1
            if pending_children[parent_id] == 0:
                queue.append(parent_id)

    unresolved = [nid for nid, cnt in pending_children.items() if cnt > 0]
    if unresolved:
        print(f"  警告：{len(unresolved)} 個節點未解析: {unresolved[:5]}")
    else:
        print(f"  所有 {resolved} 個 m1 節點已計算 isWin")


if __name__ == "__main__":
    m1_data = generate_rect_m1(8)

    with open("src/data.json", "r", encoding="utf-8") as f:
        square_data = json.load(f)
    with open("src/rect_p1_data.json", "r", encoding="utf-8") as f:
        p1_data = json.load(f)

    known_by_id = {n["id"]: n for n in square_data + p1_data}
    compute_win_loss(m1_data, known_by_id)

    with open("src/rect_m1_data.json", "w", encoding="utf-8") as f:
        json.dump(m1_data, f, ensure_ascii=False, indent=2)

    wins = sum(1 for n in m1_data if n["isWin"] is True)
    losses = sum(1 for n in m1_data if n["isWin"] is False)
    unknowns = sum(1 for n in m1_data if n["isWin"] is None)
    print(f"產生 {len(m1_data)} 個 m1 節點 → src/rect_m1_data.json")
    print(f"  Win: {wins}, Lose: {losses}, Unknown: {unknowns}")
