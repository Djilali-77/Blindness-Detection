import { motion } from 'framer-motion';
import { RefreshCw, AlertCircle } from 'lucide-react';

export default function ResultView({ result, preview, onReset }) {
  const levels = ["No DR", "Mild", "Moderate", "Severe", "Proliferative DR"];
  const diagnosisLevel = result.diagnosis_level;
  
  // URL from FastAPI static mount
  const gradCamUrl = `http://127.0.0.1:8000/images/${result.grad_cam_image}`;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="w-full max-w-4xl bg-slate-800 rounded-3xl p-8 shadow-2xl"
    >
      <div className="flex flex-col md:flex-row gap-8">
        
        {/* Images Grid */}
        <div className="flex-1 grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <span className="text-sm font-medium text-slate-400">Original Scan</span>
            <img src={preview} alt="Original" className="w-full aspect-square object-cover rounded-xl border border-slate-700" />
          </div>
          <div className="space-y-2">
            <span className="text-sm font-medium text-teal-400">AI Heatmap (Grad-CAM)</span>
            <img src={gradCamUrl} alt="Grad-CAM" className="w-full aspect-square object-cover rounded-xl border border-teal-500/50 shadow-[0_0_15px_rgba(20,184,166,0.2)]" />
          </div>
        </div>

        {/* Info Panel */}
        <div className="flex-1 flex flex-col justify-center space-y-6">
          <div className="bg-slate-900/50 p-6 rounded-2xl border border-slate-700">
            <div className="flex items-center gap-3 mb-2">
              <AlertCircle className={diagnosisLevel > 0 ? "text-amber-500" : "text-emerald-500"} />
              <h3 className="text-xl font-semibold text-white">Diagnosis Result</h3>
            </div>
            
            <div className="mt-4">
              <p className="text-4xl font-bold text-teal-400 mb-2">
                Level {diagnosisLevel}
              </p>
              <p className="text-lg text-slate-300">
                Condition: <span className="font-semibold text-white">{levels[diagnosisLevel]}</span>
              </p>
            </div>
          </div>

          <button
            onClick={onReset}
            className="flex items-center justify-center gap-2 w-full py-4 bg-slate-700 hover:bg-slate-600 text-white rounded-xl transition-all font-medium"
          >
            <RefreshCw className="w-5 h-5" />
            Analyze Another Patient
          </button>
        </div>
      </div>
    </motion.div>
  );
}