import { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import { Html } from '@react-three/drei';
import type { Mesh } from 'three';
import * as THREE from 'three';
import { useStore, rectReferencedSquareIds } from '../store/useStore';
import type { ChessNode } from '../types';

interface NodeMeshProps {
    node: ChessNode;
}

export const NodeMesh = ({ node }: NodeMeshProps) => {
    const meshRef = useRef<Mesh>(null);
    const {
        hoveredNode,
        setHoveredNode,
        selectedPath,
        setSelectedNode,
        activeLevel,
        showBelowLevel,
        showPathCounts,
        showGrundy,
        showRectNodes,
        showM1Nodes,
        showSquareNodes,
        noAdjMode,
        viewMode,
        getNodePosition
    } = useStore();

    const isHovered = hoveredNode === node.id;
    const isSelected = selectedPath.includes(node.id);

    // Highlighting logic:
    // If a path is selected (length > 0), only selected nodes are fully opaque.
    // Others are dimmed.
    // If activeLevel is set, hide nodes not in that level.
    // But Path Tracing takes precedence if we want to trace across levels, 
    // If activeLevel is set, hide nodes not in that level or the level exactly above it (n+1)
    // Note: Node tree grows downward, so n=0 is leaf, n=8 is root. Below means n <= activeLevel.
    // Complex visibility rules:
    // 1. By default, show activeLevel (n) and activeLevel - 1 (n-1)
    // 2. If activeLevel is even, ALSO show activeLevel - 2 (n-2) BUT ONLY where t is maximum (t == (n-2)/2)
    // 3. If showBelowLevel is true, show everything below activeLevel
    const isP1 = node.nodeType === 'rect_p1' || node.nodeType === 'noadj_p1';
    const isM1 = node.nodeType === 'rect_m1' || node.nodeType === 'noadj_m1';
    const isRect = isP1 || isM1;
    const isHiddenByRect = (isP1 && !showRectNodes) || (isM1 && !showM1Nodes);
    // Hide square nodes when showSquareNodes is off, unless they are endpoints of rect edges
    const isHiddenBySquare = !isRect && !showSquareNodes && !rectReferencedSquareIds.has(node.id);
    let isHiddenByLevel = false;

    if (activeLevel !== null) {
        if (showBelowLevel) {
            isHiddenByLevel = node.n > activeLevel;
        } else {
            // For fractional n (rect nodes), visible when activeLevel matches floor or ceil
            const nodeFloor = Math.floor(node.n);
            const nodeCeil = Math.ceil(node.n);
            const isN = nodeFloor === activeLevel || nodeCeil === activeLevel;
            const isNMinus1 = nodeFloor === activeLevel - 1 || nodeCeil === activeLevel - 1;

            let isNMinus2MaxT = false;
            if (activeLevel % 2 === 0) {
                const targetN = activeLevel - 2;
                const maxT = Math.floor(targetN / 2);
                isNMinus2MaxT = ((nodeFloor === targetN || nodeCeil === targetN) && node.t === maxT);
            }

            isHiddenByLevel = !(isN || isNMinus1 || isNMinus2MaxT);
        }
    }
    const isDimmed = selectedPath.length > 0 && !isSelected;

    const [x_pos, y_pos, z_pos] = getNodePosition(node.id);

    // Identify ending point: [0,0,0,0] normally; in noAdj mode, any terminal node (no moves)
    const isEndNode = noAdjMode
        ? node.nextNodes.length === 0
        : node.matrix[0] === 0 && node.matrix[1] === 0 && node.matrix[2] === 0 && node.matrix[3] === 0;

    // Identify starting points: R1=0 and C1=0 (excluding the end node)
    // For original nodes, this is [[n,0],[n,0]], for rectangular nodes this is [[n,0],[n+1,0]] or vice-versa
    const isStartNode = !isEndNode && node.matrix[1] === 0 && node.matrix[3] === 0;

    // Colors — square=emerald/red; rect (p1 & m1) both use cyan/amber
    const winColor = new THREE.Color(isRect ? '#67e8f9' : '#10b981');
    const loseColor = new THREE.Color(isRect ? '#fcd34d' : '#ef4444');
    const defaultColor = new THREE.Color('#94a3b8'); // Slate 400
    const startColor = new THREE.Color('#ffffff'); // White
    const endColor = new THREE.Color('#eab308'); // Yellow 500

    // Pre-calculated path counts from [n,0,n,0] to [0,0,0,0]
    const pathCounts: Record<number, number> = {
        1: 1, 2: 3, 3: 11, 4: 45, 5: 199, 6: 929, 7: 4505, 8: 22459
    };

    const baseColor = isStartNode ? startColor :
        isEndNode ? endColor :
            node.isWin === true ? winColor :
                node.isWin === false ? loseColor : defaultColor;

    const emissiveColor = isStartNode ? startColor : isEndNode ? endColor : node.isWin === true ? winColor : new THREE.Color('#000000');
    const emissiveIntensity = isStartNode ? 0.8 : isEndNode ? 0.8 : node.isWin === true ? 0.5 : 0;

    const getPositionString = () => {
        const x_str = node.x > 0 ? `r${node.x}` : node.y > 0 ? `c${node.y}` : `r0`;
        return `Lv${node.n}e${node.t}${x_str}`;
    };

    let cardBg = 'bg-slate-800/90 border-slate-600 text-slate-200';
    if (isEndNode) cardBg = 'bg-yellow-900/90 border-yellow-500 text-yellow-50';
    else if (isStartNode) cardBg = isRect ? 'bg-slate-300/90 border-slate-400 text-slate-900' : 'bg-slate-200/90 border-white text-slate-900';
    else if (node.isWin === true) {
        if (isRect) cardBg = 'bg-cyan-800/70 border-cyan-400 text-cyan-50';
        else cardBg = 'bg-emerald-900/90 border-emerald-500 text-emerald-50';
    } else if (node.isWin === false) {
        if (isRect) cardBg = 'bg-amber-800/70 border-amber-400 text-amber-50';
        else cardBg = 'bg-red-900/90 border-red-500 text-red-50';
    }

    // Hover effect: scale up slightly
    useFrame(() => {
        if (meshRef.current) {
            const targetScale = isHovered ? 1.5 : 1;
            meshRef.current.scale.lerp(new THREE.Vector3(targetScale, targetScale, targetScale), 0.1);
        }
    });

    return (
        <group visible={!isHiddenByLevel && !isHiddenByRect && !isHiddenBySquare && !isHiddenBySquare} position={[x_pos, y_pos, z_pos]}>
            <mesh
                ref={meshRef}
                onPointerOver={(e) => {
                    e.stopPropagation();
                    setHoveredNode(node.id);
                    document.body.style.cursor = 'pointer';
                }}
                onPointerOut={() => {
                    setHoveredNode(null);
                    document.body.style.cursor = 'auto';
                }}
                onClick={(e) => {
                    e.stopPropagation();
                    setSelectedNode(isSelected ? null : node.id); // Toggle selection
                }}
            >
                <sphereGeometry args={[viewMode === 'card' ? 0.8 : 0.4, 32, 32]} />
                <meshStandardMaterial
                    color={baseColor}
                    emissive={emissiveColor}
                    emissiveIntensity={emissiveIntensity}
                    transparent={true}
                    opacity={viewMode === 'card' ? 0 : (isDimmed ? 0.1 : 1)}
                    depthWrite={viewMode !== 'card'}
                    roughness={0.2}
                    metalness={0.1}
                />
            </mesh>

            {!isHiddenByLevel && !isHiddenByRect && !isHiddenBySquare && viewMode === 'card' && (
                <Html transform center style={{ pointerEvents: 'none' }} scale={isRect ? 0.45 : 0.65}>
                    <div className={`px-2 py-1.5 rounded-md border shadow-2xl backdrop-blur-md text-center flex flex-col items-center justify-center transition-all ${cardBg} ${isDimmed ? 'opacity-20 flex' : 'opacity-100'}`}>
                        <div className="font-mono text-sm font-bold tracking-widest whitespace-nowrap">
                            [{node.matrix[0]}, {node.matrix[1]}]<br />
                            [{node.matrix[2]}, {node.matrix[3]}]
                        </div>
                        <div className={`text-[10px] mt-1 pt-0.5 border-t w-full font-sans tracking-wider ${isStartNode ? 'border-slate-400' : 'border-white/20'}`}>
                            {getPositionString()}
                        </div>
                    </div>
                </Html>
            )}

            {!isHiddenByLevel && !isHiddenByRect && !isHiddenBySquare && isHovered && viewMode === 'sphere' && (
                <Html distanceFactor={15} center style={{ pointerEvents: 'none' }}>
                    <div className="bg-slate-900/90 text-white p-3 rounded-lg shadow-xl border border-slate-700 w-48 backdrop-blur-sm z-50">
                        <h3 className="font-bold border-b border-slate-700 pb-1 mb-2 text-sm">{node.id}</h3>
                        <div className="grid grid-cols-2 gap-1 text-xs text-slate-300">
                            <div>Level (n): <span className="text-white font-mono">{node.n}</span></div>
                            <div>Turn (t): <span className="text-white font-mono">{node.t}</span></div>
                            <div>X axis (x): <span className="text-white font-mono">{node.x}</span></div>
                            <div>Y axis (y): <span className="text-white font-mono">{node.y}</span></div>
                        </div>
                        <div className="mt-2 pt-2 border-t border-slate-700">
                            <span className="text-xs text-slate-400">Matrix:</span>
                            <div className="font-mono text-sm tracking-widest mt-1 bg-slate-800 p-1 rounded text-center">
                                [{node.matrix[0]}, {node.matrix[1]}]<br />
                                [{node.matrix[2]}, {node.matrix[3]}]
                            </div>
                        </div>
                        <div className="mt-2 pt-2 border-t border-slate-700 flex justify-between items-center">
                            <span className="text-xs text-slate-400">Status:</span>
                            <span className={`text-xs font-bold px-2 py-0.5 rounded ${isStartNode ? 'bg-white/20 text-white' : node.isWin === true ? 'bg-emerald-500/20 text-emerald-400' : node.isWin === false ? 'bg-red-500/20 text-red-400' : 'bg-slate-500/20 text-slate-400'}`}>
                                {isEndNode ? 'END' : isStartNode ? 'START' : node.isWin === true ? 'WIN' : node.isWin === false ? 'LOSE' : 'UNKNOWN'}
                            </span>
                        </div>
                    </div>
                </Html>
            )}

            {!isHiddenByLevel && !isHiddenByRect && !isHiddenBySquare && showPathCounts && isStartNode && node.n > 0 && pathCounts[node.n] && (
                <Html transform center position={[0, viewMode === 'card' ? 1.5 : 1, 0]} scale={0.7} style={{ pointerEvents: 'none' }}>
                    <div className={`px-2 py-1 bg-amber-500/90 text-amber-50 rounded-lg shadow-lg border border-amber-400 font-bold whitespace-nowrap transition-all ${isDimmed ? 'opacity-20' : 'opacity-100'}`}>
                        {pathCounts[node.n].toLocaleString()} Paths
                    </div>
                </Html>
            )}

            {!isHiddenByLevel && !isHiddenByRect && !isHiddenBySquare && showGrundy && node.grundy !== undefined && (
                <Html transform center position={[viewMode === 'card' ? 1.4 : 1.2, viewMode === 'card' ? 0.8 : 0.8, 0]} scale={0.65} style={{ pointerEvents: 'none' }}>
                    <div className={`px-2 py-0.5 bg-blue-600/90 text-blue-50 rounded-full shadow border border-blue-400 font-mono text-xs font-bold whitespace-nowrap transition-all ${isDimmed ? 'opacity-20' : 'opacity-100'}`}>
                        G: {node.grundy}
                    </div>
                </Html>
            )}
        </group>
    );
};
