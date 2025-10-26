// 'use client';
// import React, { useState, useEffect, useRef } from 'react';
// import { Camera, Upload, Brain, Activity, Trash2, Clock, CheckCircle, Info } from 'lucide-react';
// import { ToastContainer, toast } from 'react-toastify';
// import 'react-toastify/dist/ReactToastify.css';
// import AxiosInstance from "@/components/AxiosInstance";

// const CNNImageClassifier = () => {
//   const [activeTab, setActiveTab] = useState('predict');
//   const [isLoading, setIsLoading] = useState(false);
//   const [modelStatus, setModelStatus] = useState(null);
//   const fileInputRef = useRef(null);

//   const [modelConfig, setModelConfig] = useState({
//     model_type: 'simple',
//     target_size: [150, 150],
//     batch_size: 32
//   });

//   const [trainingConfig, setTrainingConfig] = useState({
//     epochs: 10,
//     batch_size: 32
//   });
//   const [trainingResults, setTrainingResults] = useState(null);

//   const [selectedImage, setSelectedImage] = useState(null);
//   const [imagePreview, setImagePreview] = useState(null);
//   const [predictionResult, setPredictionResult] = useState(null);
//   const [predictionHistory, setPredictionHistory] = useState([]);
//   const [datasetInfo, setDatasetInfo] = useState(null);

//   const architectures = [
//     {
//       name: 'simple',
//       title: 'Simple CNN',
//       description: 'Fast and lightweight - 3 convolutional layers',
//       features: ['Quick training', 'Good for learning', 'Lower accuracy'],
//       icon: '🚀'
//     },
//     {
//       name: 'vgg',
//       title: 'VGG-Style',
//       description: 'Deeper architecture - Better accuracy',
//       features: ['4 Conv blocks', 'Higher accuracy', 'Slower training'],
//       icon: '🎯'
//     },
//     {
//       name: 'resnet',
//       title: 'ResNet-Inspired',
//       description: 'State-of-the-art - Best performance',
//       features: ['Skip connections', 'Best accuracy', 'Production ready'],
//       icon: '⭐'
//     }
//   ];

//   useEffect(() => {
//     const savedHistory = JSON.parse(localStorage.getItem('cnnPredictions') || '[]');
//     setPredictionHistory(savedHistory);
//     checkModelStatus();
//   }, []);

//   const checkModelStatus = async () => {
//     try {
//       const response = await AxiosInstance.get('/api/cnn/health');
//       setModelStatus(response.data);
//     } catch (error) {
//       console.error('Error checking model status:', error);
//       toast.error('Failed to check model status');
//     }
//   };

//   const handleCreateModel = async () => {
//     setIsLoading(true);
//     try {
//       const response = await AxiosInstance.post('/api/cnn/model/create', modelConfig);
//       toast.success('Model created successfully!');
//       await checkModelStatus();
//       await fetchDatasetInfo();
//     } catch (error) {
//       console.error('Model creation error:', error);
//       toast.error(error.response?.data?.detail || 'Model creation failed');
//     } finally {
//       setIsLoading(false);
//     }
//   };

//   const handleTrainModel = async () => {
//     setIsLoading(true);
//     setTrainingResults(null);
    
//     try {
//       const response = await AxiosInstance.post('/api/cnn/model/train', trainingConfig);
//       setTrainingResults(response.data.data);
//       toast.success('Training completed successfully!');
//       await checkModelStatus();
//     } catch (error) {
//       console.error('Training error:', error);
//       toast.error(error.response?.data?.detail || 'Training failed');
//     } finally {
//       setIsLoading(false);
//     }
//   };

//   const handleEvaluateModel = async () => {
//     setIsLoading(true);
//     try {
//       const response = await AxiosInstance.post('/api/cnn/model/evaluate');
//       setTrainingResults(prev => ({ ...prev, ...response.data.data }));
//       toast.success('Evaluation completed!');
//     } catch (error) {
//       console.error('Evaluation error:', error);
//       toast.error(error.response?.data?.detail || 'Evaluation failed');
//     } finally {
//       setIsLoading(false);
//     }
//   };

//   const handleImageSelect = (e) => {
//     const file = e.target.files?.[0];
//     if (file) {
//       setSelectedImage(file);
//       const reader = new FileReader();
//       reader.onloadend = () => {
//         setImagePreview(reader.result);
//       };
//       reader.readAsDataURL(file);
//     }
//   };

//   const handlePredict = async () => {
//     if (!selectedImage) {
//       toast.warning('Please select an image first');
//       return;
//     }

//     setIsLoading(true);
//     try {
//       const formData = new FormData();
//       formData.append('file', selectedImage, selectedImage.name);

//       console.log('Sending prediction request...');
//       console.log('File:', selectedImage.name, 'Size:', selectedImage.size);

//       const response = await AxiosInstance.post('/api/cnn/predict/image', formData, {
//         headers: {
//           'Content-Type': 'multipart/form-data',
//         },
//       });

//       console.log('Prediction result:', response.data);
      
//       setPredictionResult(response.data.data);
      
//       const newPrediction = {
//         id: Date.now(),
//         timestamp: new Date().toLocaleString(),
//         prediction: response.data.data.prediction,
//         confidence: response.data.data.confidence,
//         image: imagePreview
//       };
      
//       const newHistory = [newPrediction, ...predictionHistory.slice(0, 19)];
//       setPredictionHistory(newHistory);
//       localStorage.setItem('cnnPredictions', JSON.stringify(newHistory));
      
//       toast.success('Prediction completed!');
//     } catch (error) {
//       console.error('Prediction error:', error);
//       toast.error(error.response?.data?.detail || 'Prediction failed');
//     } finally {
//       setIsLoading(false);
//     }
//   };

//   const fetchDatasetInfo = async () => {
//     try {
//       const response = await AxiosInstance.get('/api/cnn/dataset/info');
//       setDatasetInfo(response.data.data);
//     } catch (error) {
//       console.error('Error fetching dataset info:', error);
//       toast.error('Failed to fetch dataset info');
//     }
//   };

//   const clearHistory = () => {
//     setPredictionHistory([]);
//     localStorage.removeItem('cnnPredictions');
//     toast.info('History cleared');
//   };

//   return (
//     <div className="min-h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-900 py-8 px-4">
//       <ToastContainer position="top-right" autoClose={3000} theme="dark" />
      
//       <div className="max-w-7xl mx-auto">
//         <div className="text-center mb-8">
//           <h1 className="text-5xl font-bold text-white mb-3 flex items-center justify-center gap-3">
//             <Brain className="w-12 h-12" />
//             CNN IMAGE CLASSIFIER
//           </h1>
//           <div className="w-32 h-1 bg-gradient-to-r from-pink-500 to-purple-500 mx-auto mb-4"></div>
//           <p className="text-gray-200 max-w-2xl mx-auto text-lg">
//             Deep Learning powered Cat vs Dog image classification. Train custom models and get real-time predictions.
//           </p>
//         </div>

//         {modelStatus && (
//           <div className="bg-gray-800/50 backdrop-blur rounded-xl p-4 mb-6 border border-purple-500/30">
//             <div className="flex flex-wrap items-center justify-between gap-4">
//               <div className="flex items-center gap-3">
//                 <Activity className="w-5 h-5 text-purple-400" />
//                 <span className="text-gray-300">Model Status:</span>
//                 <span className={`px-3 py-1 rounded-full text-sm font-medium ${
//                   modelStatus.model_status === 'loaded' 
//                     ? 'bg-green-500/20 text-green-400' 
//                     : 'bg-yellow-500/20 text-yellow-400'
//                 }`}>
//                   {modelStatus.model_status || 'Not initialized'}
//                 </span>
//               </div>
//               <div className="flex items-center gap-3">
//                 <span className="text-gray-300">Training:</span>
//                 <span className={`px-3 py-1 rounded-full text-sm font-medium ${
//                   modelStatus.training_status === 'trained'
//                     ? 'bg-green-500/20 text-green-400'
//                     : 'bg-gray-500/20 text-gray-400'
//                 }`}>
//                   {modelStatus.training_status || 'Not trained'}
//                 </span>
//               </div>
//               <button
//                 onClick={checkModelStatus}
//                 className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-sm transition-colors"
//               >
//                 Refresh Status
//               </button>
//             </div>
//           </div>
//         )}

