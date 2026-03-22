import json

def adjust_matrix(M):
    """根據性質1調整矩陣：R1 <= C0 且 C1 <= R0"""
    a, c = M[0] # R0, R1
    b, d = M[1] # C0, C1
    c = min(c, b)
    d = min(d, a)
    return [[a, c], [b, d]]

def matrix_to_flat(M):
    """[[R0, R1], [C0, C1]] -> [R0, R1, C0, C1]"""
    return [M[0][0], M[0][1], M[1][0], M[1][1]]

def flat_to_matrix(flat):
    """[R0, R1, C0, C1] -> [[R0, R1], [C0, C1]]"""
    return [[flat[0], flat[1]], [flat[2], flat[3]]]

def get_square_node_id(M):
    """嘗試將矩陣映射回方形節點 ID（與 generate_chess_nodes.py 一致）"""
    a, c = M[0]
    b, d = M[1]
    if a >= b and d >= c:
        n = 2 * a - b + c
        t = c + a - b
        x = a - b
        return f"Lv{n}_e{t}_r{x}"
    elif a <= b and d <= c:
        n = 2 * b - a + d
        t = d + b - a
        y = b - a
        return f"Lv{n}_e{t}_c{y}"
    else:
        return None

def find_position(flat, square_nodes_by_matrix, square_nodes_by_id):
    """
    為矩形節點計算位置 (n, t, x, y)。
    找到 R0, C0 相同的方形節點，依 R1+C1 排序，將矩形節點夾在兩者之間。
    """
    R0, R1, C0, C1 = flat
    target_sum = R1 + C1

    # 找所有 R0, C0 相同的方形節點
    matching = []
    for sq_flat, sq_node in square_nodes_by_matrix.items():
        sq_R0, sq_R1, sq_C0, sq_C1 = sq_flat
        if sq_R0 == R0 and sq_C0 == C0:
            matching.append({
                "sum": sq_R1 + sq_C1,
                "n": sq_node["n"],
                "t": sq_node["t"],
                "x": sq_node["x"],
                "y": sq_node["y"],
            })

    if not matching:
        # 沒有匹配的方形節點，使用公式推算
        row_total = R0 + R1
        col_total = C0 + C1
        return (row_total + col_total) / 2.0, 0, 0

    # 依 R1+C1 排序
    matching.sort(key=lambda m: m["sum"])

    # 找夾擠位置：嚴格小於 target_sum 為下界，>= 為上界
    # 這樣同 R1+C1 的方形節點會在矩形節點上方
    lower = None
    upper = None
    for m in matching:
        if m["sum"] < target_sum:
            lower = m
        else:
            if upper is None:
                upper = m

    if lower is not None and upper is not None:
        # 夾在兩者之間
        n_pos = (lower["n"] + upper["n"]) / 2.0
        x = lower["x"] if lower["x"] == upper["x"] else lower["x"]
        y = lower["y"] if lower["y"] == upper["y"] else lower["y"]
        return n_pos, x, y
    elif lower is not None:
        # 只有下界，放在上方
        n_pos = lower["n"] + 0.5
        return n_pos, lower["x"], lower["y"]
    else:
        # 只有上界（rule 6: 所有鄰居 R1+C1 都更大），放在最小者下方
        closest = matching[0]
        n_pos = closest["n"] - 0.5
        return n_pos, closest["x"], closest["y"]


