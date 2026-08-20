import { useState } from 'react';
import { motion } from 'framer-motion';
import { UploadCloud } from 'lucide-react';

export default function Uploader({ onUpload, isLoading }) {
  const [isDragOver, setIsDragOver] = useState(false);

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) onUpload(file);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`relative flex flex-col items-center justify-center w-full max-w-xl h-64 p-6 border-2 border-dashed rounded-2xl transition-colors ${
        isDragOver ? 'border-teal-500 bg-teal-50/10' : 'border-slate-600 bg-slate-800'
      }`}
      onDragOver={(e) => { e.preventDefault(); setIsDragOver(true); }}
      onDragLeave={() => setIsDragOver(false)}
      onDrop={handleDrop}
    >
      <input
        type="file"
        accept="image/*"
        onChange={(e) => onUpload(e.target.files[0])}
        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
        disabled={isLoading}
      />
      
      <UploadCloud className={`w-16 h-16 mb-4 ${isDragOver ? 'text-teal-500' : 'text-slate-400'}`} />
      
      {isLoading ? (
        <div className="flex flex-col items-center">
          <div className="w-8 h-8 border-4 border-teal-500 border-t-transparent rounded-full animate-spin"></div>
          <p className="mt-4 text-teal-400 font-medium">AI is analyzing the retina...</p>
        </div>
      ) : (
        <div className="text-center">
          <p className="text-lg font-semibold text-slate-200">Drag & drop an image here</p>
          <p className="text-sm text-slate-400 mt-2">or click to browse from your computer</p>
        </div>
      )}
    </motion.div>
  );
}