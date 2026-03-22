import { Line } from '@react-three/drei';
import { useStore, rectReferencedSquareIds } from '../store/useStore';
import type { ChessNode } from '../types';
import * as THREE from 'three';

interface EdgeLineProps {
    startNode: ChessNode;
    endNode: ChessNode;
}

export const EdgeLine = ({ startNode, endNode }: EdgeLineProps) => {
    const { selectedPath, activeLevel, showBelowLevel, showRectNodes, showM1Nodes, showSquareNodes, getNodePosition } = useStore();

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

    const isHiddenByLevel = activeLevel !== null;

    // If path is selected, show only edges between selected nodes
    const isSelectedEdge = selectedPath.includes(startNode.id) && selectedPath.includes(endNode.id);
    const isDimmed = selectedPath.length > 0 && !isSelectedEdge;

    // Complex visibility rules (must match NodeMesh, supports fractional n)
    if (isHiddenByLevel && activeLevel !== null) {
        const checkHidden = (n: number, t: number) => {
            const nFloor = Math.floor(n);
            const nCeil = Math.ceil(n);
            if (showBelowLevel) {
                return n > activeLevel;
            }
            const isN = nFloor === activeLevel || nCeil === activeLevel;
            const isNMinus1 = nFloor === activeLevel - 1 || nCeil === activeLevel - 1;
            let isNMinus2MaxT = false;
            if (activeLevel % 2 === 0) {
                const targetN = activeLevel - 2;
                const maxT = Math.floor(targetN / 2);
                isNMinus2MaxT = ((nFloor === targetN || nCeil === targetN) && t === maxT);
            }
            return !(isN || isNMinus1 || isNMinus2MaxT);
        };

        if (checkHidden(startNode.n, startNode.t) || checkHidden(endNode.n, endNode.t)) return null;
    }

    const isLevelDrop = startNode.n !== endNode.n;

    // Highlight Level drop: yellow (#f59e0b) width 2
    // Normal line: slate (#cbd5e1) transparent 0.3 width 1
    const highlightColor = new THREE.Color('#f59e0b');
    const normalColor = new THREE.Color('#cbd5e1');

    const color = isLevelDrop ? highlightColor : normalColor;
    const lineWidth = isLevelDrop ? 2 : 1;
    const opacity = isDimmed ? 0.05 : (isLevelDrop ? 0.8 : 0.3);

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
