"""
Generate chess nodes WITHOUT the adjust_matrix constraint (R1<=C0, C1<=R0 clamping removed).
Produces three types: square, p1, m1 nodes in separate JSON files.
"""
import json
from collections import deque


def matrix_to_flat(M):
    """[[R0, R1], [C0, C1]] -> [R0, R1, C0, C1]"""
    return [M[0][0], M[0][1], M[1][0], M[1][1]]


def get_children(R0, R1, C0, C1):
    """Generate all valid children via e, c, r moves (NO adjust_matrix)."""
    children = []
    # e step
    if R0 >= 1 and C0 >= 1:
        children.append([R0 - 1, R1 + 1, C0 - 1, C1 + 1])
    # r step
    if R1 >= 1 and C0 >= 1:
        children.append([R0, R1 - 1, C0 - 1, C1 + 1])
    # c step
    if R0 >= 1 and C1 >= 1:
        children.append([R0 - 1, R1 + 1, C0, C1 - 1])
    return children


def generate_nodes(start_positions, prefix, node_type, max_n=8):
    """
    BFS-based node generation from given starting positions.
    No adjust_matrix applied. Each (R0,R1,C0,C1) state appears once.
    """
    nodes = {}  # key: (R0,R1,C0,C1) -> node dict

    for start_flat in start_positions:
        start_key = tuple(start_flat)
        if start_key in nodes:
            continue

        # Create starting node
        nodes[start_key] = make_node(start_flat, prefix, node_type)

        queue = deque([start_flat])

        while queue:
            current = queue.popleft()
            current_key = tuple(current)
            R0, R1, C0, C1 = current

            children = get_children(R0, R1, C0, C1)

            for child_flat in children:
                child_key = tuple(child_flat)

                # Create new node if not seen
                if child_key not in nodes:
                    nodes[child_key] = make_node(child_flat, prefix, node_type)
                    queue.append(child_flat)

                # Add edge
                child_id = nodes[child_key]["id"]
                if child_id not in nodes[current_key]["nextNodes"]:
                    nodes[current_key]["nextNodes"].append(child_id)

    return nodes


def make_node(flat, prefix, node_type):
    """Create a node dict from a flat matrix [R0, R1, C0, C1]."""
    R0, R1, C0, C1 = flat
    if prefix:
        node_id = f"NoAdj_{prefix}_{R0}_{R1}_{C0}_{C1}"
    else:
        node_id = f"NoAdj_{R0}_{R1}_{C0}_{C1}"

    return {
        "id": node_id,
        "n": R0 + C0,           # level (Z-axis height)
        "t": (R1 + C1) / 2,     # e-depth approximation
        "x": R1 - C1,           # row/col asymmetry
        "y": 0,
        "matrix": list(flat),
        "nextNodes": [],
        "isWin": None,
        "grundy": None,
        "nodeType": node_type,
    }


def compute_win_loss(nodes_dict):
    """
    Retrograde analysis via Kahn's topological sort.
    Terminal nodes (no nextNodes) = losing (current player can't move).
    """
    nodes_list = list(nodes_dict.values())
    node_map = {n["id"]: n for n in nodes_list}

    # Count pending rect children for each node
    pending = {n["id"]: 0 for n in nodes_list}
    parents_of = {n["id"]: [] for n in nodes_list}

    for node in nodes_list:
        for child_id in node["nextNodes"]:
            if child_id in node_map:
                pending[node["id"]] += 1
                parents_of[child_id].append(node["id"])

    # Start from leaf nodes (pending == 0)
    queue = deque(nid for nid, cnt in pending.items() if cnt == 0)
    resolved = 0

    while queue:
        nid = queue.popleft()
        node = node_map[nid]
        resolved += 1

        # Terminal: no legal moves = lose
        if not node["nextNodes"]:
            node["isWin"] = False
        else:
            win = False
            for child_id in node["nextNodes"]:
                if node_map[child_id]["isWin"] is False:
                    win = True
                    break
            node["isWin"] = win

        # Notify parents
        for parent_id in parents_of[nid]:
            pending[parent_id] -= 1
            if pending[parent_id] == 0:
                queue.append(parent_id)

    unresolved = [nid for nid, cnt in pending.items() if cnt > 0]
    if unresolved:
        print(f"  WARNING: {len(unresolved)} nodes unresolved (cycle?): {unresolved[:5]}")
    else:
        print(f"  All {resolved} nodes resolved for isWin")


