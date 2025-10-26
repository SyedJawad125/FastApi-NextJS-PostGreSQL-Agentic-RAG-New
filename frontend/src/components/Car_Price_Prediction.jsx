'use client';
import React, { useState, useEffect } from 'react';
import AxiosInstance from "@/components/AxiosInstance";

const CarPricePredictor = () => {
  const [activeTab, setActiveTab] = useState('predict');
  const [isLoading, setIsLoading] = useState(false);
  const [toast, setToast] = useState(null);

  // Prediction state
  const [formData, setFormData] = useState({
    horsepower: '',
    age: '',
    mileage: ''
  });

  const [predictionResult, setPredictionResult] = useState(null);
  const [predictionHistory, setPredictionHistory] = useState([]);

  // Batch prediction state
  const [batchPredictions, setBatchPredictions] = useState([
    { horsepower: '', age: '', mileage: '' }
  ]);
  const [batchResults, setBatchResults] = useState([]);

  // Toast notification system
  const showToast = (message, type = 'info') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 3000);
  };

  // Load prediction history on component mount
  useEffect(() => {
    const savedHistory = JSON.parse(localStorage.getItem('carPricePredictions') || '[]');
    setPredictionHistory(savedHistory);
  }, []);

  // Save prediction to history
  const savePredictionToHistory = (prediction) => {
    const newHistory = [{
      id: Date.now(),
      ...prediction,
      timestamp: new Date().toLocaleString()
    }, ...predictionHistory.slice(0, 9)];
    
    setPredictionHistory(newHistory);
    localStorage.setItem('carPricePredictions', JSON.stringify(newHistory));
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const validateForm = (data) => {
    const errors = [];
    if (!data.horsepower || data.horsepower <= 0) errors.push('Valid horsepower is required');
    if (!data.age || data.age < 0) errors.push('Valid age is required');
    if (!data.mileage || data.mileage < 0) errors.push('Valid mileage is required');
    return errors;
  };

  const handlePrediction = async () => {
    const errors = validateForm(formData);
    if (errors.length > 0) {
      showToast(errors.join(', '), 'error');
      return;
    }

    setIsLoading(true);
    try {
      const requestData = {
        Horsepower: parseFloat(formData.horsepower),
        Age: parseFloat(formData.age),
        Mileage: parseFloat(formData.mileage)
      };

      const response = await AxiosInstance.post('/car-price/predict', requestData, {
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.status !== 200) {
        throw new Error(response.data.detail || 'Prediction failed');
      }

      const result = response.data;
      setPredictionResult({
        ...result,
        features_used: requestData
      });
      
      savePredictionToHistory({
        ...requestData,
        predicted_price: result.predicted_price
      });
      
      showToast('Prediction completed!', 'success');
    } catch (error) {
      console.error('Prediction error:', error);
      if (error.response) {
        showToast(error.response.data.detail || 'Prediction failed', 'error');
      } else if (error.request) {
        showToast('No response from server. Check connection.', 'error');
      } else {
        showToast(error.message || 'Prediction failed', 'error');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const addBatchPrediction = () => {
    setBatchPredictions([...batchPredictions, { 
      horsepower: '', age: '', mileage: '' 
    }]);
  };

  const removeBatchPrediction = (index) => {
    const newBatch = batchPredictions.filter((_, i) => i !== index);
    setBatchPredictions(newBatch.length > 0 ? newBatch : [{ 
      horsepower: '', age: '', mileage: '' 
    }]);
  };

  const updateBatchPrediction = (index, field, value) => {
    const newBatch = [...batchPredictions];
    newBatch[index][field] = value;
    setBatchPredictions(newBatch);
  };

  const handleBatchPrediction = async () => {
    const validPredictions = batchPredictions.filter(pred => 
      pred.horsepower && pred.age && pred.mileage
    );

    if (validPredictions.length === 0) {
      showToast('Please fill in at least one complete car prediction', 'warning');
      return;
    }

    setIsLoading(true);
    try {
      const results = [];
      for (const pred of validPredictions) {
        const requestData = {
          Horsepower: parseFloat(pred.horsepower),
          Age: parseFloat(pred.age),
          Mileage: parseFloat(pred.mileage)
        };

        const response = await AxiosInstance.post('/car-price/predict', requestData, {
          headers: {
            'Content-Type': 'application/json',
          },
        });

        if (response.status !== 200) {
          throw new Error(response.data.detail || 'Batch prediction failed');
        }

        const result = await response.data;
        results.push({
          ...requestData,
          predicted_price: result.predicted_price,
          timestamp: new Date().toLocaleString()
        });
      }
      
      setBatchResults(results);
      showToast(`Batch prediction completed for ${results.length} cars!`, 'success');
    } catch (error) {
      console.error('Batch prediction error:', error);
      if (error.response) {
        showToast(error.response.data.detail || 'Batch prediction failed', 'error');
      } else if (error.request) {
        showToast('No response from server. Check connection.', 'error');
      } else {
        showToast(error.message || 'Batch prediction failed', 'error');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(price);
  };

  const clearHistory = () => {
    setPredictionHistory([]);
    localStorage.removeItem('carPricePredictions');
    showToast('Prediction history cleared', 'info');
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 to-gray-800 py-12 px-4">
      {/* Custom Toast Notification */}
      {toast && (
        <div className="fixed top-4 right-4 z-50 animate-fade-in">
          <div className={`px-6 py-3 rounded-lg shadow-lg ${
            toast.type === 'success' ? 'bg-green-600' :
            toast.type === 'error' ? 'bg-red-600' :
            toast.type === 'warning' ? 'bg-yellow-600' :
            'bg-blue-600'
          } text-white flex items-center gap-2`}>
            <span>
              {toast.type === 'success' ? '✓' :
               toast.type === 'error' ? '✕' :
               toast.type === 'warning' ? '⚠' : 'ℹ'}
            </span>
            <span>{toast.message}</span>
          </div>
        </div>
      )}
      
      <div className="max-w-7xl mx-auto">
        {/* Header Section */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-light text-white mb-2">CAR PRICE PREDICTOR</h1>
          <div className="w-24 h-1 bg-gradient-to-r from-blue-400 to-purple-600 mx-auto mb-4"></div>
          <p className="text-gray-300 max-w-2xl mx-auto">
            Advanced machine learning model to predict car prices based on key vehicle features. 
            Get accurate price estimates for single vehicles or analyze multiple cars at once.
          </p>
        </div>

        {/* Navigation Tabs */}
        <div className="flex flex-wrap gap-2 mb-8 bg-gray-800/30 p-2 rounded-xl">
          {[
            { id: 'predict', label: 'Single Prediction', icon: '🚗' },
            { id: 'batch', label: 'Batch Analysis', icon: '🚙' },
            { id: 'history', label: 'History', icon: '📋' },
            { id: 'info', label: 'Model Info', icon: 'ℹ️' }
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

        {/* Single Prediction Tab */}
        {activeTab === 'predict' && (
          <div className="bg-gray-800 rounded-xl p-6 shadow-2xl">
            <h2 className="text-2xl text-white mb-6 flex items-center gap-2">
              <span>🚗</span> Car Price Prediction
            </h2>
            
            <div className="grid md:grid-cols-2 gap-8">
              <div className="space-y-6">
                <div>
                  <label className="block text-gray-300 mb-2">Horsepower</label>
                  <input
                    type="number"
                    min="50"
                    value={formData.horsepower}
                    onChange={(e) => handleInputChange('horsepower', e.target.value)}
                    placeholder="e.g., 200"
                    className="w-full p-3 bg-gray-700 rounded-lg text-white focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  />
                  <p className="text-gray-400 text-sm mt-1">Engine power in horsepower (HP)</p>
                </div>

                <div>
                  <label className="block text-gray-300 mb-2">Age (Years)</label>
                  <input
                    type="number"
                    min="0"
                    value={formData.age}
                    onChange={(e) => handleInputChange('age', e.target.value)}
                    placeholder="e.g., 5"
                    className="w-full p-3 bg-gray-700 rounded-lg text-white focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  />
                  <p className="text-gray-400 text-sm mt-1">How old is the vehicle?</p>
                </div>

                <div>
                  <label className="block text-gray-300 mb-2">Mileage</label>
                  <input
                    type="number"
                    min="0"
                    value={formData.mileage}
                    onChange={(e) => handleInputChange('mileage', e.target.value)}
                    placeholder="e.g., 45000"
                    className="w-full p-3 bg-gray-700 rounded-lg text-white focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  />
                  <p className="text-gray-400 text-sm mt-1">Total miles driven</p>
                </div>

                <button
                  onClick={handlePrediction}
                  disabled={isLoading}
                  className="w-full py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded-lg transition-colors flex items-center justify-center gap-2"
                >
                  {isLoading ? (
                    <>
                      <div className="animate-spin rounded-full h-5 w-5 border-t-2 border-b-2 border-white"></div>
                      Calculating...
                    </>
                  ) : (
                    <>
                      <span>💰</span> Predict Price
                    </>
                  )}
                </button>
              </div>

              <div className="space-y-6">
                {predictionResult && (
                  <div className="bg-gradient-to-r from-blue-900/50 to-purple-900/50 rounded-lg p-6 border border-blue-500">
                    <h3 className="text-xl text-white mb-4 flex items-center gap-2">
                      <span>🎯</span> Prediction Result
                    </h3>
                    
                    <div className="text-center mb-6">
                      <div className="text-4xl font-bold text-blue-400 mb-2">
                        {formatPrice(predictionResult.predicted_price)}
                      </div>
                      <div className="text-gray-300">Estimated Market Value</div>
                    </div>

                    <div className="space-y-3 text-sm">
                      <h4 className="text-white font-medium">Vehicle Features:</h4>
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span className="text-gray-300">Horsepower:</span>
                          <span className="text-white">{predictionResult.features_used.Horsepower} HP</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-300">Age:</span>
                          <span className="text-white">{predictionResult.features_used.Age} years</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-300">Mileage:</span>
                          <span className="text-white">{predictionResult.features_used.Mileage.toLocaleString()} miles</span>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                <div className="bg-gray-700 rounded-lg p-4">
                  <h4 className="text-white mb-3">💡 Tips for Accurate Predictions</h4>
                  <ul className="text-gray-300 text-sm space-y-1">
                    <li>• Higher horsepower typically increases value</li>
                    <li>• Newer cars (lower age) are usually more valuable</li>
                    <li>• Lower mileage increases car value</li>
                    <li>• Ensure accurate data for best results</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Batch Prediction Tab */}
        {activeTab === 'batch' && (
          <div className="bg-gray-800 rounded-xl p-6 shadow-2xl">
            <h2 className="text-2xl text-white mb-6 flex items-center gap-2">
              <span>🚙</span> Batch Car Analysis
            </h2>
            
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <p className="text-gray-300">Analyze multiple cars at once:</p>
                <button
                  onClick={addBatchPrediction}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm"
                >
                  + Add Car
                </button>
              </div>

              <div className="space-y-4">
                {batchPredictions.map((car, index) => (
                  <div key={index} className="bg-gray-700 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-white font-medium">Car {index + 1}</h3>
                      {batchPredictions.length > 1 && (
                        <button
                          onClick={() => removeBatchPrediction(index)}
                          className="p-1 bg-red-600 hover:bg-red-700 text-white rounded"
                        >
                          ✕
                        </button>
                      )}
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                      <input
                        type="number"
                        placeholder="Horsepower"
                        value={car.horsepower}
                        onChange={(e) => updateBatchPrediction(index, 'horsepower', e.target.value)}
                        className="p-2 bg-gray-600 rounded text-white text-sm focus:ring-1 focus:ring-blue-500 focus:outline-none"
                      />
                      <input
                        type="number"
                        placeholder="Age (years)"
                        value={car.age}
                        onChange={(e) => updateBatchPrediction(index, 'age', e.target.value)}
                        className="p-2 bg-gray-600 rounded text-white text-sm focus:ring-1 focus:ring-blue-500 focus:outline-none"
                      />
                      <input
                        type="number"
                        placeholder="Mileage"
                        value={car.mileage}
                        onChange={(e) => updateBatchPrediction(index, 'mileage', e.target.value)}
                        className="p-2 bg-gray-600 rounded text-white text-sm focus:ring-1 focus:ring-blue-500 focus:outline-none"
                      />
                    </div>
                  </div>
                ))}
              </div>

              <button
                onClick={handleBatchPrediction}
                disabled={isLoading}
                className="w-full py-3 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded-lg transition-colors flex items-center justify-center gap-2"
              >
                {isLoading ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-t-2 border-b-2 border-white"></div>
                    Processing Batch...
                  </>
                ) : (
                  <>
                    <span>⚡</span> Analyze All Cars
                  </>
                )}
              </button>

              {batchResults.length > 0 && (
                <div className="bg-gray-700 rounded-lg p-6">
                  <h3 className="text-lg text-white mb-4">Batch Results ({batchResults.length} cars)</h3>
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="text-gray-300 border-b border-gray-600">
                          <th className="text-left p-2">Horsepower</th>
                          <th className="text-left p-2">Age</th>
                          <th className="text-left p-2">Mileage</th>
                          <th className="text-left p-2">Predicted Price</th>
                        </tr>
                      </thead>
                      <tbody>
                        {batchResults.map((result, index) => (
                          <tr key={index} className="text-white border-b border-gray-600">
                            <td className="p-2">{result.Horsepower} HP</td>
                            <td className="p-2">{result.Age} years</td>
                            <td className="p-2">{result.Mileage.toLocaleString()} mi</td>
                            <td className="p-2 font-semibold text-blue-400">
                              {formatPrice(result.predicted_price)}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* History Tab */}
        {activeTab === 'history' && (
          <div className="bg-gray-800 rounded-xl p-6 shadow-2xl">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl text-white flex items-center gap-2">
                <span>📋</span> Prediction History
              </h2>
              {predictionHistory.length > 0 && (
                <button
                  onClick={clearHistory}
                  className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg text-sm"
                >
                  Clear History
                </button>
              )}
            </div>
            
            {predictionHistory.length > 0 ? (
              <div className="space-y-4">
                {predictionHistory.map((prediction) => (
                  <div key={prediction.id} className="bg-gray-700 rounded-lg p-4 border-l-4 border-blue-500">
                    <div className="flex items-start justify-between mb-3">
                      <span className="text-gray-400 text-sm">{prediction.timestamp}</span>
                      <span className="text-2xl font-bold text-blue-400">
                        {formatPrice(prediction.predicted_price)}
                      </span>
                    </div>
                    <div className="grid grid-cols-3 gap-3 text-sm">
                      <div>
                        <span className="text-gray-400">Horsepower:</span>
                        <span className="text-white ml-2">{prediction.Horsepower} HP</span>
                      </div>
                      <div>
                        <span className="text-gray-400">Age:</span>
                        <span className="text-white ml-2">{prediction.Age} years</span>
                      </div>
                      <div>
                        <span className="text-gray-400">Mileage:</span>
                        <span className="text-white ml-2">{prediction.Mileage.toLocaleString()} mi</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center text-gray-400 py-12">
                <div className="text-6xl mb-4">🚗</div>
                <p className="text-xl">No predictions yet</p>
                <p className="mt-2">Start predicting car prices to see your history</p>
              </div>
            )}
          </div>
        )}

        {/* Model Info Tab */}
        {activeTab === 'info' && (
          <div className="bg-gray-800 rounded-xl p-6 shadow-2xl">
            <h2 className="text-2xl text-white mb-6 flex items-center gap-2">
              <span>ℹ️</span> Model Information
            </h2>
            
            <div className="grid md:grid-cols-2 gap-8">
              <div className="space-y-6">
                <div className="bg-gray-700 rounded-lg p-4">
                  <h3 className="text-lg text-white mb-3">Model Details</h3>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-300">Algorithm:</span>
                      <span className="text-blue-400">Linear Regression</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-300">Framework:</span>
                      <span className="text-blue-400">Scikit-learn</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-300">Preprocessing:</span>
                      <span className="text-blue-400">StandardScaler</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-300">Model Format:</span>
                      <span className="text-blue-400">Pickle (.pkl)</span>
                    </div>
                  </div>
                </div>

                <div className="bg-gray-700 rounded-lg p-4">
                  <h3 className="text-lg text-white mb-3">Input Features</h3>
                  <div className="space-y-2 text-sm">
                    <div className="flex items-center gap-2">
                      <span className="text-blue-400">⚡</span>
                      <span className="text-white">Horsepower - Engine power (HP)</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-blue-400">📅</span>
                      <span className="text-white">Age - Vehicle age in years</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-blue-400">🛣️</span>
                      <span className="text-white">Mileage - Total miles driven</span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="space-y-6">
                <div className="bg-gray-700 rounded-lg p-4">
                  <h3 className="text-lg text-white mb-3">Usage Guidelines</h3>
                  <div className="space-y-3 text-sm text-gray-300">
                    <div className="flex items-start gap-2">
                      <span className="text-yellow-400 mt-1">⚠️</span>
                      <span>Predictions are estimates based on training data</span>
                    </div>
                    <div className="flex items-start gap-2">
                      <span className="text-blue-400 mt-1">💡</span>
                      <span>Accurate inputs provide better predictions</span>
                    </div>
                    <div className="flex items-start gap-2">
                      <span className="text-green-400 mt-1">✅</span>
                      <span>Consider market trends and vehicle condition</span>
                    </div>
                    <div className="flex items-start gap-2">
                      <span className="text-purple-400 mt-1">🎯</span>
                      <span>Use for estimates, consult experts for final decisions</span>
                    </div>
                  </div>
                </div>

                <div className="bg-gray-700 rounded-lg p-4">
                  <h3 className="text-lg text-white mb-3">API Endpoints</h3>
                  <div className="space-y-2 text-sm">
                    <div className="bg-gray-800 p-2 rounded font-mono text-blue-400">
                      POST /car-price/predict
                    </div>
                    <div className="text-gray-300">
                      Accepts vehicle features and returns predicted price in USD
                    </div>
                  </div>
                </div>

                <div className="bg-gradient-to-r from-blue-900/50 to-purple-900/50 rounded-lg p-4 border border-blue-500">
                  <h3 className="text-lg text-white mb-2">Ready to predict?</h3>
                  <p className="text-gray-300 text-sm mb-3">
                    Start with the Single Prediction tab to analyze one car or use Batch Analysis for multiple vehicles.
                  </p>
                  <button
                    onClick={() => setActiveTab('predict')}
                    className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded text-sm transition-colors"
                  >
                    Get Started
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CarPricePredictor;