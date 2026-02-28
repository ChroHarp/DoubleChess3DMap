# 專案名稱：DoubleChess 3D 棋譜遊戲樹視覺化系統 (3D Game Tree Visualizer)

## 1. 專案概述 (Project Overview)
本專案旨在開發一個 3D 視覺化 Web 應用程式，用以呈現「黑白禁手棋 (DoubleChess)」的數學遊戲樹（Game Tree）。
該遊戲樹具有多維度變數 $Lv(n)e(t)r(x)c(y)$，且節點間具有父子關聯與勝敗屬性。系統需能在 3D 空間中清晰展示節點分佈、勝敗狀態、層級降階關係，並提供使用者友善的視角控制與資料過濾功能。

## 2. 技術棧 (Tech Stack)
* **前端框架:** Vite + React (TypeScript)
* **3D 渲染:** Three.js + React Three Fiber (@react-three/fiber) + Drei (@react-three/drei)
* **UI 組件:** Tailwind CSS (用於懸浮視窗與控制面板)
* **狀態管理:** Zustand 或 React Context (視需求輕量化處理)

## 3. 資料結構定義 (Data Interface)
請預設系統會接收一組 JSON 格式的節點資料，每個節點的 TypeScript Interface 定義如下：

```typescript
interface ChessNode {
  id: string;          // 節點唯一識別碼，格式如 "Lv6_e3_r2_c1"
  n: number;           // 盤面層級 (對應 3D 空間的 Z 軸高度)
  t: number;           // e (空白格) 步數
  x: number;           // r (橫線格) 步數 (對應 3D 空間的 X 軸)
  y: number;           // c (直線格) 步數 (對應 3D 空間的 Y 軸)
  isWin: boolean;      // 是否為勝點 (決定節點材質與顏色)
  matrix: [number, number, number, number]; // 簡化矩陣 [R0, R1, C0, C1]
  nextNodes: string[]; // 存放子節點的 id 陣列 (用於繪製連線 Edges)
}

```

## 4. 3D 空間幾何映射邏輯 (Spatial Mapping)

請將節點資料映射至 3D 場景中，規則如下：

* **Z 軸 (高度):** 綁定節點的 `n` 值。每一層 $Lv(n)$ 應在 Z 軸上有明顯的間距（例如 `z = n * 5`）。
* **X 軸 (橫向):** 綁定節點的 `x` 值。適當放大比例（例如 `x = x * 2`）。
* **Y 軸 (縱向):** 綁定節點的 `y` 值。適當放大比例（例如 `y = y * 2`）。
* *(註：如此映射將使整個結構呈現倒立的漏斗狀或金字塔狀。)*

## 5. 視覺與材質規範 (Visual Specifications)

* **節點 (Nodes):**
* 實作 `<Sphere>` 幾何體。
* `isWin === true`：綠色 (`#10b981`)，並加入些微發光材質 (`MeshStandardMaterial` with `emissive`)。
* `isWin === false`：紅色 (`#ef4444`)，材質稍微暗沈。


* **連線 (Edges):**
* 使用 Drei 的 `<Line>` 組件繪製節點間的連線。
* 一般連線為淡灰色 (`#cbd5e1`)，透明度 0.3。
* **降階連線 (Highlight):** 若連線跨越不同的 Z 軸高度 (父節點 `n` $\neq$ 子節點 `n`)，請將該連線加粗並設為黃色 (`#f59e0b`)，以凸顯降階特徵。



## 6. 核心互動功能 (Interactive Features)

1. **攝影機控制:** 預設載入 Drei 的 `<OrbitControls>`，允許縮放、旋轉、平移。
2. **節點懸停 (Hover Tooltip):** 當滑鼠 Hover 至特定節點時，使用 Drei 的 `<Html>` 標籤彈出一個 Tooltip，顯示該節點的 `id` 以及矩陣數值 `[R0, R1, C0, C1]`。
3. **單一路徑高亮 (Path Tracing):** 當點擊某個節點時，將該節點及其所有相連的連線 (Edges) 與相鄰節點保持原色，其餘不相關的場景物件全部調暗 (Opacity 降至 0.1)。
4. **Z 軸切片器 (Level Slicer UI):** 在螢幕角落實作一個 2D 的 HTML 控制面板，包含範圍到 Lv8 的 Layer Slider。使用者可滑動選擇顯示特定的 `n`，此時隱藏不屬於該層的節點與連線。附加「顯示此階及以下所有層次」與「顯示路徑數量標籤」的切換框。
5. **3D 卡片模式 (Card View Mode):** 支援將 3D 球體切換為 3D HTML 浮動卡片陣列，並透過顏色與文字清楚顯示每一張卡片的屬性`(Lv X e Y c Z)`與矩陣資訊。
6. **動態視角與切片雙層顯示:** 偶數階層時自動擴展向下推移至 n-2 的底部極限，並將攝影機預設視角改為 Level 8，全方位涵蓋完整倒金字塔。

## 7. 開發階段任務清單 (Execution Steps)

* **Step 1:** 初始化 Vite + React + TypeScript 專案，並安裝 Three.js 相關依賴。
* **Step 2:** 建立 `MockData.ts`，生成 10~20 個假節點資料（需包含跨層與勝敗屬性）以供開發測試。
* **Step 3:** 實作基礎 3D 場景 (`<Canvas>`)、燈光與攝影機控制。
* **Step 4:** 撰寫 `NodeMesh` 與 `EdgeLine` 組件，完成資料到 3D 空間的映射與渲染。
* **Step 5:** 實作 Hover 與 Click 的互動邏輯 (Tooltip 與路徑高亮)。
* **Step 6:** 實作前端 HTML 浮動面板，完成 Z 軸層級切換過濾器。

