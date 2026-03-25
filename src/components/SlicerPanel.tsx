import { useStore } from '../store/useStore';
import { Layers, Box, CreditCard, Axis3D } from 'lucide-react';

export const SlicerPanel = () => {
    const { activeLevel, maxLevel, setActiveLevel, showBelowLevel, setShowBelowLevel, showPathCounts, setShowPathCounts, showGrundy, setShowGrundy, showRectNodes, setShowRectNodes, showM1Nodes, setShowM1Nodes, showM2Nodes, setShowM2Nodes, showM3Nodes, setShowM3Nodes, showM4Nodes, setShowM4Nodes, showSquareNodes, setShowSquareNodes, noAdjMode, setNoAdjMode, viewMode, setViewMode, coordMode, setCoordMode } = useStore();

    return (
        <div className="absolute top-4 right-4 bg-slate-800/90 text-slate-200 p-4 rounded-xl border border-slate-700 shadow-2xl backdrop-blur-md w-72 z-10 transition-all">
            <div className="flex items-center justify-between mb-4 border-b border-slate-700 pb-3">
                <div className="flex items-center gap-2">
                    <Layers className="w-5 h-5 text-emerald-400" />
                    <h2 className="font-semibold text-lg">Level Slicer</h2>
                </div>
                <div className="flex bg-slate-900 rounded-lg p-1 border border-slate-700 gap-0.5">
                    <button
                        onClick={() => setViewMode('sphere')}
                        className={`p-1.5 rounded-md transition-all ${viewMode === 'sphere' ? 'bg-slate-700 text-emerald-400' : 'text-slate-500 hover:text-slate-300'}`}
                        title="Sphere View"
                    >
                        <Box className="w-4 h-4" />
                    </button>
                    <button
                        onClick={() => setViewMode('card')}
                        className={`p-1.5 rounded-md transition-all ${viewMode === 'card' ? 'bg-slate-700 text-emerald-400' : 'text-slate-500 hover:text-slate-300'}`}
                        title="Card View"
                    >
                        <CreditCard className="w-4 h-4" />
                    </button>
                </div>
            </div>

            <div className="flex items-center gap-2 mb-3 pb-3 border-b border-slate-700/50">
                <Axis3D className="w-4 h-4 text-sky-400" />
                <span className="text-sm text-slate-400">Coords:</span>
                <div className="flex bg-slate-900 rounded-lg p-1 border border-slate-700 flex-1">
                    <button
                        onClick={() => setCoordMode('original')}
                        className={`flex-1 px-2 py-1 rounded-md text-xs font-mono transition-all ${coordMode === 'original' ? 'bg-slate-700 text-sky-400' : 'text-slate-500 hover:text-slate-300'}`}
                    >
                        Original
                    </button>
                    <button
                        onClick={() => setCoordMode('unified')}
                        className={`flex-1 px-2 py-1 rounded-md text-xs font-mono transition-all ${coordMode === 'unified' ? 'bg-slate-700 text-sky-400' : 'text-slate-500 hover:text-slate-300'}`}
                    >
                        Unified
                    </button>
                    <button
                        onClick={() => setCoordMode('topological')}
                        className={`flex-1 flex items-center justify-center px-2 py-1 rounded-md text-xs font-mono transition-all ${coordMode === 'topological' ? 'bg-slate-700 text-sky-400 font-bold' : 'text-slate-500 hover:text-slate-300'}`}
                    >
                        Topological
                    </button>
                </div>
            </div>

            <div className="space-y-4">
                <div className="flex justify-between items-center mb-1">
                    <span className="text-sm text-slate-400">Current View</span>
                    <span className="bg-slate-900 px-2 py-1 rounded text-xs font-mono font-bold text-emerald-400 border border-slate-700">
                        {activeLevel === null ? 'All Levels' : `Lv ${activeLevel}${activeLevel < maxLevel ? ` & ${activeLevel + 1}` : ''}`}
                    </span>
                </div>

                <input
                    type="range"
                    min="0"
                    max={maxLevel}
                    step="1"
                    value={activeLevel === null ? maxLevel + 1 : activeLevel}
                    onChange={(e) => {
                        const val = parseInt(e.target.value);
                        if (val > maxLevel) {
                            setActiveLevel(null);
                        } else {
                            setActiveLevel(val);
                        }
                    }}
                    className="w-full accent-emerald-500 h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer"
                />

                <div className="flex justify-between text-xs text-slate-500 font-mono px-1 pb-2">
                    <span>0</span>
                    <span>{maxLevel}</span>
                    <span>All</span>
                </div>

                <label className="flex items-center gap-2 text-sm text-slate-300 cursor-pointer hover:text-white transition-colors">
                    <input
                        type="checkbox"
                        checked={showBelowLevel}
                        onChange={(e) => setShowBelowLevel(e.target.checked)}
                        className="w-4 h-4 accent-emerald-500 rounded bg-slate-800 border-slate-600 focus:ring-emerald-500"
                    />
                    顯示此階及以下所有層次
                </label>

                <label className="flex items-center gap-2 text-sm text-slate-300 cursor-pointer hover:text-white transition-colors">
                    <input
                        type="checkbox"
                        checked={showPathCounts}
                        onChange={(e) => setShowPathCounts(e.target.checked)}
                        className="w-4 h-4 accent-emerald-500 rounded bg-slate-800 border-slate-600 focus:ring-emerald-500"
                    />
                    顯示路徑數量標籤
                </label>

                <label className="flex items-center gap-2 text-sm text-slate-300 cursor-pointer hover:text-white transition-colors">
                    <input
                        type="checkbox"
                        checked={showGrundy}
                        onChange={(e) => setShowGrundy(e.target.checked)}
                        className="w-4 h-4 accent-emerald-500 rounded bg-slate-800 border-slate-600 focus:ring-emerald-500"
                    />
                    顯示 DP/Grundy 值
                </label>

                <label className="flex items-center gap-2 text-sm text-slate-300 cursor-pointer hover:text-white transition-colors">
                    <input
                        type="checkbox"
                        checked={showRectNodes}
                        onChange={(e) => setShowRectNodes(e.target.checked)}
                        className="w-4 h-4 accent-emerald-500 rounded bg-slate-800 border-slate-600 focus:ring-emerald-500"
                    />
                    顯示矩形 p1 節點
                </label>

                <label className="flex items-center gap-2 text-sm text-slate-300 cursor-pointer hover:text-white transition-colors">
                    <input
                        type="checkbox"
                        checked={showM1Nodes}
                        onChange={(e) => setShowM1Nodes(e.target.checked)}
                        className="w-4 h-4 accent-cyan-500 rounded bg-slate-800 border-slate-600 focus:ring-cyan-500"
                    />
                    顯示矩形 m1 節點
                </label>

                <label className="flex items-center gap-2 text-sm text-slate-300 cursor-pointer hover:text-white transition-colors">
                    <input
                        type="checkbox"
                        checked={showM2Nodes}
                        onChange={(e) => setShowM2Nodes(e.target.checked)}
                        className="w-4 h-4 accent-violet-400 rounded bg-slate-800 border-slate-600 focus:ring-violet-400"
                    />
                    顯示矩形 m2 節點
                </label>

                <label className="flex items-center gap-2 text-sm text-slate-300 cursor-pointer hover:text-white transition-colors">
                    <input
                        type="checkbox"
                        checked={showM3Nodes}
                        onChange={(e) => setShowM3Nodes(e.target.checked)}
                        className="w-4 h-4 accent-fuchsia-400 rounded bg-slate-800 border-slate-600 focus:ring-fuchsia-400"
                    />
                    顯示矩形 m3 節點
                </label>

                <label className="flex items-center gap-2 text-sm text-slate-300 cursor-pointer hover:text-white transition-colors">
                    <input
                        type="checkbox"
                        checked={showM4Nodes}
                        onChange={(e) => setShowM4Nodes(e.target.checked)}
                        className="w-4 h-4 accent-pink-400 rounded bg-slate-800 border-slate-600 focus:ring-pink-400"
                    />
                    顯示矩形 m4 節點
                </label>

                <label className="flex items-center gap-2 text-sm text-slate-300 cursor-pointer hover:text-white transition-colors">
                    <input
                        type="checkbox"
                        checked={showSquareNodes}
                        onChange={(e) => setShowSquareNodes(e.target.checked)}
                        className="w-4 h-4 accent-emerald-500 rounded bg-slate-800 border-slate-600 focus:ring-emerald-500"
                    />
                    顯示方形節點（隱藏時保留矩形端點）
                </label>

                <div className="pt-3 border-t border-slate-700/50">
                    <button
                        onClick={() => setNoAdjMode(!noAdjMode)}
                        className={`w-full py-2 px-3 rounded-lg text-sm font-semibold transition-all border ${noAdjMode ? 'bg-violet-700 border-violet-500 text-violet-100' : 'bg-slate-700 border-slate-600 text-slate-300 hover:bg-slate-600'}`}
                    >
                        {noAdjMode ? '✓ NoAdj 模式（無限制）' : 'NoAdj 模式（無限制）'}
                    </button>
                    {noAdjMode && (
                        <p className="text-[10px] text-violet-300 mt-1 px-1">移除 R1≤C0, C1≤R0 限制，終點為 [k,0,0,0] / [0,k,0,k] 等</p>
                    )}
                </div>

                <div className="mt-4 pt-4 border-t border-slate-700/50 text-[10px] text-slate-400 grid grid-cols-2 gap-y-2">
                    <p className="flex items-center gap-2">
                        <span className="w-3 h-3 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]"></span>
                        Square Win
                    </p>
                    <p className="flex items-center gap-2">
                        <span className="w-3 h-3 rounded-full bg-red-500"></span>
                        Square Lose
                    </p>
                    <p className="flex items-center gap-2">
                        <span className="w-3 h-3 rounded-full bg-cyan-300"></span>
                        Rect Win
                    </p>
                    <p className="flex items-center gap-2">
                        <span className="w-3 h-3 rounded-full bg-orange-400"></span>
                        Rect Lose
                    </p>
                    <p className="flex items-center gap-2">
                        <span className="w-3 h-3 rounded-full bg-yellow-400 shadow-[0_0_8px_rgba(255,255,0,0.6)]"></span>
                        Target (End)
                    </p>
                    <p className="flex items-center gap-2">
                        <span className="w-3 h-3 rounded-full bg-white shadow-[0_0_8px_rgba(255,255,255,0.4)]"></span>
                        Root (Start)
                    </p>
                </div>
            </div>
        </div>
    );
};