//         <div className="flex flex-wrap gap-2 mb-8 bg-gray-800/30 backdrop-blur p-2 rounded-xl">
//           {[
//             { id: 'predict', label: 'Predict', icon: <Camera className="w-4 h-4" /> },
//             { id: 'model', label: 'Create Model', icon: <Brain className="w-4 h-4" /> },
//             { id: 'train', label: 'Train', icon: <Activity className="w-4 h-4" /> },
//             { id: 'history', label: 'History', icon: <Clock className="w-4 h-4" /> },
//             { id: 'info', label: 'Info', icon: <Info className="w-4 h-4" /> }
//           ].map((tab) => (
//             <button
//               key={tab.id}
//               onClick={() => setActiveTab(tab.id)}
//               className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${
//                 activeTab === tab.id
//                   ? 'bg-purple-600 text-white shadow-lg shadow-purple-500/50'
//                   : 'text-gray-300 hover:bg-gray-700 hover:text-white'
//               }`}
//             >
//               {tab.icon}
//               <span className="hidden sm:inline">{tab.label}</span>
//             </button>
//           ))}
//         </div>

//         {activeTab === 'predict' && (
//           <div className="bg-gray-800/50 backdrop-blur rounded-xl p-6 shadow-2xl border border-purple-500/30">
//             <h2 className="text-2xl text-white mb-6 flex items-center gap-2">
//               <Camera className="w-6 h-6" />
//               Image Prediction
//             </h2>

//             <div className="grid md:grid-cols-2 gap-8">
//               <div className="space-y-6">
//                 <div
//                   onClick={() => fileInputRef.current?.click()}
//                   className="border-2 border-dashed border-purple-500/50 rounded-xl p-8 text-center cursor-pointer hover:border-purple-500 hover:bg-purple-500/5 transition-all"
//                 >
//                   {imagePreview ? (
//                     <img src={imagePreview} alt="Preview" className="max-h-64 mx-auto rounded-lg" />
//                   ) : (
//                     <div className="space-y-4">
//                       <Upload className="w-16 h-16 mx-auto text-purple-400" />
//                       <div>
//                         <p className="text-white text-lg">Click to upload image</p>
//                         <p className="text-gray-400 text-sm mt-2">JPG, PNG, or GIF (max 10MB)</p>
//                       </div>
//                     </div>
//                   )}
//                   <input
//                     ref={fileInputRef}
//                     type="file"
//                     accept="image/*"
//                     onChange={handleImageSelect}
//                     className="hidden"
//                   />
//                 </div>

//                 {selectedImage && (
//                   <div className="space-y-3">
//                     <button
//                       onClick={handlePredict}
//                       disabled={isLoading}
//                       className="w-full py-3 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 disabled:from-gray-600 disabled:to-gray-600 disabled:cursor-not-allowed text-white rounded-lg transition-all flex items-center justify-center gap-2 font-medium"
//                     >
//                       {isLoading ? (
//                         <>
//                           <div className="animate-spin rounded-full h-5 w-5 border-t-2 border-b-2 border-white"></div>
//                           Predicting...
//                         </>
//                       ) : (
//                         <>
//                           <Brain className="w-5 h-5" />
//                           Classify Image
//                         </>
//                       )}
//                     </button>
                    
//                     <button
//                       onClick={() => {
//                         setSelectedImage(null);
//                         setImagePreview(null);
//                         setPredictionResult(null);
//                       }}
//                       className="w-full py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors"
//                     >
//                       Clear Image
//                     </button>
//                   </div>
//                 )}
//               </div>

//               <div className="space-y-6">
//                 {predictionResult ? (
//                   <div className="bg-gradient-to-r from-purple-900/50 to-pink-900/50 rounded-xl p-6 border border-purple-500">
//                     <h3 className="text-xl text-white mb-4 flex items-center gap-2">
//                       {predictionResult.prediction === 'dog' ? '🐕' : '🐱'}
//                       Prediction Result
//                     </h3>

//                     <div className="text-center mb-6">
//                       <div className="text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-400 mb-2">
//                         {predictionResult.prediction.toUpperCase()}
//                       </div>
//                       <div className="text-gray-300">
//                         Confidence: {(predictionResult.confidence * 100).toFixed(2)}%
//                       </div>
//                     </div>

//                     <div className="space-y-3">
//                       <div className="bg-gray-800/50 rounded-lg p-3">
//                         <div className="text-sm text-gray-400 mb-2">Confidence Score</div>
//                         <div className="w-full bg-gray-700 rounded-full h-3">
//                           <div
//                             className="bg-gradient-to-r from-purple-500 to-pink-500 h-3 rounded-full transition-all duration-500"
//                             style={{ width: `${predictionResult.confidence * 100}%` }}
//                           ></div>
//                         </div>
//                       </div>

//                       {predictionResult.probabilities && (
//                         <div className="bg-gray-800/50 rounded-lg p-3 space-y-2">
//                           <div className="text-sm text-gray-400 mb-2">Class Probabilities</div>
//                           <div className="flex justify-between text-sm">
//                             <span className="text-gray-300">Cat:</span>
//                             <span className="text-white">{(predictionResult.probabilities.cat * 100).toFixed(2)}%</span>
//                           </div>
//                           <div className="flex justify-between text-sm">
//                             <span className="text-gray-300">Dog:</span>
//                             <span className="text-white">{(predictionResult.probabilities.dog * 100).toFixed(2)}%</span>
//                           </div>
//                         </div>
//                       )}
//                     </div>
//                   </div>
//                 ) : (
//                   <div className="bg-gray-700/50 rounded-xl p-6 text-center">
//                     <div className="text-6xl mb-4">🖼️</div>
//                     <p className="text-gray-400">Upload an image to get started</p>
//                     <p className="text-gray-500 text-sm mt-2">The model will classify it as Cat or Dog</p>
//                   </div>
//                 )}

//                 <div className="bg-gray-700/50 rounded-lg p-4">
//                   <h4 className="text-white mb-3 font-medium">💡 Tips</h4>
//                   <ul className="text-gray-300 text-sm space-y-2">
//                     <li>• Use clear, well-lit images</li>
//                     <li>• Single animal per image works best</li>
//                     <li>• Front-facing angles improve accuracy</li>
//                     <li>• Avoid heavily filtered images</li>
//                   </ul>
//                 </div>
//               </div>
//             </div>
//           </div>
//         )}

//         {activeTab === 'model' && (
//           <div className="bg-gray-800/50 backdrop-blur rounded-xl p-6 shadow-2xl border border-purple-500/30">
//             <h2 className="text-2xl text-white mb-6 flex items-center gap-2">
//               <Brain className="w-6 h-6" />
//               Create CNN Model
//             </h2>

//             <div className="grid md:grid-cols-3 gap-6 mb-8">
//               {architectures.map((arch) => (
//                 <div
//                   key={arch.name}
//                   onClick={() => setModelConfig({ ...modelConfig, model_type: arch.name })}
//                   className={`cursor-pointer rounded-xl p-6 border-2 transition-all ${
//                     modelConfig.model_type === arch.name
//                       ? 'border-purple-500 bg-purple-500/10'
//                       : 'border-gray-600 hover:border-gray-500'
//                   }`}
//                 >
//                   <div className="text-4xl mb-3">{arch.icon}</div>
//                   <h3 className="text-xl text-white mb-2">{arch.title}</h3>
//                   <p className="text-gray-400 text-sm mb-4">{arch.description}</p>
//                   <div className="space-y-1">
//                     {arch.features.map((feature, idx) => (
//                       <div key={idx} className="text-gray-300 text-xs flex items-center gap-2">
//                         <CheckCircle className="w-3 h-3 text-green-400" />
//                         {feature}
//                       </div>
//                     ))}
//                   </div>
//                 </div>
//               ))}
//             </div>

