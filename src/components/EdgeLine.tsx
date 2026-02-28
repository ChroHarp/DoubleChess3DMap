import { Line } from '@react-three/drei';
import { useStore } from '../store/useStore';
import type { ChessNode } from '../types';
import * as THREE from 'three';

interface EdgeLineProps {
    startNode: ChessNode;
    endNode: ChessNode;
}

export const EdgeLine = ({ startNode, endNode }: EdgeLineProps) => {
    const { selectedPath, activeLevel, showBelowLevel } = useStore();

    const isHiddenByLevel = activeLevel !== null;

    // If path is selected, show only edges between selected nodes
    const isSelectedEdge = selectedPath.includes(startNode.id) && selectedPath.includes(endNode.id);
    const isDimmed = selectedPath.length > 0 && !isSelectedEdge;

    // Complex visibility rules (must match NodeMesh)
    if (isHiddenByLevel && activeLevel !== null) {
        let isStartHidden = false;
        let isEndHidden = false;

        if (showBelowLevel) {
            isStartHidden = startNode.n > activeLevel;
            isEndHidden = endNode.n > activeLevel;
        } else {
            const isStartN = startNode.n === activeLevel;
            const isStartNMinus1 = startNode.n === activeLevel - 1;
            let isStartNMinus2MaxT = false;

            const isEndN = endNode.n === activeLevel;
            const isEndNMinus1 = endNode.n === activeLevel - 1;
            let isEndNMinus2MaxT = false;

            if (activeLevel % 2 === 0) {
                const targetN = activeLevel - 2;
                const maxT = Math.floor(targetN / 2);
                isStartNMinus2MaxT = (startNode.n === targetN && startNode.t === maxT);
                isEndNMinus2MaxT = (endNode.n === targetN && endNode.t === maxT);
            }

            isStartHidden = !(isStartN || isStartNMinus1 || isStartNMinus2MaxT);
            isEndHidden = !(isEndN || isEndNMinus1 || isEndNMinus2MaxT);
        }

        // Hide edge if either the starting node or ending node is hidden
        if (isStartHidden || isEndHidden) return null;
    }

    const isLevelDrop = startNode.n !== endNode.n;

    // Highlight Level drop: yellow (#f59e0b) width 2
    // Normal line: slate (#cbd5e1) transparent 0.3 width 1
    const highlightColor = new THREE.Color('#f59e0b');
    const normalColor = new THREE.Color('#cbd5e1');

    const color = isLevelDrop ? highlightColor : normalColor;
    const lineWidth = isLevelDrop ? 2 : 1;
    const opacity = isDimmed ? 0.05 : (isLevelDrop ? 0.8 : 0.3);

    // Coordinate mapping identical to NodeMesh
    const startX = (startNode.x > 0 ? startNode.x : -startNode.y) * 3;
    const startY = startNode.t * -3;
    const startZ = startNode.n * 5;

    const endX = (endNode.x > 0 ? endNode.x : -endNode.y) * 3;
    const endY = endNode.t * -3;
    const endZ = endNode.n * 5;

    const startVec = new THREE.Vector3(startX, startY, startZ);
    const endVec = new THREE.Vector3(endX, endY, endZ);

    const dir = new THREE.Vector3().subVectors(endVec, startVec).normalize();
    const length = startVec.distanceTo(endVec);
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
