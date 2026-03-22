import { create } from 'zustand';
import type { ChessNode } from '../types';
import rawData from '../data.json';
import rawRectP1Data from '../rect_p1_data.json';
import rawRectM1Data from '../rect_m1_data.json';
import coordsOriginal from '../coords_original.json';
import coordsUnified from '../coords_unified.json';
import coordsTopological from '../coords_topological.json';

const squareNodes = (rawData as ChessNode[]).map(n => ({ ...n, nodeType: 'square' as const }));
const rectP1Nodes = rawRectP1Data as ChessNode[];
const rectM1Nodes = rawRectM1Data as ChessNode[];
const nodesData = [...squareNodes, ...rectP1Nodes, ...rectM1Nodes];

// Pre-compute: square node IDs that are referenced by any rect nextNodes
export const rectReferencedSquareIds = new Set<string>(
    [...rectP1Nodes, ...rectM1Nodes].flatMap(n => n.nextNodes)
);

const coordSets: Record<string, Record<string, [number, number, number]>> = {
    original: coordsOriginal as unknown as Record<string, [number, number, number]>,
    unified: coordsUnified as unknown as Record<string, [number, number, number]>,
    topological: coordsTopological as unknown as Record<string, [number, number, number]>,
};

interface DefaultState {
    nodes: ChessNode[];
    activeLevel: number | null;
    showBelowLevel: boolean;
    showPathCounts: boolean;
    showGrundy: boolean;
    showRectNodes: boolean;
    showM1Nodes: boolean;
    showSquareNodes: boolean;
    viewMode: 'sphere' | 'card';
    coordMode: string;
    hoveredNode: string | null;
    selectedPath: string[]; // List of node IDs in the selected path
    maxLevel: number;
    cameraResetSignal: number;
    getNodePosition: (nodeId: string) => [number, number, number];
}

interface ActionState {
    setActiveLevel: (level: number | null) => void;
    setShowBelowLevel: (show: boolean) => void;
    setShowPathCounts: (show: boolean) => void;
    setShowGrundy: (show: boolean) => void;
    setShowRectNodes: (show: boolean) => void;
    setShowM1Nodes: (show: boolean) => void;
    setShowSquareNodes: (show: boolean) => void;
    setViewMode: (mode: 'sphere' | 'card') => void;
    setCoordMode: (mode: string) => void;
    setHoveredNode: (nodeId: string | null) => void;
    setSelectedNode: (nodeId: string | null) => void;
    triggerCameraReset: () => void;
}

export const useStore = create<DefaultState & ActionState>((set, get) => ({
    nodes: nodesData,
    activeLevel: Math.ceil(Math.max(...nodesData.map((n) => n.n))),
    showBelowLevel: false,
    showPathCounts: true,
    showGrundy: true,
    showRectNodes: true,
    showM1Nodes: true,
    showSquareNodes: true,
    viewMode: 'card',
    coordMode: 'original',
    hoveredNode: null,
    selectedPath: [],
    maxLevel: Math.ceil(Math.max(...nodesData.map((n) => n.n))),
    cameraResetSignal: 0,
    getNodePosition: (nodeId: string) => {
        const mode = get().coordMode;
        const coords = coordSets[mode] || coordSets.original;
        return coords[nodeId] || [0, 0, 0];
    },

    setActiveLevel: (level) => set({ activeLevel: level }),
    setShowBelowLevel: (show) => set({ showBelowLevel: show }),
    setShowPathCounts: (show) => set({ showPathCounts: show }),
    setShowGrundy: (show) => set({ showGrundy: show }),
    setShowRectNodes: (show) => set({ showRectNodes: show }),
    setShowM1Nodes: (show) => set({ showM1Nodes: show }),
    setShowSquareNodes: (show) => set({ showSquareNodes: show }),
    setViewMode: (mode) => set({ viewMode: mode }),
    setCoordMode: (mode) => set({ coordMode: mode }),
    setHoveredNode: (nodeId) => set({ hoveredNode: nodeId }),
    triggerCameraReset: () => set((state) => ({ cameraResetSignal: state.cameraResetSignal + 1 })),

    setSelectedNode: (nodeId) => {
        if (!nodeId) {
            set({ selectedPath: [] });
            return;
        }

        const { nodes } = get();
        const path = new Set<string>([nodeId]);

        // 1. Build parent map for upward traversal
        const parentMap: Record<string, string[]> = {};
        nodes.forEach(node => {
            node.nextNodes.forEach(childId => {
                if (!parentMap[childId]) parentMap[childId] = [];
                parentMap[childId].push(node.id);
            });
        });

        // 2. Traversal DOWN (Find all Descendants)
        const queueDown = [nodeId];
        while (queueDown.length > 0) {
            const currentId = queueDown.shift()!;
            const node = nodes.find(n => n.id === currentId);
            if (node) {
                node.nextNodes.forEach(childId => {
                    if (!path.has(childId)) {
                        path.add(childId);
                        queueDown.push(childId);
                    }
                });
            }
        }

        // 3. Traversal UP (Find all Ancestors)
        const queueUp = [nodeId];
        while (queueUp.length > 0) {
            const currentId = queueUp.shift()!;
            const parents = parentMap[currentId] || [];
            parents.forEach(parentId => {
                if (!path.has(parentId)) {
                    path.add(parentId);
                    queueUp.push(parentId);
                }
            });
        }

        set({ selectedPath: Array.from(path) });
    }
}));