//             <div className="grid md:grid-cols-2 gap-6 mb-6">
//               <div>
//                 <label className="block text-gray-300 mb-2">Image Size (Width × Height)</label>
//                 <select
//                   value={JSON.stringify(modelConfig.target_size)}
//                   onChange={(e) => setModelConfig({ ...modelConfig, target_size: JSON.parse(e.target.value) })}
//                   className="w-full p-3 bg-gray-700 rounded-lg text-white focus:ring-2 focus:ring-purple-500 focus:outline-none"
//                 >
//                   <option value="[150,150]">150 × 150 (Fast)</option>
//                   <option value="[224,224]">224 × 224 (Balanced)</option>
//                   <option value="[299,299]">299 × 299 (High Quality)</option>
//                 </select>
//               </div>

//               <div>
//                 <label className="block text-gray-300 mb-2">Batch Size</label>
//                 <select
//                   value={modelConfig.batch_size}
//                   onChange={(e) => setModelConfig({ ...modelConfig, batch_size: parseInt(e.target.value) })}
//                   className="w-full p-3 bg-gray-700 rounded-lg text-white focus:ring-2 focus:ring-purple-500 focus:outline-none"
//                 >
//                   <option value="16">16 (Small GPU)</option>
//                   <option value="32">32 (Standard)</option>
//                   <option value="64">64 (Large GPU)</option>
//                 </select>
//               </div>
//             </div>

//             <button
//               onClick={handleCreateModel}
//               disabled={isLoading}
//               className="w-full py-3 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 disabled:from-gray-600 disabled:to-gray-600 disabled:cursor-not-allowed text-white rounded-lg transition-all flex items-center justify-center gap-2 font-medium text-lg"
//             >
//               {isLoading ? (
//                 <>
//                   <div className="animate-spin rounded-full h-5 w-5 border-t-2 border-b-2 border-white"></div>
//                   Creating Model...
//                 </>
//               ) : (
//                 <>
//                   <Brain className="w-5 h-5" />
//                   Create Model
//                 </>
//               )}
//             </button>
//           </div>
//         )}

//         {activeTab === 'train' && (
//           <div className="bg-gray-800/50 backdrop-blur rounded-xl p-6 shadow-2xl border border-purple-500/30">
//             <h2 className="text-2xl text-white mb-6 flex items-center gap-2">
//               <Activity className="w-6 h-6" />
//               Train Model
//             </h2>

//             <div className="grid md:grid-cols-2 gap-8">
//               <div className="space-y-6">
//                 <div>
//                   <label className="block text-gray-300 mb-2">Number of Epochs</label>
//                   <input
//                     type="number"
//                     min="1"
//                     max="100"
//                     value={trainingConfig.epochs}
//                     onChange={(e) => setTrainingConfig({ ...trainingConfig, epochs: parseInt(e.target.value) })}
//                     className="w-full p-3 bg-gray-700 rounded-lg text-white focus:ring-2 focus:ring-purple-500 focus:outline-none"
//                   />
//                   <p className="text-gray-400 text-sm mt-1">Recommended: 10-20 epochs</p>
//                 </div>

//                 <div>
//                   <label className="block text-gray-300 mb-2">Batch Size</label>
//                   <select
//                     value={trainingConfig.batch_size}
//                     onChange={(e) => setTrainingConfig({ ...trainingConfig, batch_size: parseInt(e.target.value) })}
//                     className="w-full p-3 bg-gray-700 rounded-lg text-white focus:ring-2 focus:ring-purple-500 focus:outline-none"
//                   >
//                     <option value="16">16</option>
//                     <option value="32">32</option>
//                     <option value="64">64</option>
//                   </select>
//                 </div>

//                 <button
//                   onClick={handleTrainModel}
//                   disabled={isLoading || modelStatus?.model_status !== 'loaded'}
//                   className="w-full py-3 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 disabled:from-gray-600 disabled:to-gray-600 disabled:cursor-not-allowed text-white rounded-lg transition-all flex items-center justify-center gap-2 font-medium"
//                 >
//                   {isLoading ? (
//                     <>
//                       <div className="animate-spin rounded-full h-5 w-5 border-t-2 border-b-2 border-white"></div>
//                       Training...
//                     </>
//                   ) : (
//                     <>
//                       <Activity className="w-5 h-5" />
//                       Start Training
//                     </>
//                   )}
//                 </button>

//                 {modelStatus?.training_status === 'trained' && (
//                   <button
//                     onClick={handleEvaluateModel}
//                     disabled={isLoading}
//                     className="w-full py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded-lg transition-colors flex items-center justify-center gap-2"
//                   >
//                     Evaluate on Test Set
//                   </button>
//                 )}
//               </div>

//               <div>
//                 {trainingResults ? (
//                   <div className="bg-gradient-to-r from-green-900/50 to-emerald-900/50 rounded-xl p-6 border border-green-500">
//                     <h3 className="text-xl text-white mb-4">Training Results</h3>
                    
//                     <div className="space-y-4">
//                       {trainingResults.final_accuracy && (
//                         <div className="bg-gray-800/50 rounded-lg p-4">
//                           <div className="text-sm text-gray-400 mb-2">Training Accuracy</div>
//                           <div className="text-3xl font-bold text-green-400">
//                             {(trainingResults.final_accuracy * 100).toFixed(2)}%
//                           </div>
//                         </div>
//                       )}

//                       {trainingResults.validation_accuracy && (
//                         <div className="bg-gray-800/50 rounded-lg p-4">
//                           <div className="text-sm text-gray-400 mb-2">Validation Accuracy</div>
//                           <div className="text-3xl font-bold text-blue-400">
//                             {(trainingResults.validation_accuracy * 100).toFixed(2)}%
//                           </div>
//                         </div>
//                       )}

//                       {trainingResults.test_accuracy && (
//                         <div className="bg-gray-800/50 rounded-lg p-4">
//                           <div className="text-sm text-gray-400 mb-2">Test Accuracy</div>
//                           <div className="text-3xl font-bold text-purple-400">
//                             {(trainingResults.test_accuracy * 100).toFixed(2)}%
//                           </div>
//                         </div>
//                       )}

//                       {trainingResults.training_time && (
//                         <div className="text-gray-300 text-sm">
//                           Training time: {trainingResults.training_time}
//                         </div>
//                       )}
//                     </div>
//                   </div>
//                 ) : (
//                   <div className="bg-gray-700/50 rounded-xl p-6 text-center">
//                     <Activity className="w-16 h-16 mx-auto text-gray-500 mb-4" />
//                     <p className="text-gray-400">No training results yet</p>
//                     <p className="text-gray-500 text-sm mt-2">Train the model to see results</p>
//                   </div>
//                 )}
//               </div>
//             </div>
//           </div>
//         )}

//         {activeTab === 'history' && (
//           <div className="bg-gray-800/50 backdrop-blur rounded-xl p-6 shadow-2xl border border-purple-500/30">
//             <div className="flex items-center justify-between mb-6">
//               <h2 className="text-2xl text-white flex items-center gap-2">
//                 <Clock className="w-6 h-6" />
//                 Prediction History
//               </h2>
//               {predictionHistory.length > 0 && (
//                 <button
//                   onClick={clearHistory}
//                   className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg text-sm flex items-center gap-2"
//                 >
//                   <Trash2 className="w-4 h-4" />
//                   Clear History
//                 </button>
//               )}
//             </div>

//             {predictionHistory.length > 0 ? (
//               <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
//                 {predictionHistory.map((item) => (
//                   <div key={item.id} className="bg-gray-700/50 rounded-lg overflow-hidden border border-gray-600">
//                     <img src={item.image} alt="Prediction" className="w-full h-48 object-cover" />
//                     <div className="p-4">
//                       <div className="flex items-center justify-between mb-2">
//                         <span className="text-2xl">{item.prediction === 'dog' ? '🐕' : '🐱'}</span>
//                         <span className="text-xl font-bold text-purple-400">
//                           {item.prediction.toUpperCase()}
//                         </span>
//                       </div>
//                       <div className="text-sm text-gray-400 mb-2">
//                         Confidence: {(item.confidence * 100).toFixed(2)}%
//                       </div>
//                       <div className="text-xs text-gray-500">{item.timestamp}</div>
//                     </div>
//                   </div>
//                 ))}
//               </div>
//             ) : (
//               <div className="text-center text-gray-400 py-12">
//                 <Clock className="w-16 h-16 mx-auto text-gray-500 mb-4" />
//                 <p className="text-xl">No predictions yet</p>
//                 <p className="text-gray-500 text-sm mt-2">Upload and classify images to see your history</p>
//               </div>
//             )}
//           </div>
//         )}

