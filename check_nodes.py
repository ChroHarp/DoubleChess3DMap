import json

with open("d:/GitHub/DoubleChess3DMap/src/data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print("Nodes with R0=2, C0=3:")
for node in data:
    if node["matrix"][0] == 2 and node["matrix"][2] == 3:
        print(f"ID: {node['id']}, matrix: {node['matrix']}, r1+c1: {node['matrix'][1] + node['matrix'][3]}")

print("\nNodes with R0=2, C0=4:")
for node in data:
    if node["matrix"][0] == 2 and node["matrix"][2] == 4:
        print(f"ID: {node['id']}, matrix: {node['matrix']}, r1+c1: {node['matrix'][1] + node['matrix'][3]}")
