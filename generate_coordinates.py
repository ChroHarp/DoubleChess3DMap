"""
Generate coordinate JSON files for different positioning strategies.
Reads data.json, rect_p1_data.json, rect_m1_data.json, outputs coords_*.json files.
"""
import json

def load_nodes():
    with open("src/data.json", "r", encoding="utf-8") as f:
        square = json.load(f)
    with open("src/rect_p1_data.json", "r", encoding="utf-8") as f:
        p1 = json.load(f)
    with open("src/rect_m1_data.json", "r", encoding="utf-8") as f:
        m1 = json.load(f)
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
        x_pos = (R0 - C0) * 5 + (R1 - C1) * 1
        y_pos = -(R1 + C1) * 4
        z_pos = (R0 + C0) * 3
        coords[node["id"]] = [round(x_pos, 4), round(y_pos, 4), round(z_pos, 4)]
    return coords


def coords_topological(nodes):
    """
    Topological coordinate system mapping mechanics to strict axes:
      Z = (R0 + R1 + C0 + C1) * 3  -- Top-down: drops by 1 per r/c step, invariant under e step.
      Y = -(R1 + C1) * 3           -- Depth: moves back by 2 per e step, invariant under r/c step.
      X = (R0 - C0) * 5 + (R1 - C1) * 1  -- Horizontal: Asymmetry.
    """
    coords = {}
    for node in nodes:
        R0, R1, C0, C1 = node["matrix"]
        x_pos = (R0 - C0) * 5 + (R1 - C1) * 1
        y_pos = -(R1 + C1) * 3
        z_pos = (R0 + R1 + C0 + C1) * 3
        coords[node["id"]] = [round(x_pos, 4), round(y_pos, 4), round(z_pos, 4)]
    return coords


def main():
    nodes = load_nodes()

    original = coords_original(nodes)
    unified = coords_unified(nodes)
    topological = coords_topological(nodes)

    with open("src/coords_original.json", "w", encoding="utf-8") as f:
        json.dump(original, f, indent=2)
    print(f"Written src/coords_original.json ({len(original)} nodes)")

    with open("src/coords_unified.json", "w", encoding="utf-8") as f:
        json.dump(unified, f, indent=2)
    print(f"Written src/coords_unified.json ({len(unified)} nodes)")

    with open("src/coords_topological.json", "w", encoding="utf-8") as f:
        json.dump(topological, f, indent=2)
    print(f"Written src/coords_topological.json ({len(topological)} nodes)")

    # Verify no collisions in each coordinate system
    for name, coord_set in [("original", original), ("unified", unified), ("topological", topological)]:
        seen = {}
        collisions = 0
        for nid, pos in coord_set.items():
            key = tuple(pos)
            if key in seen:
                collisions += 1
                print(f"  COLLISION in {name}: {seen[key]} and {nid} at {pos}")
            else:
                seen[key] = nid
        print(f"{name} collisions: {collisions}")


if __name__ == "__main__":
    main()
