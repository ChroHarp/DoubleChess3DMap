import json

def count_paths_all_levels():
    # 載入節點資料
    try:
        with open('src/data.json', 'r', encoding='utf-8') as f:
            graph_data = json.load(f)
    except FileNotFoundError:
        print("Error: src/data.json file not found.")
        return

    # 建立 Adjacency List (Lookup Table)
    adjacency_list = { node['id']: node['nextNodes'] for node in graph_data }

    # DFS + Memoization
    memo = {}
    def count_paths(current_id, target_id):
        if current_id == target_id:
            return 1
        if current_id in memo:
            return memo[current_id]
        
        total = 0
        for child_id in adjacency_list.get(current_id, []):
            total += count_paths(child_id, target_id)
            
        memo[current_id] = total
        return total

    target_node_id = "Lv0_e0_r0"  # 結束點 [0,0,0,0]

    print("Path counts from [n,0,n,0] to [0,0,0,0]:")
    print("-" * 40)
    for n in range(1, 9):
        start_node_id = f"Lv{n}_e0_r0"  # [n,0,n,0] 其 t=0, x=0, y=0 必為 e0_r0
        if start_node_id in adjacency_list:
            # 清空 memo 以確保每次計算獨立 (不過其實終點一樣，共用 memo 也可以，甚至共用更快)
            ways = count_paths(start_node_id, target_node_id)
            print(f"n = {n} ({start_node_id}): {ways} ways")
        else:
            print(f"n = {n} ({start_node_id}): Node not found in graph")
            
if __name__ == "__main__":
    count_paths_all_levels()