//         {activeTab === 'info' && (
//           <div className="bg-gray-800/50 backdrop-blur rounded-xl p-6 shadow-2xl border border-purple-500/30">
//             <h2 className="text-2xl text-white mb-6 flex items-center gap-2">
//               <Info className="w-6 h-6" />
//               Model Information & Dataset
//             </h2>

//             <div className="grid md:grid-cols-2 gap-8">
//               <div className="space-y-6">
//                 <div className="bg-gray-700/50 rounded-lg p-5">
//                   <h3 className="text-lg text-white mb-4 flex items-center gap-2">
//                     <Brain className="w-5 h-5" />
//                     Model Details
//                   </h3>
//                   <div className="space-y-3 text-sm">
//                     <div className="flex justify-between">
//                       <span className="text-gray-300">Framework:</span>
//                       <span className="text-purple-400">TensorFlow/Keras</span>
//                     </div>
//                     <div className="flex justify-between">
//                       <span className="text-gray-300">Task:</span>
//                       <span className="text-purple-400">Binary Classification</span>
//                     </div>
//                     <div className="flex justify-between">
//                       <span className="text-gray-300">Output:</span>
//                       <span className="text-purple-400">Cat vs Dog</span>
//                     </div>
//                     <div className="flex justify-between">
//                       <span className="text-gray-300">API:</span>
//                       <span className="text-purple-400">FastAPI</span>
//                     </div>
//                   </div>
//                 </div>

//                 <div className="bg-gray-700/50 rounded-lg p-5">
//                   <h3 className="text-lg text-white mb-4">Architecture Options</h3>
//                   <div className="space-y-3">
//                     {architectures.map((arch) => (
//                       <div key={arch.name} className="border-l-4 border-purple-500 pl-3">
//                         <div className="flex items-center gap-2 mb-1">
//                           <span className="text-xl">{arch.icon}</span>
//                           <span className="text-white font-medium">{arch.title}</span>
//                         </div>
//                         <p className="text-gray-400 text-sm">{arch.description}</p>
//                       </div>
//                     ))}
//                   </div>
//                 </div>

//                 <div className="bg-gray-700/50 rounded-lg p-5">
//                   <h3 className="text-lg text-white mb-4">Key Features</h3>
//                   <div className="space-y-2 text-sm">
//                     <div className="flex items-center gap-2 text-gray-300">
//                       <CheckCircle className="w-4 h-4 text-green-400" />
//                       Convolutional layers for feature extraction
//                     </div>
//                     <div className="flex items-center gap-2 text-gray-300">
//                       <CheckCircle className="w-4 h-4 text-green-400" />
//                       Max pooling for dimensionality reduction
//                     </div>
//                     <div className="flex items-center gap-2 text-gray-300">
//                       <CheckCircle className="w-4 h-4 text-green-400" />
//                       Dropout for regularization
//                     </div>
//                     <div className="flex items-center gap-2 text-gray-300">
//                       <CheckCircle className="w-4 h-4 text-green-400" />
//                       Data augmentation for better generalization
//                     </div>
//                     <div className="flex items-center gap-2 text-gray-300">
//                       <CheckCircle className="w-4 h-4 text-green-400" />
//                       Binary crossentropy loss function
//                     </div>
//                   </div>
//                 </div>
//               </div>

//               <div className="space-y-6">
//                 <div className="bg-gray-700/50 rounded-lg p-5">
//                   <h3 className="text-lg text-white mb-4">Dataset Information</h3>
//                   {datasetInfo ? (
//                     <div className="space-y-4">
//                       <div className="text-sm">
//                         <div className="text-gray-400 mb-2">Total Images:</div>
//                         <div className="text-2xl font-bold text-purple-400">
//                           {datasetInfo.total_images?.toLocaleString() || 'N/A'}
//                         </div>
//                       </div>

//                       {datasetInfo.folders && (
//                         <div className="space-y-3">
//                           {Object.entries(datasetInfo.folders).map(([folder, info]) => (
//                             <div key={folder} className="bg-gray-800/50 rounded p-3">
//                               <div className="font-medium text-white mb-2 capitalize">{folder}</div>
//                               {info.subfolders && (
//                                 <div className="grid grid-cols-2 gap-2 text-sm">
//                                   {Object.entries(info.subfolders).map(([subfolder, count]) => (
//                                     <div key={subfolder} className="flex justify-between">
//                                       <span className="text-gray-400 capitalize">{subfolder}:</span>
//                                       <span className="text-purple-400">{count}</span>
//                                     </div>
//                                   ))}
//                                 </div>
//                               )}
//                             </div>
//                           ))}
//                         </div>
//                       )}

//                       <button
//                         onClick={fetchDatasetInfo}
//                         className="w-full py-2 bg-purple-600 hover:bg-purple-700 text-white rounded text-sm"
//                       >
//                         Refresh Dataset Info
//                       </button>
//                     </div>
//                   ) : (
//                     <div className="text-center py-8">
//                       <p className="text-gray-400 mb-3">No dataset information loaded</p>
//                       <button
//                         onClick={fetchDatasetInfo}
//                         className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded text-sm"
//                       >
//                         Load Dataset Info
//                       </button>
//                     </div>
//                   )}
//                 </div>

//                 <div className="bg-gray-700/50 rounded-lg p-5">
//                   <h3 className="text-lg text-white mb-4">Data Augmentation</h3>
//                   <p className="text-gray-400 text-sm mb-3">
//                     Training uses augmentation to improve model robustness:
//                   </p>
//                   <div className="space-y-2 text-sm">
//                     <div className="flex items-start gap-2 text-gray-300">
//                       <span className="text-purple-400">•</span>
//                       <span>Random rotation up to 20 degrees</span>
//                     </div>
//                     <div className="flex items-start gap-2 text-gray-300">
//                       <span className="text-purple-400">•</span>
//                       <span>Width and height shifts up to 20%</span>
//                     </div>
//                     <div className="flex items-start gap-2 text-gray-300">
//                       <span className="text-purple-400">•</span>
//                       <span>Random horizontal flips</span>
//                     </div>
//                     <div className="flex items-start gap-2 text-gray-300">
//                       <span className="text-purple-400">•</span>
//                       <span>Shear transformations</span>
//                     </div>
//                     <div className="flex items-start gap-2 text-gray-300">
//                       <span className="text-purple-400">•</span>
//                       <span>Random zoom up to 20%</span>
//                     </div>
//                   </div>
//                 </div>

//                 <div className="bg-gradient-to-r from-purple-900/50 to-pink-900/50 rounded-lg p-5 border border-purple-500">
//                   <h3 className="text-lg text-white mb-3">🚀 Quick Start Guide</h3>
//                   <ol className="space-y-2 text-sm text-gray-300">
//                     <li className="flex items-start gap-2">
//                       <span className="text-purple-400 font-bold">1.</span>
//                       <span>Create a model with your preferred architecture</span>
//                     </li>
//                     <li className="flex items-start gap-2">
//                       <span className="text-purple-400 font-bold">2.</span>
//                       <span>Train the model on the dataset (10-20 epochs recommended)</span>
//                     </li>
//                     <li className="flex items-start gap-2">
//                       <span className="text-purple-400 font-bold">3.</span>
//                       <span>Upload images to get predictions</span>
//                     </li>
//                     <li className="flex items-start gap-2">
//                       <span className="text-purple-400 font-bold">4.</span>
//                       <span>Check history to review past predictions</span>
//                     </li>
//                   </ol>
//                   <button
//                     onClick={() => setActiveTab('model')}
//                     className="mt-4 w-full px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded transition-colors"
//                   >
//                     Get Started
//                   </button>
//                 </div>
//               </div>
//             </div>

