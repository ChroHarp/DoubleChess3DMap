import json

with open("d:/GitHub/DoubleChess3DMap/src/data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

rects = [n for n in data if n["id"].startswith("Rect_")]
print(f"Generated {len(rects)} rectangular nodes.")
for r in rects[:10]:
    print(f"ID: {r['id']}, n: {r['n']}, x: {r['x']}, y: {r['y']}, isWin: {r['isWin']}")

test_cases = [[5,0,5,2], [6,0,7,0]]
for target in test_cases:
    found = next((n for n in rects if n["matrix"] == target), None)
    if found:
        print(f"Target {target} placed at n={found['n']}, x={found['x']}, y={found['y']}")
    else:
        print(f"Target {target} not generated.")