def compute_grundy(nodes_dict):
    """Compute Grundy/SG values via memoized DFS, ordered by R0+C0 ascending."""
    node_map = {n["id"]: n for n in nodes_dict.values()}

    def _grundy(node_id):
        node = node_map[node_id]
        if node["grundy"] is not None:
            return node["grundy"]

        child_grundys = set()
        for child_id in node["nextNodes"]:
            child_grundys.add(_grundy(child_id))

        # mex (minimum excludant)
        g = 0
        while g in child_grundys:
            g += 1

        node["grundy"] = g
        return g

    # Process in ascending R0+C0 order to ensure children computed first
    sorted_nodes = sorted(nodes_dict.values(), key=lambda n: n["n"])
    for node in sorted_nodes:
        _grundy(node["id"])


def generate_and_save(name, start_positions, prefix, node_type, output_path):
    """Generate nodes, compute win/loss + grundy, save to JSON."""
    print(f"\n=== Generating {name} ===")
    nodes_dict = generate_nodes(start_positions, prefix, node_type)
    print(f"  Generated {len(nodes_dict)} nodes")

    compute_win_loss(nodes_dict)
    compute_grundy(nodes_dict)

    nodes_list = list(nodes_dict.values())

    # Stats
    wins = sum(1 for n in nodes_list if n["isWin"] is True)
    losses = sum(1 for n in nodes_list if n["isWin"] is False)
    unknowns = sum(1 for n in nodes_list if n["isWin"] is None)
    terminals = sum(1 for n in nodes_list if not n["nextNodes"])
    print(f"  Win: {wins}, Lose: {losses}, Unknown: {unknowns}")
    print(f"  Terminal nodes (no moves): {terminals}")

    # Show terminal node matrices
    terminal_matrices = [n["matrix"] for n in nodes_list if not n["nextNodes"]]
    unique_patterns = set()
    for m in terminal_matrices:
        # Categorize: [k,0,0,0], [0,0,k,0], [0,0,0,0], or other
        if m[1] == 0 and m[2] == 0 and m[3] == 0:
            unique_patterns.add(f"[k,0,0,0] (k={m[0]})")
        elif m[0] == 0 and m[1] == 0 and m[3] == 0:
            unique_patterns.add(f"[0,0,k,0] (k={m[2]})")
        else:
            unique_patterns.add(f"other: {m}")
    print(f"  Terminal patterns: {sorted(unique_patterns)}")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(nodes_list, f, ensure_ascii=False, indent=2)
    print(f"  Saved to {output_path}")


if __name__ == "__main__":
    MAX_N = 8

    # Square nodes: start from [n, 0, n, 0]
    square_starts = [[n, 0, n, 0] for n in range(MAX_N + 1)]
    generate_and_save(
        "NoAdj Square Nodes",
        square_starts, "", "noadj_square",
        "src/noadj_data.json",
    )

    # Rectangular p1 nodes: start from [n, 0, n+1, 0]
    p1_starts = [[n, 0, n + 1, 0] for n in range(1, MAX_N + 1)]
    generate_and_save(
        "NoAdj Rect p1 Nodes",
        p1_starts, "p1", "noadj_p1",
        "src/noadj_rect_p1_data.json",
    )

    # Rectangular m1 nodes: start from [n+1, 0, n, 0]
    m1_starts = [[n + 1, 0, n, 0] for n in range(1, MAX_N + 1)]
    generate_and_save(
        "NoAdj Rect m1 Nodes",
        m1_starts, "m1", "noadj_m1",
        "src/noadj_rect_m1_data.json",
    )
