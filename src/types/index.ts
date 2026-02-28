export interface ChessNode {
    id: string;          // e.g. "Lv6_e3_r2"
    n: number;           // Z axis height
    t: number;
    x: number;           // X axis
    y: number;           // Y axis
    isWin: boolean | null;
    matrix: [number, number, number, number]; // [R0, R1, C0, C1]
    nextNodes: string[]; // for drawing Edges
    grundy: number;      // DP/Grundy SG value
}
