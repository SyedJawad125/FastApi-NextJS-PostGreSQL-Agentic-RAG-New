'use client';
import React, { useState, useEffect } from 'react';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import AxiosInstance from "@/components/AxiosInstance";

const BertSentimentAnalysis = () => {
  const [activeTab, setActiveTab] = useState('predict');
  const [modelStatus, setModelStatus] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);

  // Training state
  const [trainingParams, setTrainingParams] = useState({
    epochs: 2,
    batch_size: 16,
    learning_rate: 0.00002,
    max_len: 256,
    sample_size: null
  });
  const [isTraining, setIsTraining] = useState(false);

  // Prediction state
  const [predictionText, setPredictionText] = useState('');
  const [predictionResult, setPredictionResult] = useState(null);
  const [predictionHistory, setPredictionHistory] = useState([]);

  // Batch prediction state
  const [batchTexts, setBatchTexts] = useState(['']);
  const [batchResults, setBatchResults] = useState([]);

  // Fetch model status on component mount and refresh
  useEffect(() => {
    fetchModelStatus();
  }, [refreshKey]);

  const fetchModelStatus = async () => {
    try {
      const response = await AxiosInstance.get('/sentiment/status');
      setModelStatus(response.data);
      setIsTraining(response.data.status === 'training');
    } catch (error) {
      console.error('Error fetching model status:', error);
      toast.error('Failed to fetch model status');
    }
  };

  const handleTraining = async () => {
    if (isTraining) {
      toast.warning('Training is already in progress');
      return;
    }

    setIsTraining(true);
    try {
      const response = await AxiosInstance.post('/sentiment/train', trainingParams);
      toast.success(response.data.message);
      
      // Poll status during training
      const pollStatus = setInterval(async () => {
        try {
          const statusResponse = await AxiosInstance.get('/sentiment/status');
          setModelStatus(statusResponse.data);
          
          if (statusResponse.data.status === 'trained') {
            setIsTraining(false);
            clearInterval(pollStatus);
            toast.success('Training completed successfully!');
            setRefreshKey(prev => prev + 1);
          } else if (statusResponse.data.status === 'error') {
            setIsTraining(false);
            clearInterval(pollStatus);
            toast.error('Training failed');
          }
        } catch (error) {
          console.error('Error polling status:', error);
        }
      }, 3000);

      // Clear interval after 10 minutes (timeout)
      setTimeout(() => {
        clearInterval(pollStatus);
        if (isTraining) {
          setIsTraining(false);
          toast.warning('Training status polling timed out');
        }
      }, 600000);

    } catch (error) {
      setIsTraining(false);
      console.error('Training error:', error);
      toast.error(error.response?.data?.detail || 'Training failed');
    }
  };

  const handlePrediction = async () => {
    if (!predictionText.trim()) {
      toast.warning('Please enter some text to analyze');
      return;
    }

    if (modelStatus?.status !== 'trained') {
      toast.error('Model is not trained yet. Please train the model first.');
      return;
    }

    setIsLoading(true);
    try {
      const response = await AxiosInstance.post('/sentiment/predict', {
        text: predictionText
      });
      
      const result = response.data;
      setPredictionResult(result);
      
      // Add to history
      setPredictionHistory(prev => [{
        id: Date.now(),
        text: predictionText,
        sentiment: result.sentiment,
        confidence: result.confidence,
        timestamp: new Date().toLocaleString()
      }, ...prev.slice(0, 9)]); // Keep last 10 predictions
      
      toast.success('Prediction completed!');
    } catch (error) {
      console.error('Prediction error:', error);
      toast.error(error.response?.data?.detail || 'Prediction failed');
    } finally {
      setIsLoading(false);
    }
  };

  const addBatchTextInput = () => {
    setBatchTexts([...batchTexts, '']);
  };

  const removeBatchTextInput = (index) => {
    const newTexts = batchTexts.filter((_, i) => i !== index);
    setBatchTexts(newTexts.length > 0 ? newTexts : ['']);
  };

  const updateBatchText = (index, value) => {
    const newTexts = [...batchTexts];
    newTexts[index] = value;
    setBatchTexts(newTexts);
  };

  const handleBatchPrediction = async () => {
    const validTexts = batchTexts.filter(text => text.trim());
    
    if (validTexts.length === 0) {
      toast.warning('Please enter at least one text to analyze');
      return;
    }

    if (modelStatus?.status !== 'trained') {
      toast.error('Model is not trained yet. Please train the model first.');
      return;
    }

    setIsLoading(true);
    try {
      const results = [];
      for (const text of validTexts) {
        const response = await AxiosInstance.post('/sentiment/predict', { text });
        results.push({
          text,
          ...response.data,
          timestamp: new Date().toLocaleString()
        });
      }
      
      setBatchResults(results);
      toast.success(`Batch prediction completed for ${results.length} texts!`);
    } catch (error) {
      console.error('Batch prediction error:', error);
      toast.error(error.response?.data?.detail || 'Batch prediction failed');
    } finally {
      setIsLoading(false);
    }
  };

  const getSentimentColor = (sentiment) => {
    return sentiment === 'positive' ? 'text-green-400' : 'text-red-400';
  };

  const getSentimentBadgeColor = (sentiment) => {
    return sentiment === 'positive' 
      ? 'bg-green-900/30 text-green-400 border-green-400' 
      : 'bg-red-900/30 text-red-400 border-red-400';
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 to-gray-800 py-12 px-4">
      <ToastContainer position="top-right" autoClose={3000} theme="dark" />
      
      <div className="max-w-7xl mx-auto">
        {/* Header Section */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-light text-white mb-2">BERT SENTIMENT ANALYSIS</h1>
          <div className="w-24 h-1 bg-gradient-to-r from-blue-400 to-purple-600 mx-auto mb-4"></div>
          <p className="text-gray-300 max-w-2xl mx-auto">
            Advanced sentiment analysis using BERT transformer model. Train your model, analyze text sentiment, and get confidence scores.
          </p>
        </div>

        {/* Status Card */}
        <div className="bg-gray-800/50 rounded-xl p-6 mb-8 border border-gray-700">
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
            <div>
              <h3 className="text-xl text-white font-medium mb-2">Model Status</h3>
              <div className="flex items-center gap-3">
                <span className={`px-3 py-1 rounded-full text-sm font-medium border ${
                  modelStatus?.status === 'trained' ? 'bg-green-900/30 text-green-400 border-green-400' :
                  modelStatus?.status === 'training' ? 'bg-yellow-900/30 text-yellow-400 border-yellow-400' :
                  modelStatus?.status === 'error' ? 'bg-red-900/30 text-red-400 border-red-400' :
                  'bg-gray-700 text-gray-400 border-gray-600'
                }`}>
                  {modelStatus?.status || 'Unknown'}
                </span>
                {isTraining && (
                  <div className="flex items-center gap-2 text-yellow-400">
                    <div className="animate-spin rounded-full h-4 w-4 border-t-2 border-b-2 border-yellow-400"></div>
                    <span className="text-sm">Training in progress...</span>
                  </div>
                )}
              </div>
            </div>
            
            {modelStatus?.metrics && (
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div className="text-center">
                  <div className="text-gray-400">Train Accuracy</div>
                  <div className="text-blue-400 font-medium">
                    {(modelStatus.metrics.train_accuracy * 100).toFixed(1)}%
                  </div>
                </div>
                <div className="text-center">
                  <div className="text-gray-400">Val Accuracy</div>
                  <div className="text-purple-400 font-medium">
                    {(modelStatus.metrics.val_accuracy * 100).toFixed(1)}%
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="flex flex-wrap gap-2 mb-8 bg-gray-800/30 p-2 rounded-xl">
          {[
            { id: 'predict', label: 'Single Prediction', icon: '🔍' },
            { id: 'batch', label: 'Batch Analysis', icon: '📊' },
            { id: 'train', label: 'Model Training', icon: '🧠' },
            { id: 'history', label: 'History', icon: '📋' }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                activeTab === tab.id
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-300 hover:bg-gray-700 hover:text-white'
              }`}
            >
              <span>{tab.icon}</span>
              <span className="hidden sm:inline">{tab.label}</span>
            </button>
          ))}
        </div>

        {/* Content Sections */}
        {activeTab === 'predict' && (
          <div className="bg-gray-800 rounded-xl p-6 shadow-2xl">
            <h2 className="text-2xl text-white mb-6 flex items-center gap-2">
              <span>🔍</span> Single Text Analysis
            </h2>
            
            <div className="space-y-6">
              <div>
                <label className="block text-gray-300 mb-2">Enter text to analyze:</label>
                <textarea
                  value={predictionText}
                  onChange={(e) => setPredictionText(e.target.value)}
                  placeholder="Type your text here..."
                  className="w-full h-32 p-4 bg-gray-700 rounded-lg text-white resize-none focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  maxLength={1000}
                />
                <div className="text-right text-gray-400 text-sm mt-1">
                  {predictionText.length}/1000 characters
                </div>
              </div>

              <button
                onClick={handlePrediction}
                disabled={isLoading || !predictionText.trim()}
                className="w-full py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded-lg transition-colors flex items-center justify-center gap-2"
              >
                {isLoading ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-t-2 border-b-2 border-white"></div>
                    Analyzing...
                  </>
                ) : (
                  <>
                    <span>🎯</span> Analyze Sentiment
                  </>
                )}
              </button>

              {predictionResult && (
                <div className="bg-gray-700 rounded-lg p-6 border-l-4 border-blue-500">
                  <h3 className="text-lg text-white mb-3">Analysis Result</h3>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-gray-300">Sentiment:</span>
                      <span className={`px-3 py-1 rounded-full border text-sm font-medium ${getSentimentBadgeColor(predictionResult.sentiment)}`}>
                        {predictionResult.sentiment.toUpperCase()}
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-gray-300">Confidence:</span>
                      <span className="text-white font-medium">
                        {(predictionResult.confidence * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className="bg-gray-600 rounded-full h-2">
                      <div 
                        className={`h-2 rounded-full ${predictionResult.sentiment === 'positive' ? 'bg-green-500' : 'bg-red-500'}`}
                        style={{ width: `${predictionResult.confidence * 100}%` }}
                      ></div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'batch' && (
          <div className="bg-gray-800 rounded-xl p-6 shadow-2xl">
            <h2 className="text-2xl text-white mb-6 flex items-center gap-2">
              <span>📊</span> Batch Analysis
            </h2>
            
            <div className="space-y-6">
              <div>
                <div className="flex items-center justify-between mb-4">
                  <label className="text-gray-300">Enter multiple texts to analyze:</label>
                  <button
                    onClick={addBatchTextInput}
                    className="px-3 py-1 bg-green-600 hover:bg-green-700 text-white rounded text-sm"
                  >
                    + Add Text
                  </button>
                </div>
                
                <div className="space-y-3">
                  {batchTexts.map((text, index) => (
                    <div key={index} className="flex gap-2">
                      <textarea
                        value={text}
                        onChange={(e) => updateBatchText(index, e.target.value)}
                        placeholder={`Text ${index + 1}...`}
                        className="flex-1 h-20 p-3 bg-gray-700 rounded-lg text-white resize-none focus:ring-2 focus:ring-blue-500 focus:outline-none"
                      />
                      {batchTexts.length > 1 && (
                        <button
                          onClick={() => removeBatchTextInput(index)}
                          className="p-2 bg-red-600 hover:bg-red-700 text-white rounded-lg h-fit"
                        >
                          ✕
                        </button>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              <button
                onClick={handleBatchPrediction}
                disabled={isLoading || batchTexts.every(text => !text.trim())}
                className="w-full py-3 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded-lg transition-colors flex items-center justify-center gap-2"
              >
                {isLoading ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-t-2 border-b-2 border-white"></div>
                    Processing Batch...
                  </>
                ) : (
                  <>
                    <span>⚡</span> Analyze All Texts
                  </>
                )}
              </button>

              {batchResults.length > 0 && (
                <div className="bg-gray-700 rounded-lg p-6">
                  <h3 className="text-lg text-white mb-4">Batch Results ({batchResults.length} texts)</h3>
                  <div className="space-y-4">
                    {batchResults.map((result, index) => (
                      <div key={index} className="bg-gray-600 rounded-lg p-4">
                        <div className="flex items-start justify-between mb-2">
                          <span className="text-gray-300 text-sm">Text {index + 1}:</span>
                          <span className={`px-2 py-1 rounded text-xs border ${getSentimentBadgeColor(result.sentiment)}`}>
                            {result.sentiment} ({(result.confidence * 100).toFixed(1)}%)
                          </span>
                        </div>
                        <p className="text-white text-sm bg-gray-800 p-3 rounded">
                          {result.text.length > 150 ? result.text.substring(0, 150) + '...' : result.text}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'train' && (
          <div className="bg-gray-800 rounded-xl p-6 shadow-2xl">
            <h2 className="text-2xl text-white mb-6 flex items-center gap-2">
              <span>🧠</span> Model Training
            </h2>
            
            <div className="grid md:grid-cols-2 gap-8">
              <div className="space-y-6">
                <div>
                  <label className="block text-gray-300 mb-2">Epochs</label>
                  <input
                    type="number"
                    min="1"
                    max="10"
                    value={trainingParams.epochs}
                    onChange={(e) => setTrainingParams({...trainingParams, epochs: parseInt(e.target.value)})}
                    className="w-full p-3 bg-gray-700 rounded-lg text-white focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  />
                </div>

                <div>
                  <label className="block text-gray-300 mb-2">Batch Size</label>
                  <select
                    value={trainingParams.batch_size}
                    onChange={(e) => setTrainingParams({...trainingParams, batch_size: parseInt(e.target.value)})}
                    className="w-full p-3 bg-gray-700 rounded-lg text-white focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  >
                    <option value={8}>8</option>
                    <option value={16}>16</option>
                    <option value={32}>32</option>
                  </select>
                </div>

                <div>
                  <label className="block text-gray-300 mb-2">Learning Rate</label>
                  <select
                    value={trainingParams.learning_rate}
                    onChange={(e) => setTrainingParams({...trainingParams, learning_rate: parseFloat(e.target.value)})}
                    className="w-full p-3 bg-gray-700 rounded-lg text-white focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  >
                    <option value={0.00001}>1e-5</option>
                    <option value={0.00002}>2e-5</option>
                    <option value={0.00003}>3e-5</option>
                    <option value={0.00005}>5e-5</option>
                  </select>
                </div>

                <div>
                  <label className="block text-gray-300 mb-2">Max Length</label>
                  <select
                    value={trainingParams.max_len}
                    onChange={(e) => setTrainingParams({...trainingParams, max_len: parseInt(e.target.value)})}
                    className="w-full p-3 bg-gray-700 rounded-lg text-white focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  >
                    <option value={128}>128</option>
                    <option value={256}>256</option>
                    <option value={512}>512</option>
                  </select>
                </div>

                <div>
                  <label className="block text-gray-300 mb-2">Sample Size (optional)</label>
                  <input
                    type="number"
                    min="100"
                    max="50000"
                    value={trainingParams.sample_size || ''}
                    onChange={(e) => setTrainingParams({...trainingParams, sample_size: e.target.value ? parseInt(e.target.value) : null})}
                    placeholder="Leave empty for full dataset"
                    className="w-full p-3 bg-gray-700 rounded-lg text-white focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  />
                </div>
              </div>

              <div className="space-y-6">
                <div className="bg-gray-700 rounded-lg p-4">
                  <h3 className="text-white mb-3">Training Configuration</h3>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-300">Model:</span>
                      <span className="text-blue-400">BERT Base Uncased</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-300">Dataset:</span>
                      <span className="text-blue-400">Amazon Food Reviews</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-300">Task:</span>
                      <span className="text-blue-400">Binary Sentiment Classification</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-300">Validation Split:</span>
                      <span className="text-blue-400">10%</span>
                    </div>
                  </div>
                </div>

                {modelStatus?.metrics && (
                  <div className="bg-gray-700 rounded-lg p-4">
                    <h3 className="text-white mb-3">Last Training Metrics</h3>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-300">Train Loss:</span>
                        <span className="text-orange-400">{modelStatus.metrics.train_loss.toFixed(4)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-300">Val Loss:</span>
                        <span className="text-orange-400">{modelStatus.metrics.val_loss.toFixed(4)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-300">Epochs:</span>
                        <span className="text-blue-400">{modelStatus.metrics.epochs}</span>
                      </div>
                    </div>
                  </div>
                )}

                <button
                  onClick={handleTraining}
                  disabled={isTraining}
                  className="w-full py-3 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 disabled:from-gray-600 disabled:to-gray-600 disabled:cursor-not-allowed text-white rounded-lg transition-all duration-300 flex items-center justify-center gap-2"
                >
                  {isTraining ? (
                    <>
                      <div className="animate-spin rounded-full h-5 w-5 border-t-2 border-b-2 border-white"></div>
                      Training in Progress...
                    </>
                  ) : (
                    <>
                      <span>🚀</span> Start Training
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'history' && (
          <div className="bg-gray-800 rounded-xl p-6 shadow-2xl">
            <h2 className="text-2xl text-white mb-6 flex items-center gap-2">
              <span>📋</span> Prediction History
            </h2>
            
            {predictionHistory.length > 0 ? (
              <div className="space-y-4">
                {predictionHistory.map((prediction) => (
                  <div key={prediction.id} className="bg-gray-700 rounded-lg p-4 border-l-4 border-blue-500">
                    <div className="flex items-start justify-between mb-2">
                      <span className="text-gray-400 text-sm">{prediction.timestamp}</span>
                      <span className={`px-3 py-1 rounded-full border text-sm font-medium ${getSentimentBadgeColor(prediction.sentiment)}`}>
                        {prediction.sentiment} ({(prediction.confidence * 100).toFixed(1)}%)
                      </span>
                    </div>
                    <p className="text-white bg-gray-800 p-3 rounded">
                      {prediction.text}
                    </p>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center text-gray-400 py-12">
                <div className="text-6xl mb-4">📝</div>
                <p className="text-xl">No predictions yet</p>
                <p className="mt-2">Start analyzing text to see your prediction history</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default BertSentimentAnalysis;