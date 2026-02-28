import { ChessGraph } from './components/ChessGraph';
import { SlicerPanel } from './components/SlicerPanel';
import { useStore } from './store/useStore';
import { Home } from 'lucide-react';

function App() {
  const { selectedPath, setSelectedNode, setActiveLevel, triggerCameraReset } = useStore();

  const handleHomeClick = () => {
    setSelectedNode(null);
    setActiveLevel(null);
    triggerCameraReset();
  };

  return (
    <div className="w-full h-screen relative overflow-hidden bg-slate-900 font-sans">
      <ChessGraph />
      <SlicerPanel />

      {/* Title & Home */}
      <div className="absolute top-4 left-6 z-10 flex items-start gap-4 text-white">
        <div>
          <h1 className="text-3xl font-black tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-cyan-400 drop-shadow-sm">
            DoubleChess Layer
          </h1>
          <p className="text-sm font-medium text-slate-400 mt-1 uppercase tracking-widest pointer-events-none">
            3D Game Tree Visualizer
          </p>
        </div>
        <button
          onClick={handleHomeClick}
          className="bg-slate-800/80 hover:bg-slate-700 text-slate-300 hover:text-white p-2 rounded-lg border border-slate-600 shadow-md backdrop-blur-sm transition-all flex items-center gap-2 group"
          title="Reset View"
        >
          <Home className="w-5 h-5 group-hover:scale-110 transition-transform" />
          <span className="text-sm font-semibold hidden md:block">Home</span>
        </button>
      </div>

      {/* Selection Reset Button */}
      {selectedPath.length > 0 && (
        <button
          onClick={() => setSelectedNode(null)}
          className="absolute bottom-6 left-1/2 -translate-x-1/2 z-10 bg-slate-800 hover:bg-slate-700 text-white px-6 py-3 rounded-full shadow-2xl border border-slate-600 transition-all font-medium text-sm hover:scale-105 active:scale-95"
        >
          Clear Path Selection
        </button>
      )}

      {/* Help prompt */}
      <div className="absolute bottom-6 right-6 z-10 text-xs text-slate-500 pointer-events-none text-right">
        <p>Left Click + Drag to Rotate</p>
        <p>Right Click + Drag to Pan</p>
        <p>Scroll to Zoom</p>
      </div>
    </div>
  );
}

export default App;
