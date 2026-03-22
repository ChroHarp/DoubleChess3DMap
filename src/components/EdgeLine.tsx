import { Line } from '@react-three/drei';
import { useStore, rectReferencedSquareIds } from '../store/useStore';
import type { ChessNode } from '../types';
import * as THREE from 'three';

interface EdgeLineProps {
    startNode: ChessNode;
    endNode: ChessNode;
}

export const EdgeLine = ({ startNode, endNode }: EdgeLineProps) => {
    const { selectedPath, activeTier, showBelowLevel, showRectNodes, showM1Nodes, showSquareNodes, getNodePosition } = useStore();

    const startIsP1 = startNode.nodeType === 'rect_p1';
    const endIsP1 = endNode.nodeType === 'rect_p1';
    const startIsM1 = startNode.nodeType === 'rect_m1';
    const endIsM1 = endNode.nodeType === 'rect_m1';

    // Hide edges involving hidden rect nodes
    if (!showRectNodes && (startIsP1 || endIsP1)) return null;
    if (!showM1Nodes && (startIsM1 || endIsM1)) return null;

    // Hide edges where a square endpoint is hidden (not a rect-referenced endpoint)
    const startIsRect = startIsP1 || startIsM1;
    const endIsRect = endIsP1 || endIsM1;
    const startSquareHidden = !startIsRect && !showSquareNodes && !rectReferencedSquareIds.has(startNode.id);
    const endSquareHidden = !endIsRect && !showSquareNodes && !rectReferencedSquareIds.has(endNode.id);
    if (startSquareHidden || endSquareHidden) return null;

    // If path is selected, show only edges between selected nodes
    const isSelectedEdge = selectedPath.includes(startNode.id) && selectedPath.includes(endNode.id);
    const isDimmed = selectedPath.length > 0 && !isSelectedEdge;

    // Tier-based visibility (matches NodeMesh logic)
    if (activeTier !== null) {
        const checkHidden = (node: ChessNode) => {
            if (showBelowLevel) {
                return node.tier > activeTier;
            }
            const isCurrentTier = node.tier === activeTier;
            const isPrevTier = node.tier === activeTier - 1;
            let isTwoBelow = false;
            if (activeTier % 2 === 0) {
                const targetTier = activeTier - 2;
                const maxT = Math.floor(targetTier / 2);
                isTwoBelow = node.tier === targetTier && node.t === maxT;
            }
            return !(isCurrentTier || isPrevTier || isTwoBelow);
        };

        if (checkHidden(startNode) || checkHidden(endNode)) return null;
    }

    // Highlight tier-crossing edges
    const isTierDrop = startNode.tier !== endNode.tier;

    const highlightColor = new THREE.Color('#f59e0b');
    const normalColor = new THREE.Color('#cbd5e1');

    const color = isTierDrop ? highlightColor : normalColor;
    const lineWidth = isTierDrop ? 2 : 1;
    const opacity = isDimmed ? 0.05 : (isTierDrop ? 0.8 : 0.3);

    const [startX, startY, startZ] = getNodePosition(startNode.id);
    const [endX, endY, endZ] = getNodePosition(endNode.id);

    const startVec = new THREE.Vector3(startX, startY, startZ);
    const endVec = new THREE.Vector3(endX, endY, endZ);

    const dir = new THREE.Vector3().subVectors(endVec, startVec);
    const length = startVec.distanceTo(endVec);

    if (length < 0.001) {
        return null; // Avoid NaN crash when placing an edge between identical coordinates
    }
    dir.normalize();

    // position arrow near the end, but before the 0.4 radius sphere
    const arrowPos = startVec.clone().add(dir.clone().multiplyScalar(Math.max(0, length - 0.6)));

    // Create quaternion to rotate the default ConeGeometry (which points up +Y) to match `dir`
    const quaternion = new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 1, 0), dir);

    return (
        <group>
            <Line
                points={[startVec, endVec]}
                color={color}
                lineWidth={lineWidth}
                transparent={true}
                opacity={opacity}
            />
            <mesh position={arrowPos} quaternion={quaternion}>
                <coneGeometry args={[0.2, 0.6, 8]} />
                <meshBasicMaterial color={color} transparent={true} opacity={opacity} />
            </mesh>
        </group>
    );
};