def generate_rect_p1(max_n=8):
    # 1. 載入方形節點
    with open("src/data.json", "r", encoding="utf-8") as f:
        square_data = json.load(f)

    square_nodes_by_matrix = {}
    square_nodes_by_id = {}
    for node in square_data:
        key = tuple(node["matrix"])
        square_nodes_by_matrix[key] = node
        square_nodes_by_id[node["id"]] = node

    # 2. 生成矩形 p1 節點
    rect_nodes = {}  # key: (R0,R1,C0,C1) -> node dict
    rect_by_id = {}  # key: id -> node dict

    for n in range(1, max_n + 1):
        start_matrix = [n, 0, n + 1, 0]
        start_key = tuple(start_matrix)
        max_e = (n + 1) // 2  # floor((n+1)/2)

        # 檢查起始節點是否已存在於方形節點
        if start_key in square_nodes_by_matrix:
            continue
        # 檢查是否已存在於矩形節點
        if start_key in rect_nodes:
            continue

        # BFS 展開
        # 每個 BFS 項目: (flat_matrix, e_depth)
        queue = [(start_matrix, 0)]
        visited_this_tree = set()
        visited_this_tree.add(start_key)

        # 建立起始節點
        if start_key not in rect_nodes:
            n_pos, x_pos, y_pos = find_position(
                start_matrix, square_nodes_by_matrix, square_nodes_by_id
            )
            node_id = f"Rect_p1_{start_matrix[0]}_{start_matrix[1]}_{start_matrix[2]}_{start_matrix[3]}"
            rect_nodes[start_key] = {
                "id": node_id,
                "n": n_pos,
                "t": 0,  # 起始節點 e_depth = 0
                "x": x_pos,
                "y": y_pos,
                "matrix": start_matrix,
                "nextNodes": [],
                "isWin": None,
                "grundy": None,
                "nodeType": "rect_p1"
            }
            rect_by_id[node_id] = rect_nodes[start_key]

        while queue:
            current_flat, e_depth = queue.pop(0)
            current_key = tuple(current_flat)

            # 找到當前節點的 ID
            if current_key in square_nodes_by_matrix:
                current_id = square_nodes_by_matrix[current_key]["id"]
            elif current_key in rect_nodes:
                current_id = rect_nodes[current_key]["id"]
            else:
                continue

            R0, R1, C0, C1 = current_flat
            M = [[R0, R1], [C0, C1]]
            a, c = M[0]
            b, d = M[1]

            children = []

            # e 步
            if a >= 1 and b >= 1:
                M_e = adjust_matrix([[a - 1, c + 1], [b - 1, d + 1]])
                children.append((matrix_to_flat(M_e), e_depth + 1))

            # r 步
            if c >= 1 and b >= 1:
                M_r = adjust_matrix([[a, c - 1], [b - 1, d + 1]])
                children.append((matrix_to_flat(M_r), e_depth))

            # c 步
            if a >= 1 and d >= 1:
                M_c = adjust_matrix([[a - 1, c + 1], [b, d - 1]])
                children.append((matrix_to_flat(M_c), e_depth))

            for child_flat, child_e_depth in children:
                child_key = tuple(child_flat)

                # 檢查 e_depth 限制（只限制 e 步的展開深度）
                if child_e_depth > max_e:
                    continue

                # 確定子節點的 ID
                child_id = None

                # 1. 檢查是否為方形節點
                if child_key in square_nodes_by_matrix:
                    child_id = square_nodes_by_matrix[child_key]["id"]
                # 2. 檢查是否為已存在的矩形節點
                elif child_key in rect_nodes:
                    child_id = rect_nodes[child_key]["id"]
                # 3. 建立新的矩形節點
                else:
                    child_flat_list = list(child_flat)
                    n_pos, x_pos, y_pos = find_position(
                        child_flat_list, square_nodes_by_matrix, square_nodes_by_id
                    )
                    child_id = f"Rect_p1_{child_flat[0]}_{child_flat[1]}_{child_flat[2]}_{child_flat[3]}"
                    rect_nodes[child_key] = {
                        "id": child_id,
                        "n": n_pos,
                        "t": child_e_depth,
                        "x": x_pos,
                        "y": y_pos,
                        "matrix": child_flat_list,
                        "nextNodes": [],
                        "isWin": None,
                        "grundy": None,
                        "nodeType": "rect_p1"
                    }
                    rect_by_id[child_id] = rect_nodes[child_key]

                # 只對矩形節點添加連線（方形節點不修改）
                if current_key in rect_nodes:
                    if child_id not in rect_nodes[current_key]["nextNodes"]:
                        rect_nodes[current_key]["nextNodes"].append(child_id)

                # 繼續展開（只展開矩形節點，不展開方形節點）
                if child_key not in square_nodes_by_matrix and child_key not in visited_this_tree:
                    visited_this_tree.add(child_key)
                    queue.append((list(child_flat), child_e_depth))

    return list(rect_nodes.values())


def compute_win_loss(rect_nodes, square_nodes_by_id):
    """
    DAG 逆向推算 (retrograde analysis)：
    - 終點 (nextNodes 全為方形節點) 直接從方形節點 isWin 計算
    - isWin = 存在至少一個 nextNode.isWin == False（可移至對手輸的位置）
    - isLose = 所有 nextNode.isWin == True，或 nextNodes 為空
    - 用 Kahn 拓撲排序從葉往根處理
    """
    rect_map = {n["id"]: n for n in rect_nodes}

    # 建立 rect 子圖的 in-degree（父→子方向為 forward，我們要 leaf-first）
    # forward: parent -> children  (nextNodes)
    # 我們需要知道每個節點「有幾個 rect 子節點尚未解決」
    pending_children = {n["id"]: 0 for n in rect_nodes}
    parents_of = {n["id"]: [] for n in rect_nodes}

    for node in rect_nodes:
        for child_id in node["nextNodes"]:
            if child_id in rect_map:
                pending_children[node["id"]] += 1
                parents_of[child_id].append(node["id"])

    # 初始化：pending_children == 0 的節點（所有子節點都是方形節點）
    from collections import deque
    queue = deque(nid for nid, cnt in pending_children.items() if cnt == 0)

    resolved = 0
    while queue:
        nid = queue.popleft()
        node = rect_map[nid]
        resolved += 1

        # 計算此節點的 isWin
        win = False
        for child_id in node["nextNodes"]:
            if child_id in rect_map:
                child_win = rect_map[child_id]["isWin"]
            elif child_id in square_nodes_by_id:
                child_win = square_nodes_by_id[child_id]["isWin"]
            else:
                child_win = None

            if child_win is False:
                win = True
                break

        if not node["nextNodes"]:
            win = False  # 沒有合法移動 = 輸

        node["isWin"] = win

        # 通知父節點
        for parent_id in parents_of[nid]:
            pending_children[parent_id] -= 1
            if pending_children[parent_id] == 0:
                queue.append(parent_id)

    unresolved = [nid for nid, cnt in pending_children.items() if cnt > 0]
    if unresolved:
        print(f"  警告：{len(unresolved)} 個節點未能解析（可能有環）: {unresolved[:5]}")
    else:
        print(f"  所有 {resolved} 個矩形節點已計算 isWin")


if __name__ == "__main__":
    rect_data = generate_rect_p1(8)

    # 載入方形節點的 isWin 值
    with open("src/data.json", "r", encoding="utf-8") as f:
        square_data = json.load(f)
    square_nodes_by_id = {n["id"]: n for n in square_data}

    compute_win_loss(rect_data, square_nodes_by_id)

    with open("src/rect_p1_data.json", "w", encoding="utf-8") as f:
        json.dump(rect_data, f, ensure_ascii=False, indent=2)
    print(f"成功產生 {len(rect_data)} 個矩形 p1 節點並存至 src/rect_p1_data.json")

    # 顯示摘要
    wins = sum(1 for n in rect_data if n["isWin"] is True)
    losses = sum(1 for n in rect_data if n["isWin"] is False)
    unknowns = sum(1 for n in rect_data if n["isWin"] is None)
    print(f"  Win: {wins}, Lose: {losses}, Unknown: {unknowns}")
