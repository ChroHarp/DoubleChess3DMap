# DoubleChess Layer - 3D Game Tree Visualizer ♟️🎲

An interactive, high-performance 3D visualization Web Application designed to compute, map, and explore the mathematical Game Tree of "DoubleChess" up to Level 8.

## Features ✨

*   **3D Spatial Mapping**: Instantly visualizes complex Game Tree data. Root nodes start at `Level 8` and flow down geometrically to the end state `Level 0`.
*   **Card View Mode**: Seamlessly toggle between abstract 3D Spheres or literal 3D HTML Cards. The Card View natively renders the actual `2x2` state matrix and spatial string representations `(Lv_X_eY_rZ)`.
*   **Dynamic Level Slicer**: Highly responsive Tailwind UI panel that slices through the Data Tree. It includes specific viewing rules (e.g., viewing `n`, `n-1`, and specific bottom layers of `n-2`), enabling deep cross-sectional analysis.
*   **Path Tracing (DAG Traversals)**: Click on any active node or card to send dual-directional BFS rays (Ancestors & Descendants) to instantly highlight complete historical and future branch paths.
*   **Mathematical Metadata**: Automatically surfaces mathematically computed trajectory counts (e.g., *22,459 Paths* at Level 8) bound to each primary level layer.
*   **Retrograde Analysis Mapping**: Instantly identifies Winning points (Green/Emerald) and Losing points (Red) via algorithmic retrograde mapping.

## Tech Stack 🛠️

*   **Vite + React (TypeScript)**
*   **Three.js** 
*   **@react-three/fiber** (R3F)
*   **@react-three/drei** (HTML overlays, Cameras, UI helpers)
*   **Zustand** (Global Application State & Graph memory)
*   **Tailwind CSS**

## Prerequisites

- Node.js (v18+)
- Python 3.10+ (If you wish to recalculate mathematical nodes)

## Setup & Running Locally 🚀

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd DoubleChessLayer
   ```

2. **Install Frontend Dependencies:**
   ```bash
   npm install
   ```

3. **(Optional) Re-calculate graph nodes:**
   If you wish to alter the depth of the graph or adjust the validation metrics, run the Python script. It will automatically export the valid DAG payload to `src/data.json`.
   ```bash
   python generate_chess_nodes.py
   python calculate_paths.py
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

## Design Overview

This system fundamentally solves the occlusion and cognitive-overload problems inherent to massive interconnected directed acyclic graphs (DAGs). By utilizing 3D depth buffers, spatial segregation (`z = level`, `y = empty cells`, `x = row/col shifts`), and strict component culling via Zustand state checks, the visualizer preserves full 60FPS interactivity even with exponentially growing node datasets.
