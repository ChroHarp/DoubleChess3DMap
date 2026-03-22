# DoubleChess 3D 專案腳本與節點說明

## 1. 專案中各 `.py` 腳本的用途

專案目錄下包含多個 Python 腳本，主要用於數學驗證、資料產生與路徑分析：

1. **`generate_chess_nodes.py`**
   - **用途：** 核心生成腳本。負責產生 DoubleChess 在正方形盤面（$n \times n$）下的完整狀態空間與遊戲樹（DAG）。
   - **功能：** 計算節點矩陣 `[R0, R1, C0, C1]`，依據遊戲規則（$e, r, c$ 步）建立父子連線（Edges），並利用逆向分析（Retrograde Analysis）標記勝敗節點位置（`isWin`），最後計算每個節點的 Grundy (SG) 值，將結果輸出至 `src/data.json` 供前端視覺化。

2. **`generate_rect_p1_nodes.py`**
   - **用途：** 矩形 p1 節點生成腳本。產生以 $[n, 0, n+1, 0]$ 為起點的非對稱盤面節點群。
   - **功能：**
     - BFS 展開，e 步深度限制為 `floor((n+1)/2)`
     - 重複偵測：若子節點矩陣已存在於方形節點中，直接連邊而不新增節點
     - 逆向分析（retrograde analysis）計算每個矩形節點的 `isWin` 值
     - 以插入方形節點之間（依 R1+C1 排序）的方式決定分數型 n 座標
     - 輸出至 `src/rect_p1_data.json`

3. **`generate_rect_m1_nodes.py`**
   - **用途：** 矩形 m1 節點生成腳本。產生以 $[n+1, 0, n, 0]$ 為起點的非對稱盤面節點群（p1 的行列轉置版本）。
   - **功能：**
     - 重複偵測對象涵蓋方形節點與 p1 節點
     - 同樣計算 `isWin` 逆向分析
     - 輸出至 `src/rect_m1_data.json`

4. **`generate_coordinates.py`**
   - **用途：** 座標方案產生腳本。讀取所有節點，輸出兩套 3D 座標 JSON 供前端切換比較。
   - **功能：**
     - **Original 方案**：沿用原始 `z = n*5, y = -t*3, x = ±offset*3` 公式
     - **Unified 方案**：以矩陣值直接映射，`Z = (R0+C0)*3, X = (R0-C0)*5 + (R1-C1)*1, Y = -(R1+C1)*4`，語義明確且保證 225 個節點零碰撞
     - 輸出至 `src/coords_original.json` 與 `src/coords_unified.json`

5. **`test_schroder.py`**
   - **用途：** 理論驗證腳本。用於計算 DoubleChess 在各階層的路徑總數，並將其與 Little Schröder 數列進行比對。
   - **功能：** 透過遞迴與記憶化搜尋（Memoization），分別計算「加入自動調整規則（Adjust）」與「未加入調整規則」的總路徑數，用以證明盤面積累的數學等價性。

6. **`calculate_paths.py`**
   - **用途：** 路徑數量統計。
   - **功能：** 讀取 `src/data.json` 已經生成的遊戲樹，透過 DFS 與 Memoization 演算法，精確計算出從各個起始點 `[n,0,n,0]` 到達結束點 `[0,0,0,0]` 的路徑數，並將結果輸出。

7. **`find_recurrence.py`**
   - **用途：** 尋找線性遞迴關係。
   - **功能：** 實作 Berlekamp-Massey 演算法，針對已知的前幾項路徑數量序列，推導出該數列的生成多項式與線性遞迴式。

8. **`query_oeis.py`**
   - **用途：** OEIS 資料庫查詢。
   - **功能：** 將專案中算出的遊戲樹路徑數量序列（如 `1,3,11,45,199...`）打 API 到「整數數列線上大全 (OEIS)」，尋找是否有數學上已知的匹配數列（例如 A001003）。

9. **`check_distance.py`**、**`check_nodes.py`**、**`inspect_nodes.py`**、**`print_rects.py`**
   - **用途：** 除錯與圖形檢測工具。
   - **功能：** 檢測零距離連線、搜尋特定矩陣節點、統計矩形節點數量等驗證用途。

