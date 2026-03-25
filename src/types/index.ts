export interface ChessNode {
    id: string;          // e.g. "4x4_1_1" or "1x2_0_0"
    legacyId: string | null; // e.g. "Lv6_e3_r2" or "Rect_p1_5_0_5_2"
    tier: number;        // R0 + C0 (integer, strict topological ordering)
    n: number;           // Legacy level (can be fractional for rect nodes)
    t: number;
    x: number;           // X axis
    y: number;           // Y axis
    isWin: boolean | null;
    matrix: [number, number, number, number]; // [R0, R1, C0, C1]
    nextNodes: string[]; // for drawing Edges
    grundy: number | null; // DP/Grundy SG value
    nodeType?: 'square' | 'rect_p1' | 'rect_m1' | 'noadj_square' | 'noadj_p1' | 'noadj_m1';
}
