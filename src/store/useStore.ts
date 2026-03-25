import { create } from 'zustand';
import type { ChessNode } from '../types';
import rawData from '../data.json';
import rawRectP1Data from '../rect_p1_data.json';
import rawRectM1Data from '../rect_m1_data.json';
import rawNoAdjData from '../noadj_data.json';
import rawNoAdjP1Data from '../noadj_rect_p1_data.json';
import rawNoAdjM1Data from '../noadj_rect_m1_data.json';
import coordsOriginal from '../coords_original.json';
import coordsUnified from '../coords_unified.json';
import coordsTopological from '../coords_topological.json';

const squareNodes = rawData as ChessNode[];
const rectP1Nodes = rawRectP1Data as ChessNode[];
const rectM1Nodes = rawRectM1Data as ChessNode[];
const nodesData = [...squareNodes, ...rectP1Nodes, ...rectM1Nodes];

const noAdjSquareNodes = (rawNoAdjData as ChessNode[]).map(n => ({ ...n, nodeType: 'noadj_square' as const }));
const noAdjP1Nodes = (rawNoAdjP1Data as ChessNode[]).map(n => ({ ...n, nodeType: 'noadj_p1' as const }));
const noAdjM1Nodes = (rawNoAdjM1Data as ChessNode[]).map(n => ({ ...n, nodeType: 'noadj_m1' as const }));
const noAdjNodesData = [...noAdjSquareNodes, ...noAdjP1Nodes, ...noAdjM1Nodes];

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
    activeTier: number | null;
    showBelowLevel: boolean;
    showPathCounts: boolean;
    showGrundy: boolean;
    showRectNodes: boolean;
    showM1Nodes: boolean;
    showSquareNodes: boolean;
    noAdjMode: boolean;
    viewMode: 'sphere' | 'card';
    coordMode: string;
    hoveredNode: string | null;
    selectedPath: string[]; // List of node IDs in the selected path
    maxTier: number;
    cameraResetSignal: number;
    getNodePosition: (nodeId: string) => [number, number, number];
}

interface ActionState {
    setActiveTier: (tier: number | null) => void;
    setShowBelowLevel: (show: boolean) => void;
    setShowPathCounts: (show: boolean) => void;
    setShowGrundy: (show: boolean) => void;
    setShowRectNodes: (show: boolean) => void;
    setShowM1Nodes: (show: boolean) => void;
    setShowSquareNodes: (show: boolean) => void;
    setNoAdjMode: (mode: boolean) => void;
    setViewMode: (mode: 'sphere' | 'card') => void;
    setCoordMode: (mode: string) => void;
    setHoveredNode: (nodeId: string | null) => void;
    setSelectedNode: (nodeId: string | null) => void;
    triggerCameraReset: () => void;
}

export const useStore = create<DefaultState & ActionState>((set, get) => ({
    nodes: nodesData,
    activeTier: Math.max(...nodesData.map((n) => n.tier)),
    showBelowLevel: false,
    showPathCounts: true,
    showGrundy: true,
    showRectNodes: true,
    showM1Nodes: true,
    showSquareNodes: true,
    noAdjMode: false,
    viewMode: 'card',
    coordMode: 'original',
    hoveredNode: null,
    selectedPath: [],
    maxTier: Math.max(...nodesData.map((n) => n.tier)),
    cameraResetSignal: 0,
    getNodePosition: (nodeId: string) => {
        const mode = get().coordMode;
        const coords = coordSets[mode] || coordSets.original;
        return coords[nodeId] || [0, 0, 0];
    },

    setActiveTier: (tier) => set({ activeTier: tier }),
    setShowBelowLevel: (show) => set({ showBelowLevel: show }),
    setShowPathCounts: (show) => set({ showPathCounts: show }),
    setShowGrundy: (show) => set({ showGrundy: show }),
    setShowRectNodes: (show) => set({ showRectNodes: show }),
    setShowM1Nodes: (show) => set({ showM1Nodes: show }),
    setShowSquareNodes: (show) => set({ showSquareNodes: show }),
    setNoAdjMode: (mode) => set((state) => {
        const nextNodes = mode ? noAdjNodesData : nodesData;
        const newMaxLevel = Math.ceil(Math.max(...nextNodes.map((n) => n.n)));
        return {
            noAdjMode: mode,
            nodes: nextNodes,
            maxLevel: newMaxLevel,
            activeLevel: newMaxLevel,
            selectedPath: [],
        };
    }),
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