//             <div className="mt-8 bg-gray-700/30 rounded-lg p-5 border border-gray-600">
//               <h3 className="text-lg text-white mb-3">📚 CNN Concepts</h3>
//               <div className="grid md:grid-cols-2 gap-4 text-sm">
//                 <div className="space-y-2">
//                   <h4 className="text-purple-400 font-medium">Convolution</h4>
//                   <p className="text-gray-400">
//                     Filters slide across the input image to detect patterns like edges, textures, and shapes.
//                   </p>
//                 </div>
//                 <div className="space-y-2">
//                   <h4 className="text-purple-400 font-medium">Pooling</h4>
//                   <p className="text-gray-400">
//                     Reduces spatial dimensions while retaining important features, making the model more efficient.
//                   </p>
//                 </div>
//                 <div className="space-y-2">
//                   <h4 className="text-purple-400 font-medium">Dropout</h4>
//                   <p className="text-gray-400">
//                     Randomly disables neurons during training to prevent overfitting and improve generalization.
//                   </p>
//                 </div>
//                 <div className="space-y-2">
//                   <h4 className="text-purple-400 font-medium">Binary Classification</h4>
//                   <p className="text-gray-400">
//                     Output layer with sigmoid activation produces a probability between 0 (cat) and 1 (dog).
//                   </p>
//                 </div>
//               </div>
//             </div>
//           </div>
//         )}
//       </div>
//     </div>
//   );
// };

// export default CNNImageClassifier;




'use client';
import React, { useState, useEffect, useRef } from 'react';
import { Camera, Upload, Brain, Activity, Trash2, Clock, CheckCircle, Info } from 'lucide-react';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import AxiosInstance from "@/components/AxiosInstance";

