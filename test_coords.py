import json

def load_nodes():
    with open("d:/GitHub/DoubleChess3DMap/src/data.json", "r", encoding="utf-8") as f:
        square = json.load(f)
    try:
        with open("d:/GitHub/DoubleChess3DMap/src/rect_p1_data.json", "r", encoding="utf-8") as f:
            p1 = json.load(f)
        with open("d:/GitHub/DoubleChess3DMap/src/rect_m1_data.json", "r", encoding="utf-8") as f:
            m1 = json.load(f)
        return square + p1 + m1
    except:
        return square

nodes = load_nodes()

def test_scheme(A, B):
    seen = {}
    collisions = 0
    for node in nodes:
        R0, R1, C0, C1 = node["matrix"]
        Z = R0 + R1 + C0 + C1
        Y = -(R1 + C1)
        X = (R0 - C0) * A + (R1 - C1) * B
        key = (X, Y, Z)
        if key in seen:
            collisions += 1
            # print(f"COLLISION: {seen[key]} and {node['id']} at {key}")
        else:
            seen[key] = node["id"]
    return collisions

print("Testing schemes...")
for a in range(1, 10):
    for b in range(1, 10):
        c = test_scheme(a, b)
        if c == 0:
            print(f"A={a}, B={b} has 0 collisions")
