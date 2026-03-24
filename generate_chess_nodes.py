import json

def adjust_matrix(M):
    """根據性質1調整矩陣：R1 <= C0 且 C1 <= R0"""
    a, c = M[0] # R0, R1
    b, d = M[1] # C0, C1
    c = min(c, b)
    d = min(d, a)
    return [[a, c], [b, d]]

def matrix_to_id(R0, R1, C0, C1):
    """New universal ID: {rows}x{cols}_{R1}_{C1}"""
    return f"{R0+R1}x{C0+C1}_{R1}_{C1}"

def get_legacy_params(R0, R1, C0, C1):
    """Compute legacy (id, n, t, x, y) from matrix for backward compat"""
    a, c, b, d = R0, R1, C0, C1
    if a >= b and d >= c:
        n = 2 * a - b + c
        t = c + a - b
        x = a - b
        return f"Lv{n}_e{t}_r{x}", n, t, x, 0
    elif a <= b and d <= c:
        n = 2 * b - a + d
        t = d + b - a
        y = b - a
        return f"Lv{n}_e{t}_c{y}", n, t, 0, y
    return None, 0, 0, 0, 0

def generate_graph(max_n=6):
    nodes = {}  # key: (R0, R1, C0, C1) tuple -> node dict

    # 1. 建立所有節點 (by matrix, auto-deduplicate)
    for n in range(max_n + 1):
        for t in range((n // 2) + 1):
            # r 側節點
            for x in range(t + 1):
                M = adjust_matrix([[n-t, t-x], [n-t-x, t+x]])
                flat = (M[0][0], M[0][1], M[1][0], M[1][1])
                if flat not in nodes:
                    R0, R1, C0, C1 = flat
                    lid, cn, ct, cx, cy = get_legacy_params(R0, R1, C0, C1)
                    nodes[flat] = {
                        "id": matrix_to_id(R0, R1, C0, C1),
                        "legacyId": lid,
                        "tier": R0 + C0,
                        "n": cn, "t": ct, "x": cx, "y": cy,
                        "matrix": [R0, R1, C0, C1],
                        "nextNodes": [], "isWin": None, "grundy": None,
                        "nodeType": "square"
                    }
            # c 側節點 (從 y=1 開始避免重複中軸)
            for y in range(1, t + 1):
                M = adjust_matrix([[n-t-y, t+y], [n-t, t-y]])
                flat = (M[0][0], M[0][1], M[1][0], M[1][1])
                if flat not in nodes:
                    R0, R1, C0, C1 = flat
                    lid, cn, ct, cx, cy = get_legacy_params(R0, R1, C0, C1)
                    nodes[flat] = {
                        "id": matrix_to_id(R0, R1, C0, C1),
                        "legacyId": lid,
                        "tier": R0 + C0,
                        "n": cn, "t": ct, "x": cx, "y": cy,
                        "matrix": [R0, R1, C0, C1],
                        "nextNodes": [], "isWin": None, "grundy": None,
                        "nodeType": "square"
                    }

    # 2. 建立連線 (Edges) — directly using matrix tuples
    for flat, data in nodes.items():
        R0, R1, C0, C1 = flat
        next_ids = set()

        # 下 e (空白格)
        if R0 >= 1 and C0 >= 1:
            M_e = adjust_matrix([[R0-1, R1+1], [C0-1, C1+1]])
            cf = (M_e[0][0], M_e[0][1], M_e[1][0], M_e[1][1])
            if cf in nodes: next_ids.add(nodes[cf]["id"])

        # 下 r (橫線格)
        if R1 >= 1 and C0 >= 1:
            M_r = adjust_matrix([[R0, R1-1], [C0-1, C1+1]])
            cf = (M_r[0][0], M_r[0][1], M_r[1][0], M_r[1][1])
            if cf in nodes: next_ids.add(nodes[cf]["id"])

        # 下 c (直線格)
        if R0 >= 1 and C1 >= 1:
            M_c = adjust_matrix([[R0-1, R1+1], [C0, C1-1]])
            cf = (M_c[0][0], M_c[0][1], M_c[1][0], M_c[1][1])
            if cf in nodes: next_ids.add(nodes[cf]["id"])

        data["nextNodes"] = list(next_ids)

    # 3. 逆向推導勝敗點 (Retrograde Analysis)
    nodes_by_id = {n["id"]: n for n in nodes.values()}
    changed = True
    while changed:
        changed = False
        for node in nodes.values():
            if node["isWin"] is not None:
                continue

            children = [nodes_by_id[nid] for nid in node["nextNodes"]]

            # 終點為勝點
            if len(children) == 0:
                node["isWin"] = True
                changed = True
            # 子節點有任何一個是勝點，則此點為敗點
            elif any(c["isWin"] is True for c in children):
                node["isWin"] = False
                changed = True
            # 子節點全部是敗點，則此點為勝點
            elif all(c["isWin"] is False for c in children):
                node["isWin"] = True
                changed = True

    # 4. 計算 DP/Grundy (SG) 值 (計算 mex)
    def compute_grundy(node_id):
        node = nodes_by_id[node_id]
        if node["grundy"] is not None:
            return node["grundy"]

        child_grundys = set()
        for child_id in node["nextNodes"]:
            child_grundys.add(compute_grundy(child_id))

        # mex (Minimum Excluded Value)
        g = 0
        while g in child_grundys:
            g += 1

        node["grundy"] = g
        return g

    for node_id in nodes_by_id:
        compute_grundy(node_id)

    return list(nodes.values())

if __name__ == "__main__":
    graph_data = generate_graph(8)
    with open("src/data.json", "w", encoding="utf-8") as f:
        json.dump(graph_data, f, ensure_ascii=False, indent=2)
    print(f"成功產生 {len(graph_data)} 個節點並存至 src/data.json")
