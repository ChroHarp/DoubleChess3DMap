import json

with open("d:/GitHub/DoubleChess3DMap/src/data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

nodes = {n["id"]: n for n in data}
zero_edges = []

for node in data:
    for child_id in node["nextNodes"]:
        if child_id in nodes:
            c = nodes[child_id]
            if node["n"] == c["n"] and node["x"] == c["x"] and node["y"] == c["y"] and node["t"] == c["t"]:
                zero_edges.append((node["id"], child_id))

if zero_edges:
    print(f"FOUND {len(zero_edges)} ZERO-LENGTH EDGES!")
    for e in zero_edges[:5]:
        print(f"{e[0]} -> {e[1]}")
else:
    print("No zero-length edges found.")
