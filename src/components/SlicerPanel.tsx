import { useStore } from '../store/useStore';
import { Layers, Box, CreditCard } from 'lucide-react';

export const SlicerPanel = () => {
    const { activeLevel, maxLevel, setActiveLevel, showBelowLevel, setShowBelowLevel, showPathCounts, setShowPathCounts, showGrundy, setShowGrundy, viewMode, setViewMode } = useStore();

    return (
        <div className="absolute top-4 right-4 bg-slate-800/90 text-slate-200 p-4 rounded-xl border border-slate-700 shadow-2xl backdrop-blur-md w-72 z-10 transition-all">
            <div className="flex items-center justify-between mb-4 border-b border-slate-700 pb-3">
                <div className="flex items-center gap-2">
                    <Layers className="w-5 h-5 text-emerald-400" />
                    <h2 className="font-semibold text-lg">Level Slicer</h2>
                </div>
                <div className="flex bg-slate-900 rounded-lg p-1 border border-slate-700">
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

                <div className="mt-4 pt-4 border-t border-slate-700/50 text-xs text-slate-400 space-y-2">
                    <p className="flex items-center gap-2">
                        <span className="w-3 h-3 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]"></span>
                        Winning Nodes
                    </p>
                    <p className="flex items-center gap-2">
                        <span className="w-3 h-3 rounded-full bg-red-500 shadow-sm"></span>
                        Losing Nodes
                    </p>
                    <p className="flex items-center gap-2">
                        <span className="w-4 h-0.5 bg-amber-500 rounded"></span>
                        Level Traversal Line
                    </p>
                </div>
            </div>
        </div>
    );
};
