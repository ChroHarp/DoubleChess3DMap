"""
Generate coordinate JSON files for different positioning strategies.
Reads data.json and rect_p1_data.json, outputs coords_*.json files.
"""
import json

def load_nodes():
    with open("src/data.json", "r", encoding="utf-8") as f:
        square = json.load(f)
    with open("src/rect_p1_data.json", "r", encoding="utf-8") as f:
        p1 = json.load(f)
    with open("src/rect_m1_data.json", "r", encoding="utf-8") as f:
        m1 = json.load(f)
    for n in square:
        n.setdefault("nodeType", "square")
    for n in p1:
        n.setdefault("nodeType", "rect_p1")
    for n in m1:
        n.setdefault("nodeType", "rect_m1")
    return square + p1 + m1


def coords_original(nodes):
    """Original coordinate system: z=n*5, y=-t*3, x=(r or -c)*3"""
    coords = {}
    for node in nodes:
        x_pos = (node["x"] if node["x"] > 0 else -node["y"]) * 3
        y_pos = node["t"] * -3
        z_pos = node["n"] * 5
        coords[node["id"]] = [round(x_pos, 4), round(y_pos, 4), round(z_pos, 4)]
    return coords


def coords_unified(nodes):
    """
    Unified coordinate system based on matrix values:
      Z = (R0 + C0) * 2.5       -- remaining pieces (game progress)
      X = (R0 - C0) * 2 + (R1 - C1) * 0.5  -- asymmetry
      Y = -(R1 + C1) * 2        -- placed pieces (depth)
    """
    coords = {}
    for node in nodes:
        R0, R1, C0, C1 = node["matrix"]
        # X = (R0-C0)*5 + (R1-C1)*1 ensures:
        #   - Nodes with same R0+C0 but different asymmetry are 5 units apart
        #   - Transpose-symmetric pairs (e.g. p1/m1 mirrors) get opposite X signs
        #   - No collisions among all 225 nodes (verified)
        x_pos = (R0 - C0) * 5 + (R1 - C1) * 1
        y_pos = -(R1 + C1) * 4
        z_pos = (R0 + C0) * 3
        coords[node["id"]] = [round(x_pos, 4), round(y_pos, 4), round(z_pos, 4)]
    return coords


def main():
    nodes = load_nodes()

    original = coords_original(nodes)
    unified = coords_unified(nodes)

    with open("src/coords_original.json", "w", encoding="utf-8") as f:
        json.dump(original, f, indent=2)
    print(f"Written src/coords_original.json ({len(original)} nodes)")

    with open("src/coords_unified.json", "w", encoding="utf-8") as f:
        json.dump(unified, f, indent=2)
    print(f"Written src/coords_unified.json ({len(unified)} nodes)")

    # Verify no collisions in unified
    seen = {}
    collisions = 0
    for nid, pos in unified.items():
        key = tuple(pos)
        if key in seen:
            collisions += 1
            print(f"  COLLISION: {seen[key]} and {nid} at {pos}")
        else:
            seen[key] = nid
    print(f"Unified collisions: {collisions}")


if __name__ == "__main__":
    main()
