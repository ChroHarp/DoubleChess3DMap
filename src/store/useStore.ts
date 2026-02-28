import { create } from 'zustand';
import type { ChessNode } from '../types';
import rawData from '../data.json';

const nodesData = rawData as ChessNode[];

interface DefaultState {
    nodes: ChessNode[];
    activeLevel: number | null;
    showBelowLevel: boolean;
    showPathCounts: boolean;
    viewMode: 'sphere' | 'card';
    hoveredNode: string | null;
    selectedPath: string[]; // List of node IDs in the selected path
    maxLevel: number;
    cameraResetSignal: number;
}

interface ActionState {
    setActiveLevel: (level: number | null) => void;
    setShowBelowLevel: (show: boolean) => void;
    setShowPathCounts: (show: boolean) => void;
    setViewMode: (mode: 'sphere' | 'card') => void;
    setHoveredNode: (nodeId: string | null) => void;
    setSelectedNode: (nodeId: string | null) => void;
    triggerCameraReset: () => void;
}

export const useStore = create<DefaultState & ActionState>((set, get) => ({
    nodes: nodesData,
    activeLevel: Math.max(...nodesData.map((n) => n.n)),
    showBelowLevel: false,
    showPathCounts: true,
    viewMode: 'card',
    hoveredNode: null,
    selectedPath: [],
    maxLevel: Math.max(...nodesData.map((n) => n.n)),
    cameraResetSignal: 0,

    setActiveLevel: (level) => set({ activeLevel: level }),
    setShowBelowLevel: (show) => set({ showBelowLevel: show }),
    setShowPathCounts: (show) => set({ showPathCounts: show }),
    setViewMode: (mode) => set({ viewMode: mode }),
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
