import { useState } from 'react';
import axios from 'axios';
import Uploader from '../components/Uploader';
import ResultView from '../components/ResultView';

export default function Home() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleUpload = async (selectedFile) => {
    if (!selectedFile) return;
    
    setFile(selectedFile);
    setPreview(URL.createObjectURL(selectedFile));
    setIsLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      const response = await axios.post("http://127.0.0.1:8000/upload-image/", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Something went wrong connecting to the AI Server.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setFile(null);
    setPreview(null);
    setResult(null);
    setError(null);
  };

  return (
    <div className="min-h-screen bg-slate-900 text-slate-50 flex flex-col items-center py-20 px-4 font-sans">
      
      {/* Header */}
      <div className="text-center mb-12">
        <h1 className="text-5xl font-bold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-teal-400 to-blue-500 mb-4">
          Retina AI Diagnostic
        </h1>
        <p className="text-slate-400 text-lg max-w-xl mx-auto">
          Upload an OCT or Fundus retina scan. Our deep learning model will analyze it and provide a Grad-CAM explainability heatmap.
        </p>
      </div>

      {/* Main Content Area */}
      {error && (
        <div className="mb-6 p-4 bg-red-500/20 border border-red-500 text-red-300 rounded-xl max-w-xl w-full text-center">
          {error}
        </div>
      )}

      {!result ? (
        <Uploader onUpload={handleUpload} isLoading={isLoading} />
      ) : (
        <ResultView result={result} preview={preview} onReset={handleReset} />
      )}
      
    </div>
  );
}