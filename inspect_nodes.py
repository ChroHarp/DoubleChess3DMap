import json

with open("d:/GitHub/DoubleChess3DMap/src/data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

targets = [
    [2, 4, 4, 2], [2, 4, 4, 1], [2, 4, 3, 1],
    [5, 0, 5, 2], [5, 1, 5, 1], [5, 0, 5, 0],
    [6, 0, 7, 0], [6, 2, 7, 0], [6, 3, 7, 1]
]

for target in targets:
    found = False
    for node in data:
        if node["matrix"] == target:
            print(f"Matrix {target} -> ID: {node['id']}, n: {node['n']}, x: {node['x']}, y: {node['y']}, t: {node['t']}")
            found = True
    if not found:
        print(f"Matrix {target} -> Not found in data.json")
