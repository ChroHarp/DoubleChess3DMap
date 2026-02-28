import json

def adjust_matrix(M):
    """根據性質1調整矩陣：R1 <= C0 且 C1 <= R0"""
    a, c = M[0] # R0, R1
    b, d = M[1] # C0, C1
    c = min(c, b)
    d = min(d, a)
    return [[a, c], [b, d]]

def get_node_id(M):
    """根據定理2，將矩陣反推回節點 ID"""
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

def generate_graph(max_n=6):
    nodes = {}
    
    # 1. 建立所有 n=0 到 max_n 的節點
    for n in range(max_n + 1):
        for t in range((n // 2) + 1):
            # r 側節點
            for x in range(t + 1):
                M = adjust_matrix([[n-t, t-x], [n-t-x, t+x]])
                node_id = f"Lv{n}_e{t}_r{x}"
                nodes[node_id] = {
                    "id": node_id, "n": n, "t": t, "x": x, "y": 0,
                    "matrix": [M[0][0], M[0][1], M[1][0], M[1][1]],
                    "nextNodes": [], "isWin": None
                }
            # c 側節點 (從 y=1 開始避免重複中軸)
            for y in range(1, t + 1):
                M = adjust_matrix([[n-t-y, t+y], [n-t, t-y]])
                node_id = f"Lv{n}_e{t}_c{y}"
                nodes[node_id] = {
                    "id": node_id, "n": n, "t": t, "x": 0, "y": y,
                    "matrix": [M[0][0], M[0][1], M[1][0], M[1][1]],
                    "nextNodes": [], "isWin": None
                }
                
    # 2. 建立連線 (Edges)
    for node_id, data in nodes.items():
        M = [[data["matrix"][0], data["matrix"][1]], 
             [data["matrix"][2], data["matrix"][3]]]
        a, c = M[0]
        b, d = M[1]
        next_ids = set()

        # 下 e (空白格)
        if a >= 1 and b >= 1:
            M_e = adjust_matrix([[a-1, c+1], [b-1, d+1]])
            n_id = get_node_id(M_e)
            if n_id in nodes: next_ids.add(n_id)

        # 下 r (橫線格)
        if c >= 1 and b >= 1:
            M_r = adjust_matrix([[a, c-1], [b-1, d+1]])
            n_id = get_node_id(M_r)
            if n_id in nodes: next_ids.add(n_id)

        # 下 c (直線格)
        if a >= 1 and d >= 1:
            M_c = adjust_matrix([[a-1, c+1], [b, d-1]])
            n_id = get_node_id(M_c)
            if n_id in nodes: next_ids.add(n_id)

        data["nextNodes"] = list(next_ids)

    # 3. 逆向推導勝敗點 (Retrograde Analysis)
    changed = True
    while changed:
        changed = False
        for node in nodes.values():
            if node["isWin"] is not None:
                continue
            
            children = [nodes[nid] for nid in node["nextNodes"]]
            
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

    return list(nodes.values())

if __name__ == "__main__":
    graph_data = generate_graph(8)
    with open("src/data.json", "w", encoding="utf-8") as f:
        json.dump(graph_data, f, ensure_ascii=False, indent=2)
    print(f"成功產生 {len(graph_data)} 個節點並存至 src/data.json")