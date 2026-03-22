# DoubleChess Layer - 3D Game Tree Visualizer

An interactive, high-performance 3D visualization Web Application designed to compute, map, and explore the mathematical Game Tree of "DoubleChess" up to Level 8.

## Features

- **3D Spatial Mapping**: Instantly visualizes complex Game Tree data. Root nodes start at `Level 8` and flow down geometrically to the end state `Level 0`.
- **Card View Mode**: Seamlessly toggle between abstract 3D Spheres or literal 3D HTML Cards. The Card View natively renders the actual `2x2` state matrix and spatial string representations `(Lv_X_eY_rZ)`.
- **Dynamic Level Slicer**: Highly responsive UI panel that slices through the Data Tree. It includes specific viewing rules enabling deep cross-sectional analysis.
- **Path Tracing (DAG Traversals)**: Click on any active node or card to send dual-directional BFS rays (Ancestors & Descendants) to instantly highlight complete historical and future branch paths.
- **Mathematical Metadata**: Automatically surfaces mathematically computed trajectory counts (e.g., *22,459 Paths* at Level 8) bound to each primary level layer.
- **Retrograde Analysis Mapping**: Instantly identifies Winning nodes (Green/Emerald for square; Cyan for rect) and Losing nodes (Red for square; Amber for rect) via algorithmic retrograde mapping.
- **Rectangular Node Support**: Visualizes asymmetric board states:
  - **p1 nodes**: starting from $[n, 0, n+1, 0]$ (one extra column)
  - **m1 nodes**: starting from $[n+1, 0, n, 0]$ (one extra row)
  - Win/loss computed via retrograde analysis on the rect DAG subgraph
- **Coordinate System Switcher**: Toggle between two coordinate schemes:
  - **Original**: based on node `(n, t, x, y)` fields — preserves the original pyramid layout
  - **Unified**: based directly on matrix values `Z=(R0+C0)*3, X=(R0-C0)*5+(R1-C1), Y=-(R1+C1)*4` — mathematically principled, zero collisions across all 225 nodes
- **Visibility Toggles**: Independently show/hide square, p1, and m1 nodes. "Hide square" mode retains rect-referenced endpoints so edges remain meaningful.

## Tech Stack

- **Vite + React (TypeScript)**
- **Three.js**
- **@react-three/fiber** (R3F)
- **@react-three/drei** (HTML overlays, Cameras, UI helpers)
- **Zustand** (Global Application State & Graph memory)
- **Tailwind CSS**

## Prerequisites

- Node.js (v18+)
- Python 3.10+ (to recalculate or regenerate node data)

## Setup & Running Locally

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd DoubleChessLayer
   ```

2. **Install Frontend Dependencies:**
   ```bash
   npm install
   ```

3. **(Optional) Re-generate graph nodes and coordinates:**
   ```bash
   # Generate square nodes (src/data.json)
   python generate_chess_nodes.py

   # Generate rectangular p1 nodes (src/rect_p1_data.json)
   python generate_rect_p1_nodes.py

   # Generate rectangular m1 nodes (src/rect_m1_data.json)
   python generate_rect_m1_nodes.py

   # Generate coordinate JSON files for both display modes
   python generate_coordinates.py
   ```

4. **Start the Development Server:**
   ```bash
   npm run dev
   ```
   Navigate to `http://localhost:5173`.

5. **Build for Production:**
   ```bash
   npm run build
   npm run preview
   ```

## Data Files

| File | Description |
|---|---|
| `src/data.json` | Square nodes with full `isWin` and `grundy` values |
| `src/rect_p1_data.json` | Rect p1 nodes `[n,0,n+1,0]` with retrograde `isWin` |
| `src/rect_m1_data.json` | Rect m1 nodes `[n+1,0,n,0]` with retrograde `isWin` |
| `src/coords_original.json` | Original coordinate scheme (id → [x,y,z]) |
| `src/coords_unified.json` | Unified coordinate scheme (id → [x,y,z]) |

## Design Overview

This system fundamentally solves the occlusion and cognitive-overload problems inherent to massive interconnected directed acyclic graphs (DAGs). By utilizing 3D depth buffers, spatial segregation, and strict component culling via Zustand state checks, the visualizer preserves interactivity even with exponentially growing node datasets.

The dual coordinate system enables side-by-side comparison of the traditional positional layout against a mathematically grounded projection that encodes remaining pieces (Z), board asymmetry (X), and exchange depth (Y) directly from the game state matrix.
