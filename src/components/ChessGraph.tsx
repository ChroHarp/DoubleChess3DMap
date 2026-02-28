import { useRef, useEffect } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import { useStore } from '../store/useStore';
import type { OrbitControls as OrbitControlsImpl } from 'three-stdlib';
import { NodeMesh } from './NodeMesh';
import { EdgeLine } from './EdgeLine';

export const ChessGraph = () => {
    const { nodes, cameraResetSignal } = useStore();
    const controlsRef = useRef<OrbitControlsImpl>(null);

    useEffect(() => {
        if (cameraResetSignal > 0 && controlsRef.current) {
            controlsRef.current.reset();
        }
    }, [cameraResetSignal]);

    return (
        <div className="w-full h-screen bg-slate-900 absolute inset-0 z-0">
            <Canvas camera={{ position: [0, -10, 60], fov: 60 }}>
                <color attach="background" args={['#0f172a']} />

                {/* Lights */}
                <ambientLight intensity={0.5} />
                <directionalLight position={[10, 20, 10]} intensity={1} />
                <pointLight position={[-10, 10, -10]} intensity={0.5} />

                {/* Controls */}
                <OrbitControls ref={controlsRef} makeDefault />

                {/* 
          Render Edges first so they are behind Nodes 
          Iterate nodes to find nextNodes and draw lines
        */}
                <group>
                    {nodes.map(node => (
                        node.nextNodes.map(childId => {
                            const childNode = nodes.find(n => n.id === childId);
                            if (!childNode) return null;

                            return (
                                <EdgeLine
                                    key={`${node.id}-${childId}`}
                                    startNode={node}
                                    endNode={childNode}
                                />
                            );
                        })
                    ))}
                </group>

                {/* Render Nodes */}
                <group>
                    {nodes.map(node => (
                        <NodeMesh key={node.id} node={node} />
                    ))}
                </group>
            </Canvas>
        </div>
    );
};