const CNNImageClassifier = () => {
  const [activeTab, setActiveTab] = useState('predict');
  const [isLoading, setIsLoading] = useState(false);
  const [modelStatus, setModelStatus] = useState(null);
  const fileInputRef = useRef(null);

  const [modelConfig, setModelConfig] = useState({
    model_type: 'simple',
    target_size: [150, 150],
    batch_size: 32
  });

  const [trainingConfig, setTrainingConfig] = useState({
    epochs: 10,
    batch_size: 32
  });
  const [trainingResults, setTrainingResults] = useState(null);

  const [selectedImage, setSelectedImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [predictionResult, setPredictionResult] = useState(null);
  const [predictionHistory, setPredictionHistory] = useState([]);
  const [datasetInfo, setDatasetInfo] = useState(null);

  const architectures = [
    {
      name: 'simple',
      title: 'Simple CNN',
      description: 'Fast and lightweight - 3 convolutional layers',
      features: ['Quick training', 'Good for learning', 'Lower accuracy'],
      icon: '🚀'
    },
    {
      name: 'vgg',
      title: 'VGG-Style',
      description: 'Deeper architecture - Better accuracy',
      features: ['4 Conv blocks', 'Higher accuracy', 'Slower training'],
      icon: '🎯'
    },
    {
      name: 'resnet',
      title: 'ResNet-Inspired',
      description: 'State-of-the-art - Best performance',
      features: ['Skip connections', 'Best accuracy', 'Production ready'],
      icon: '⭐'
    }
  ];

  useEffect(() => {
    checkModelStatus();
  }, []);

  const checkModelStatus = async () => {
    try {
      const response = await AxiosInstance.get('/api/cnn/health');
      setModelStatus(response.data);
    } catch (error) {
      console.error('Error checking model status:', error);
      toast.error('Failed to check model status');
    }
  };

  const handleCreateModel = async () => {
    setIsLoading(true);
    try {
      const response = await AxiosInstance.post('/api/cnn/model/create', modelConfig);
      toast.success('Model created successfully!');
      await checkModelStatus();
      await fetchDatasetInfo();
    } catch (error) {
      console.error('Model creation error:', error);
      toast.error(error.response?.data?.detail || 'Model creation failed');
    } finally {
      setIsLoading(false);
    }
  };

  const handleTrainModel = async () => {
    setIsLoading(true);
    setTrainingResults(null);
    
    try {
      const response = await AxiosInstance.post('/api/cnn/model/train', trainingConfig);
      setTrainingResults(response.data.data);
      toast.success('Training completed successfully!');
      await checkModelStatus();
    } catch (error) {
      console.error('Training error:', error);
      toast.error(error.response?.data?.detail || 'Training failed');
    } finally {
      setIsLoading(false);
    }
  };

  const handleEvaluateModel = async () => {
    setIsLoading(true);
    try {
      const response = await AxiosInstance.post('/api/cnn/model/evaluate');
      setTrainingResults(prev => ({ ...prev, ...response.data.data }));
      toast.success('Evaluation completed!');
    } catch (error) {
      console.error('Evaluation error:', error);
      toast.error(error.response?.data?.detail || 'Evaluation failed');
    } finally {
      setIsLoading(false);
    }
  };

  const handleImageSelect = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedImage(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handlePredict = async () => {
    if (!selectedImage) {
      toast.warning('Please select an image first');
      return;
    }

    setIsLoading(true);
    try {
      const formData = new FormData();
      formData.append('file', selectedImage, selectedImage.name);

      console.log('=== PREDICTION REQUEST DEBUG ===');
      console.log('File:', selectedImage.name, 'Size:', selectedImage.size, 'Type:', selectedImage.type);

      const response = await AxiosInstance.post('/api/cnn/predict/image', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      console.log('=== RESPONSE DEBUG ===');
      console.log('Status:', response.status);
      console.log('Response Data:', response.data);
      
      let predictionData = null;
      
      // Case 1: Backend format - response.data.data.predicted_class
      if (response.data?.data?.predicted_class) {
        console.log('✓ Found backend structure: response.data.data.predicted_class');
        const rawData = response.data.data;
        
        // Transform backend format to frontend format
        predictionData = {
          prediction: rawData.predicted_class.toLowerCase(), // "Dogs" -> "dog", "Cats" -> "cats"
          confidence: rawData.confidence,
          probabilities: {
            cat: rawData.probabilities?.Cats || 0,
            dog: rawData.probabilities?.Dogs || 0
          },
          raw_prediction: rawData.raw_prediction
        };
      }
      // Case 2: response.data.data.prediction (nested structure)
      else if (response.data?.data?.prediction) {
        console.log('✓ Found nested structure: response.data.data.prediction');
        predictionData = response.data.data;
      }
      // Case 3: response.data.prediction (direct structure)
      else if (response.data?.prediction) {
        console.log('✓ Found direct structure: response.data.prediction');
        predictionData = response.data;
      }
      // Case 4: Empty or invalid response
      else {
        console.error('✗ Invalid response structure detected');
        console.error('Response.data:', JSON.stringify(response.data, null, 2));
        toast.error('Backend returned unexpected response format. Check console.', {
          autoClose: 5000
        });
        setPredictionResult(null);
        setIsLoading(false);
        return;
      }
      
      // Validate prediction data
      if (!predictionData.prediction || predictionData.confidence === undefined) {
        console.error('✗ Missing required fields in prediction data');
        console.error('Prediction Data:', predictionData);
        toast.error('Incomplete prediction data received');
        setPredictionResult(null);
        setIsLoading(false);
        return;
      }
      
      console.log('✓ SUCCESS - Valid prediction received');
      console.log('Prediction:', predictionData.prediction);
      console.log('Confidence:', predictionData.confidence);
      
      // Success - set prediction result
      setPredictionResult(predictionData);
      
      const newPrediction = {
        id: Date.now(),
        timestamp: new Date().toLocaleString(),
        prediction: predictionData.prediction,
        confidence: predictionData.confidence,
        probabilities: predictionData.probabilities,
        image: imagePreview
      };
      
      const newHistory = [newPrediction, ...predictionHistory.slice(0, 19)];
      setPredictionHistory(newHistory);
      
      toast.success('Prediction completed!');
      
    } catch (error) {
      console.error('=== PREDICTION ERROR ===');
      console.error('Error:', error);
      
      if (error.response) {
        console.error('Response Status:', error.response.status);
        console.error('Response Data:', error.response.data);
        toast.error(error.response.data?.detail || `Server Error: ${error.response.status}`);
      } else if (error.request) {
        console.error('No response received');
        toast.error('No response from server. Is the backend running?');
      } else {
        toast.error(error.message || 'Prediction failed');
      }
      
      setPredictionResult(null);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchDatasetInfo = async () => {
    try {
      const response = await AxiosInstance.get('/api/cnn/dataset/info');
      setDatasetInfo(response.data.data);
    } catch (error) {
      console.error('Error fetching dataset info:', error);
      toast.error('Failed to fetch dataset info');
    }
  };

  const clearHistory = () => {
    setPredictionHistory([]);
    toast.info('History cleared');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-900 py-8 px-4">
      <ToastContainer position="top-right" autoClose={3000} theme="dark" />
      
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-5xl font-bold text-white mb-3 flex items-center justify-center gap-3">
            <Brain className="w-12 h-12" />
            CNN IMAGE CLASSIFIER
          </h1>
          <div className="w-32 h-1 bg-gradient-to-r from-pink-500 to-purple-500 mx-auto mb-4"></div>
          <p className="text-gray-200 max-w-2xl mx-auto text-lg">
            Deep Learning powered Cat vs Dog image classification. Train custom models and get real-time predictions.
          </p>
        </div>

        {modelStatus && (
          <div className="bg-gray-800/50 backdrop-blur rounded-xl p-4 mb-6 border border-purple-500/30">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <div className="flex items-center gap-3">
                <Activity className="w-5 h-5 text-purple-400" />
                <span className="text-gray-300">Model Status:</span>
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                  modelStatus.model_status === 'loaded' 
                    ? 'bg-green-500/20 text-green-400' 
                    : 'bg-yellow-500/20 text-yellow-400'
                }`}>
                  {modelStatus.model_status || 'Not initialized'}
                </span>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-gray-300">Training:</span>
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                  modelStatus.training_status === 'trained'
                    ? 'bg-green-500/20 text-green-400'
                    : 'bg-gray-500/20 text-gray-400'
                }`}>
                  {modelStatus.training_status || 'Not trained'}
                </span>
              </div>
              <button
                onClick={checkModelStatus}
                className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-sm transition-colors"
              >
                Refresh Status
              </button>
            </div>
          </div>
        )}

        <div className="flex flex-wrap gap-2 mb-8 bg-gray-800/30 backdrop-blur p-2 rounded-xl">
          {[
            { id: 'predict', label: 'Predict', icon: <Camera className="w-4 h-4" /> },
            { id: 'model', label: 'Create Model', icon: <Brain className="w-4 h-4" /> },
            { id: 'train', label: 'Train', icon: <Activity className="w-4 h-4" /> },
            { id: 'history', label: 'History', icon: <Clock className="w-4 h-4" /> },
            { id: 'info', label: 'Info', icon: <Info className="w-4 h-4" /> }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${
                activeTab === tab.id
                  ? 'bg-purple-600 text-white shadow-lg shadow-purple-500/50'
                  : 'text-gray-300 hover:bg-gray-700 hover:text-white'
              }`}
            >
              {tab.icon}
              <span className="hidden sm:inline">{tab.label}</span>
            </button>
          ))}
        </div>

        {activeTab === 'predict' && (
          <div className="bg-gray-800/50 backdrop-blur rounded-xl p-6 shadow-2xl border border-purple-500/30">
            <h2 className="text-2xl text-white mb-6 flex items-center gap-2">
              <Camera className="w-6 h-6" />
              Image Prediction
            </h2>

            <div className="grid md:grid-cols-2 gap-8">
              <div className="space-y-6">
                <div
                  onClick={() => fileInputRef.current?.click()}
                  className="border-2 border-dashed border-purple-500/50 rounded-xl p-8 text-center cursor-pointer hover:border-purple-500 hover:bg-purple-500/5 transition-all"
                >
                  {imagePreview ? (
                    <img src={imagePreview} alt="Preview" className="max-h-64 mx-auto rounded-lg" />
                  ) : (
                    <div className="space-y-4">
                      <Upload className="w-16 h-16 mx-auto text-purple-400" />
                      <div>
                        <p className="text-white text-lg">Click to upload image</p>
                        <p className="text-gray-400 text-sm mt-2">JPG, PNG, or GIF (max 10MB)</p>
                      </div>
                    </div>
                  )}
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/*"
                    onChange={handleImageSelect}
                    className="hidden"
                  />
                </div>

                {selectedImage && (
                  <div className="space-y-3">
                    <button
                      onClick={handlePredict}
                      disabled={isLoading}
                      className="w-full py-3 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 disabled:from-gray-600 disabled:to-gray-600 disabled:cursor-not-allowed text-white rounded-lg transition-all flex items-center justify-center gap-2 font-medium"
                    >
                      {isLoading ? (
                        <>
                          <div className="animate-spin rounded-full h-5 w-5 border-t-2 border-b-2 border-white"></div>
                          Predicting...
                        </>
                      ) : (
                        <>
                          <Brain className="w-5 h-5" />
                          Classify Image
                        </>
                      )}
                    </button>
                    
                    <button
                      onClick={() => {
                        setSelectedImage(null);
                        setImagePreview(null);
                        setPredictionResult(null);
                      }}
                      className="w-full py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors"
                    >
                      Clear Image
                    </button>
                  </div>
                )}
              </div>

              <div className="space-y-6">
                {predictionResult ? (
                  <div className="bg-gradient-to-r from-purple-900/50 to-pink-900/50 rounded-xl p-6 border border-purple-500">
                    <h3 className="text-xl text-white mb-4 flex items-center gap-2">
                      {predictionResult.prediction === 'dog' || predictionResult.prediction === 'dogs' ? '🐕' : '🐱'}
                      Prediction Result
                    </h3>

                    <div className="text-center mb-6">
                      <div className="text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-400 mb-2">
                        {predictionResult?.prediction?.toUpperCase() || 'UNKNOWN'}
                      </div>
                      <div className="text-gray-300">
                        Confidence: {predictionResult?.confidence ? (predictionResult.confidence * 100).toFixed(2) : '0.00'}%
                      </div>
                    </div>

                    <div className="space-y-3">
                      <div className="bg-gray-800/50 rounded-lg p-3">
                        <div className="text-sm text-gray-400 mb-2">Confidence Score</div>
                        <div className="w-full bg-gray-700 rounded-full h-3">
                          <div
                            className="bg-gradient-to-r from-purple-500 to-pink-500 h-3 rounded-full transition-all duration-500"
                            style={{ width: `${(predictionResult?.confidence || 0) * 100}%` }}
                          ></div>
                        </div>
                      </div>

                      {predictionResult.probabilities && (
                        <div className="bg-gray-800/50 rounded-lg p-3 space-y-2">
                          <div className="text-sm text-gray-400 mb-2">Class Probabilities</div>
                          <div className="flex justify-between text-sm">
                            <span className="text-gray-300">Cat:</span>
                            <span className="text-white">
                              {((predictionResult.probabilities.cat || 0) * 100).toFixed(2)}%
                            </span>
                          </div>
                          <div className="flex justify-between text-sm">
                            <span className="text-gray-300">Dog:</span>
                            <span className="text-white">
                              {((predictionResult.probabilities.dog || 0) * 100).toFixed(2)}%
                            </span>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                ) : (
                  <div className="bg-gray-700/50 rounded-xl p-6 text-center">
                    <div className="text-6xl mb-4">🖼️</div>
                    <p className="text-gray-400">Upload an image to get started</p>
                    <p className="text-gray-500 text-sm mt-2">The model will classify it as Cat or Dog</p>
                  </div>
                )}

                <div className="bg-gray-700/50 rounded-lg p-4">
                  <h4 className="text-white mb-3 font-medium">💡 Tips</h4>
                  <ul className="text-gray-300 text-sm space-y-2">
                    <li>• Use clear, well-lit images</li>
                    <li>• Single animal per image works best</li>
                    <li>• Front-facing angles improve accuracy</li>
                    <li>• Avoid heavily filtered images</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'model' && (
          <div className="bg-gray-800/50 backdrop-blur rounded-xl p-6 shadow-2xl border border-purple-500/30">
            <h2 className="text-2xl text-white mb-6 flex items-center gap-2">
              <Brain className="w-6 h-6" />
              Create CNN Model
            </h2>

            <div className="grid md:grid-cols-3 gap-6 mb-8">
              {architectures.map((arch) => (
                <div
                  key={arch.name}
                  onClick={() => setModelConfig({ ...modelConfig, model_type: arch.name })}
                  className={`cursor-pointer rounded-xl p-6 border-2 transition-all ${
                    modelConfig.model_type === arch.name
                      ? 'border-purple-500 bg-purple-500/10'
                      : 'border-gray-600 hover:border-gray-500'
                  }`}
                >
                  <div className="text-4xl mb-3">{arch.icon}</div>
                  <h3 className="text-xl text-white mb-2">{arch.title}</h3>
                  <p className="text-gray-400 text-sm mb-4">{arch.description}</p>
                  <div className="space-y-1">
                    {arch.features.map((feature, idx) => (
                      <div key={idx} className="text-gray-300 text-xs flex items-center gap-2">
                        <CheckCircle className="w-3 h-3 text-green-400" />
                        {feature}
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>

            <div className="grid md:grid-cols-2 gap-6 mb-6">
              <div>
                <label className="block text-gray-300 mb-2">Image Size (Width × Height)</label>
                <select
                  value={JSON.stringify(modelConfig.target_size)}
                  onChange={(e) => setModelConfig({ ...modelConfig, target_size: JSON.parse(e.target.value) })}
                  className="w-full p-3 bg-gray-700 rounded-lg text-white focus:ring-2 focus:ring-purple-500 focus:outline-none"
                >
                  <option value="[150,150]">150 × 150 (Fast)</option>
                  <option value="[224,224]">224 × 224 (Balanced)</option>
                  <option value="[299,299]">299 × 299 (High Quality)</option>
                </select>
              </div>

              <div>
                <label className="block text-gray-300 mb-2">Batch Size</label>
                <select
                  value={modelConfig.batch_size}
                  onChange={(e) => setModelConfig({ ...modelConfig, batch_size: parseInt(e.target.value) })}
                  className="w-full p-3 bg-gray-700 rounded-lg text-white focus:ring-2 focus:ring-purple-500 focus:outline-none"
                >
                  <option value="16">16 (Small GPU)</option>
                  <option value="32">32 (Standard)</option>
                  <option value="64">64 (Large GPU)</option>
                </select>
              </div>
            </div>

            <button
              onClick={handleCreateModel}
              disabled={isLoading}
              className="w-full py-3 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 disabled:from-gray-600 disabled:to-gray-600 disabled:cursor-not-allowed text-white rounded-lg transition-all flex items-center justify-center gap-2 font-medium text-lg"
            >
              {isLoading ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-t-2 border-b-2 border-white"></div>
                  Creating Model...
                </>
              ) : (
                <>
                  <Brain className="w-5 h-5" />
                  Create Model
                </>
              )}
            </button>
          </div>
        )}

        {activeTab === 'train' && (
          <div className="bg-gray-800/50 backdrop-blur rounded-xl p-6 shadow-2xl border border-purple-500/30">
            <h2 className="text-2xl text-white mb-6 flex items-center gap-2">
              <Activity className="w-6 h-6" />
              Train Model
            </h2>

            <div className="grid md:grid-cols-2 gap-8">
              <div className="space-y-6">
                <div>
                  <label className="block text-gray-300 mb-2">Number of Epochs</label>
                  <input
                    type="number"
                    min="1"
                    max="100"
                    value={trainingConfig.epochs}
                    onChange={(e) => setTrainingConfig({ ...trainingConfig, epochs: parseInt(e.target.value) })}
                    className="w-full p-3 bg-gray-700 rounded-lg text-white focus:ring-2 focus:ring-purple-500 focus:outline-none"
                  />
                  <p className="text-gray-400 text-sm mt-1">Recommended: 10-20 epochs</p>
                </div>

                <div>
                  <label className="block text-gray-300 mb-2">Batch Size</label>
                  <select
                    value={trainingConfig.batch_size}
                    onChange={(e) => setTrainingConfig({ ...trainingConfig, batch_size: parseInt(e.target.value) })}
                    className="w-full p-3 bg-gray-700 rounded-lg text-white focus:ring-2 focus:ring-purple-500 focus:outline-none"
                  >
                    <option value="16">16</option>
                    <option value="32">32</option>
                    <option value="64">64</option>
                  </select>
                </div>

                <button
                  onClick={handleTrainModel}
                  disabled={isLoading || modelStatus?.model_status !== 'loaded'}
                  className="w-full py-3 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 disabled:from-gray-600 disabled:to-gray-600 disabled:cursor-not-allowed text-white rounded-lg transition-all flex items-center justify-center gap-2 font-medium"
                >
                  {isLoading ? (
                    <>
                      <div className="animate-spin rounded-full h-5 w-5 border-t-2 border-b-2 border-white"></div>
                      Training...
                    </>
                  ) : (
                    <>
                      <Activity className="w-5 h-5" />
                      Start Training
                    </>
                  )}
                </button>

                {modelStatus?.training_status === 'trained' && (
                  <button
                    onClick={handleEvaluateModel}
                    disabled={isLoading}
                    className="w-full py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded-lg transition-colors flex items-center justify-center gap-2"
                  >
                    Evaluate on Test Set
                  </button>
                )}
              </div>

              <div>
                {trainingResults ? (
                  <div className="bg-gradient-to-r from-green-900/50 to-emerald-900/50 rounded-xl p-6 border border-green-500">
                    <h3 className="text-xl text-white mb-4">Training Results</h3>
                    
                    <div className="space-y-4">
                      {trainingResults.final_accuracy && (
                        <div className="bg-gray-800/50 rounded-lg p-4">
                          <div className="text-sm text-gray-400 mb-2">Training Accuracy</div>
                          <div className="text-3xl font-bold text-green-400">
                            {(trainingResults.final_accuracy * 100).toFixed(2)}%
                          </div>
                        </div>
                      )}

                      {trainingResults.validation_accuracy && (
                        <div className="bg-gray-800/50 rounded-lg p-4">
                          <div className="text-sm text-gray-400 mb-2">Validation Accuracy</div>
                          <div className="text-3xl font-bold text-blue-400">
                            {(trainingResults.validation_accuracy * 100).toFixed(2)}%
                          </div>
                        </div>
                      )}

                      {trainingResults.test_accuracy && (
                        <div className="bg-gray-800/50 rounded-lg p-4">
                          <div className="text-sm text-gray-400 mb-2">Test Accuracy</div>
                          <div className="text-3xl font-bold text-purple-400">
                            {(trainingResults.test_accuracy * 100).toFixed(2)}%
                          </div>
                        </div>
                      )}

                      {trainingResults.training_time && (
                        <div className="text-gray-300 text-sm">
                          Training time: {trainingResults.training_time}
                        </div>
                      )}
                    </div>
                  </div>
                ) : (
                  <div className="bg-gray-700/50 rounded-xl p-6 text-center">
                    <Activity className="w-16 h-16 mx-auto text-gray-500 mb-4" />
                    <p className="text-gray-400">No training results yet</p>
                    <p className="text-gray-500 text-sm mt-2">Train the model to see results</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'history' && (
          <div className="bg-gray-800/50 backdrop-blur rounded-xl p-6 shadow-2xl border border-purple-500/30">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl text-white flex items-center gap-2">
                <Clock className="w-6 h-6" />
                Prediction History
              </h2>
              {predictionHistory.length > 0 && (
                <button
                  onClick={clearHistory}
                  className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg text-sm flex items-center gap-2"
                >
                  <Trash2 className="w-4 h-4" />
                  Clear History
                </button>
              )}
            </div>

            {predictionHistory.length > 0 ? (
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                {predictionHistory.map((item) => (
                  <div key={item.id} className="bg-gray-700/50 rounded-lg overflow-hidden border border-gray-600">
                    <img src={item.image} alt="Prediction" className="w-full h-48 object-cover" />
                    <div className="p-4">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-2xl">
                          {item.prediction === 'dog' || item.prediction === 'dogs' ? '🐕' : '🐱'}
                        </span>
                        <span className="text-xl font-bold text-purple-400">
                          {item.prediction?.toUpperCase() || 'UNKNOWN'}
                        </span>
                      </div>
                      <div className="text-sm text-gray-400 mb-2">
                        Confidence: {item.confidence ? (item.confidence * 100).toFixed(2) : '0.00'}%
                      </div>
                      <div className="text-xs text-gray-500">{item.timestamp}</div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center text-gray-400 py-12">
                <Clock className="w-16 h-16 mx-auto text-gray-500 mb-4" />
                <p className="text-xl">No predictions yet</p>
                <p className="text-gray-500 text-sm mt-2">Upload and classify images to see your history</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'info' && (
          <div className="bg-gray-800/50 backdrop-blur rounded-xl p-6 shadow-2xl border border-purple-500/30">
            <h2 className="text-2xl text-white mb-6 flex items-center gap-2">
              <Info className="w-6 h-6" />
              Model Information & Dataset
            </h2>

            <div className="grid md:grid-cols-2 gap-8">
              <div className="space-y-6">
                <div className="bg-gray-700/50 rounded-lg p-5">
                  <h3 className="text-lg text-white mb-4 flex items-center gap-2">
                    <Brain className="w-5 h-5" />
                    Model Details
                  </h3>
                  <div className="space-y-3 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-300">Framework:</span>
                      <span className="text-purple-400">TensorFlow/Keras</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-300">Task:</span>
                      <span className="text-purple-400">Binary Classification</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-300">Output:</span>
                      <span className="text-purple-400">Cat vs Dog</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-300">API:</span>
                      <span className="text-purple-400">FastAPI</span>
                    </div>
                  </div>
                </div>

                <div className="bg-gray-700/50 rounded-lg p-5">
                  <h3 className="text-lg text-white mb-4">Architecture Options</h3>
                  <div className="space-y-3">
                    {architectures.map((arch) => (
                      <div key={arch.name} className="border-l-4 border-purple-500 pl-3">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-xl">{arch.icon}</span>
                          <span className="text-white font-medium">{arch.title}</span>
                        </div>
                        <p className="text-gray-400 text-sm">{arch.description}</p>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="bg-gray-700/50 rounded-lg p-5">
                  <h3 className="text-lg text-white mb-4">Key Features</h3>
                  <div className="space-y-2 text-sm">
                    <div className="flex items-center gap-2 text-gray-300">
                      <CheckCircle className="w-4 h-4 text-green-400" />
                      Convolutional layers for feature extraction
                    </div>
                    <div className="flex items-center gap-2 text-gray-300">
                      <CheckCircle className="w-4 h-4 text-green-400" />
                      Max pooling for dimensionality reduction
                    </div>
                    <div className="flex items-center gap-2 text-gray-300">
                      <CheckCircle className="w-4 h-4 text-green-400" />
                      Dropout for regularization
                    </div>
                    <div className="flex items-center gap-2 text-gray-300">
                      <CheckCircle className="w-4 h-4 text-green-400" />
                      Data augmentation for better generalization
                    </div>
                    <div className="flex items-center gap-2 text-gray-300">
                      <CheckCircle className="w-4 h-4 text-green-400" />
                      Binary crossentropy loss function
                    </div>
                  </div>
                </div>
              </div>

              <div className="space-y-6">
                <div className="bg-gray-700/50 rounded-lg p-5">
                  <h3 className="text-lg text-white mb-4">Dataset Information</h3>
                  {datasetInfo ? (
                    <div className="space-y-4">
                      <div className="text-sm">
                        <div className="text-gray-400 mb-2">Total Images:</div>
                        <div className="text-2xl font-bold text-purple-400">
                          {datasetInfo.total_images?.toLocaleString() || 'N/A'}
                        </div>
                      </div>

                      {datasetInfo.folders && (
                        <div className="space-y-3">
                          {Object.entries(datasetInfo.folders).map(([folder, info]) => (
                            <div key={folder} className="bg-gray-800/50 rounded p-3">
                              <div className="font-medium text-white mb-2 capitalize">{folder}</div>
                              {info.subfolders && (
                                <div className="grid grid-cols-2 gap-2 text-sm">
                                  {Object.entries(info.subfolders).map(([subfolder, count]) => (
                                    <div key={subfolder} className="flex justify-between">
                                      <span className="text-gray-400 capitalize">{subfolder}:</span>
                                      <span className="text-purple-400">{count}</span>
                                    </div>
                                  ))}
                                </div>
                              )}
                            </div>
                          ))}
                        </div>
                      )}

                      <button
                        onClick={fetchDatasetInfo}
                        className="w-full py-2 bg-purple-600 hover:bg-purple-700 text-white rounded text-sm"
                      >
                        Refresh Dataset Info
                      </button>
                    </div>
                  ) : (
                    <div className="text-center py-8">
                      <p className="text-gray-400 mb-3">No dataset information loaded</p>
                      <button
                        onClick={fetchDatasetInfo}
                        className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded text-sm"
                      >
                        Load Dataset Info
                      </button>
                    </div>
                  )}
                </div>

                <div className="bg-gray-700/50 rounded-lg p-5">
                  <h3 className="text-lg text-white mb-4">Data Augmentation</h3>
                  <p className="text-gray-400 text-sm mb-3">
                    Training uses augmentation to improve model robustness:
                  </p>
                  <div className="space-y-2 text-sm">
                    <div className="flex items-start gap-2 text-gray-300">
                      <span className="text-purple-400">•</span>
                      <span>Random rotation up to 20 degrees</span>
                    </div>
                    <div className="flex items-start gap-2 text-gray-300">
                      <span className="text-purple-400">•</span>
                      <span>Width and height shifts up to 20%</span>
                    </div>
                    <div className="flex items-start gap-2 text-gray-300">
                      <span className="text-purple-400">•</span>
                      <span>Random horizontal flips</span>
                    </div>
                    <div className="flex items-start gap-2 text-gray-300">
                      <span className="text-purple-400">•</span>
                      <span>Shear transformations</span>
                    </div>
                    <div className="flex items-start gap-2 text-gray-300">
                      <span className="text-purple-400">•</span>
                      <span>Random zoom up to 20%</span>
                    </div>
                  </div>
                </div>

                <div className="bg-gradient-to-r from-purple-900/50 to-pink-900/50 rounded-lg p-5 border border-purple-500">
                  <h3 className="text-lg text-white mb-3">🚀 Quick Start Guide</h3>
                  <ol className="space-y-2 text-sm text-gray-300">
                    <li className="flex items-start gap-2">
                      <span className="text-purple-400 font-bold">1.</span>
                      <span>Create a model with your preferred architecture</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-purple-400 font-bold">2.</span>
                      <span>Train the model on the dataset (10-20 epochs recommended)</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-purple-400 font-bold">3.</span>
                      <span>Upload images to get predictions</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-purple-400 font-bold">4.</span>
                      <span>Check history to review past predictions</span>
                    </li>
                  </ol>
                  <button
                    onClick={() => setActiveTab('model')}
                    className="mt-4 w-full px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded transition-colors"
                  >
                    Get Started
                  </button>
                </div>
              </div>
            </div>

            <div className="mt-8 bg-gray-700/30 rounded-lg p-5 border border-gray-600">
              <h3 className="text-lg text-white mb-3">📚 CNN Concepts</h3>
              <div className="grid md:grid-cols-2 gap-4 text-sm">
                <div className="space-y-2">
                  <h4 className="text-purple-400 font-medium">Convolution</h4>
                  <p className="text-gray-400">
                    Filters slide across the input image to detect patterns like edges, textures, and shapes.
                  </p>
                </div>
                <div className="space-y-2">
                  <h4 className="text-purple-400 font-medium">Pooling</h4>
                  <p className="text-gray-400">
                    Reduces spatial dimensions while retaining important features, making the model more efficient.
                  </p>
                </div>
                <div className="space-y-2">
                  <h4 className="text-purple-400 font-medium">Dropout</h4>
                  <p className="text-gray-400">
                    Randomly disables neurons during training to prevent overfitting and improve generalization.
                  </p>
                </div>
                <div className="space-y-2">
                  <h4 className="text-purple-400 font-medium">Binary Classification</h4>
                  <p className="text-gray-400">
                    Output layer with sigmoid activation produces a probability between 0 (cat) and 1 (dog).
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CNNImageClassifier;