---

## 2. 節點類型說明

### 方形節點（Square Nodes）
- 起始矩陣：$[n, 0, n, 0]$（$n \times n$ 正方形盤面）
- ID 格式：`Lv{n}_e{t}_r{x}` 或 `Lv{n}_e{t}_c{y}`
- 資料來源：`src/data.json`
- 含完整 `isWin` 與 `grundy` 值

### 矩形 p1 節點（Rect p1 Nodes）
- 起始矩陣：$[n, 0, n+1, 0]$（列數比行數多 1）
- ID 格式：`Rect_p1_{R0}_{R1}_{C0}_{C1}`
- 資料來源：`src/rect_p1_data.json`
- 含逆向推算之 `isWin` 值；`grundy` 為 null
- 連線方向：單向，只能指向方形節點或其他矩形節點

### 矩形 m1 節點（Rect m1 Nodes）
- 起始矩陣：$[n+1, 0, n, 0]$（行數比列數多 1，p1 之轉置）
- ID 格式：`Rect_m1_{R0}_{R1}_{C0}_{C1}`
- 資料來源：`src/rect_m1_data.json`
- 含逆向推算之 `isWin` 值；重複偵測涵蓋方形節點與 p1 節點

---

## 3. 矩形節點產生方式與連線方式

### 產生方式 (Generation Strategy)
1. **初始狀態定義 (Asymmetric Initial Matrix):**
   起點矩陣為不對稱：p1 為 $R_0=n, C_0=n+1$；m1 為 $R_0=n+1, C_0=n$。

2. **自動平衡調整約束 (Matrix Adjustment Rule):**
   DoubleChess 核心定理要求：$R_1 \le C_0$ 且 $C_1 \le R_0$。
   ```python
   R1 = min(R1, C0)
   C1 = min(C1, R0)
   ```

3. **e 步深度限制：** BFS 展開時，e 步次數不超過 `floor((n+1)/2)`。

4. **重複節點處理：** 若衍生矩陣已存在於已知節點中，直接連邊而不建立新節點。

### 連線方式 (Connection Rules / Edges)
每個節點矩陣 $M = [[R_0, R_1], [C_0, C_1]]$ 依法衍生下列連線：

1. **e 步（空白格落子）：** 若 $R_0 \ge 1$ 且 $C_0 \ge 1$：
   `adjust([[R0-1, R1+1], [C0-1, C1+1]])`

2. **r 步（橫線格落子）：** 若 $R_1 \ge 1$ 且 $C_0 \ge 1$：
   `adjust([[R0, R1-1], [C0-1, C1+1]])`

3. **c 步（直線格落子）：** 若 $R_0 \ge 1$ 且 $C_1 \ge 1$：
   `adjust([[R0-1, R1+1], [C0, C1-1]])`

### 勝敗計算（Retrograde Analysis）
矩形節點的 `isWin` 透過 Kahn 拓撲排序逆向推算：
- 葉節點（所有子節點均為方形節點）直接從方形節點 `isWin` 計算
- `isWin = True` 若任一子節點 `isWin == False`（可移至對手的敗局）
- `isWin = False` 若所有子節點均 `isWin == True`，或無合法移動

---

## 4. 座標系統說明

前端支援兩套可切換的座標方案，儲存於獨立 JSON 並以節點 ID 為鍵值：

### Original 方案（`src/coords_original.json`）
沿用原始公式，以節點的 `n, t, x, y` 欄位計算：
- `Z = n * 5`
- `Y = -t * 3`
- `X = x * 3`（r 側）或 `-y * 3`（c 側）

### Unified 方案（`src/coords_unified.json`）
直接以矩陣值映射，語義明確：
- `Z = (R0 + C0) * 3`　── 剩餘棋子數（遊戲進度）
- `X = (R0 - C0) * 5 + (R1 - C1) * 1`　── 行列不對稱程度
- `Y = -(R1 + C1) * 4`　── 已落子數（換子深度）

此公式保證 225 個節點（方形 + p1 + m1）完全無碰撞。
