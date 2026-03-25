export interface ChessNode {
    id: string;          // e.g. "Lv6_e3_r2" or "Rect_p1_5_0_5_2"
    n: number;           // Z axis height (can be fractional for rect nodes)
    t: number;
    x: number;           // X axis
    y: number;           // Y axis
    isWin: boolean | null;
    matrix: [number, number, number, number]; // [R0, R1, C0, C1]
    nextNodes: string[]; // for drawing Edges
    grundy: number | null; // DP/Grundy SG value
    nodeType?: 'square' | 'rect_p1' | 'rect_m1' | 'rect_m2' | 'rect_m3' | 'rect_m4' | 'noadj_square' | 'noadj_p1' | 'noadj_m1';
}
