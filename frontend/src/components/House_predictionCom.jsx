'use client';
import React, { useState, useEffect } from 'react';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import AxiosInstance from "@/components/AxiosInstance";

const HousePricePredictor = () => {
  const [activeTab, setActiveTab] = useState('predict');
  const [isLoading, setIsLoading] = useState(false);

  // Prediction state
  const [formData, setFormData] = useState({
    size_sqft: '',
    bedrooms: '',
    bathrooms: '',
    location: '',
    age_years: ''
  });

  // Location options (you can customize these based on your model's encoding)
  const locationOptions = [
    { value: 0, label: 'Urban Core' },
    { value: 1, label: 'Downtown' },
    { value: 2, label: 'Suburban' },
    { value: 3, label: 'Residential' },
    { value: 4, label: 'Outskirts' },
    { value: 5, label: 'Rural' }
  ];
  const [predictionResult, setPredictionResult] = useState(null);
  const [predictionHistory, setPredictionHistory] = useState([]);

  // Batch prediction state
  const [batchPredictions, setBatchPredictions] = useState([
    { size_sqft: '', bedrooms: '', bathrooms: '', location: '', age_years: '' }
  ]);
  const [batchResults, setBatchResults] = useState([]);

  // Load prediction history from localStorage on component mount
  useEffect(() => {
    const savedHistory = localStorage.getItem('housePricePredictions');
    if (savedHistory) {
      setPredictionHistory(JSON.parse(savedHistory));
    }
  }, []);

  // Save prediction history to localStorage
  const savePredictionToHistory = (prediction) => {
    const newHistory = [{
      id: Date.now(),
      ...prediction,
      timestamp: new Date().toLocaleString()
    }, ...predictionHistory.slice(0, 9)];
    
    setPredictionHistory(newHistory);
    localStorage.setItem('housePricePredictions', JSON.stringify(newHistory));
  };

  // API base URL - you can configure this
  const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '';

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const validateForm = (data) => {
    const errors = [];
    if (!data.size_sqft || data.size_sqft <= 0) errors.push('Valid size in sqft is required');
    if (!data.bedrooms || data.bedrooms < 0) errors.push('Valid number of bedrooms is required');
    if (!data.bathrooms || data.bathrooms < 0) errors.push('Valid number of bathrooms is required');
    if (data.location === '' || data.location < 0) errors.push('Location selection is required');
    if (!data.age_years || data.age_years < 0) errors.push('Valid age in years is required');
    return errors;
  };

  const handlePrediction = async () => {
  const errors = validateForm(formData);
  if (errors.length > 0) {
    toast.error(errors.join(', '));
    return;
  }

  setIsLoading(true);
  try {
    // Convert string inputs to numbers for numeric fields
    const requestData = {
      size_sqft: parseFloat(formData.size_sqft),
      bedrooms: parseInt(formData.bedrooms),
      bathrooms: parseFloat(formData.bathrooms),
      location: parseInt(formData.location),
      age_years: parseInt(formData.age_years)
    };

    const response = await AxiosInstance.post('/api/house-price/predict', requestData, {
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (response.status !== 200) {
      throw new Error(response.data.detail || 'Prediction failed');
    }

    const result = response.data;
    setPredictionResult(result);
    
    // Save to history
    savePredictionToHistory({
      ...requestData,
      predicted_price: result.predicted_price
    });
    
    toast.success('Prediction completed!');
  } catch (error) {
    console.error('Prediction error:', error);
    if (error.response) {
      // Server responded with error status
      toast.error(error.response.data.detail || 'Prediction failed');
    } else if (error.request) {
      // Request was made but no response received
      toast.error('No response from server. Check connection.');
    } else {
      // Other errors
      toast.error(error.message || 'Prediction failed');
    }
  } finally {
    setIsLoading(false);
  }
};

  const addBatchPrediction = () => {
    setBatchPredictions([...batchPredictions, { 
      size_sqft: '', bedrooms: '', bathrooms: '', location: '', age_years: '' 
    }]);
  };

  const removeBatchPrediction = (index) => {
    const newBatch = batchPredictions.filter((_, i) => i !== index);
    setBatchPredictions(newBatch.length > 0 ? newBatch : [{ 
      size_sqft: '', bedrooms: '', bathrooms: '', location: '', age_years: '' 
    }]);
  };

  const updateBatchPrediction = (index, field, value) => {
    const newBatch = [...batchPredictions];
    newBatch[index][field] = value;
    setBatchPredictions(newBatch);
  };

  const handleBatchPrediction = async () => {
    const validPredictions = batchPredictions.filter(pred => 
      pred.size_sqft && pred.bedrooms && pred.bathrooms && pred.location !== '' && pred.age_years
    );

    if (validPredictions.length === 0) {
      toast.warning('Please fill in at least one complete property prediction');
      return;
    }

    setIsLoading(true);
    try {
      const results = [];
      for (const pred of validPredictions) {
        const requestData = {
          size_sqft: parseFloat(pred.size_sqft),
          bedrooms: parseInt(pred.bedrooms),
          bathrooms: parseFloat(pred.bathrooms),
          location: parseInt(pred.location),
          age_years: parseInt(pred.age_years)
        };

        const response = await fetch(`${API_BASE_URL}/api/house-price/predict`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(requestData),
        });

        if (!response.ok) {
          const error = await response.json();
          throw new Error(error.detail || 'Batch prediction failed');
        }

        const result = await response.json();
        results.push({
          ...requestData,
          predicted_price: result.predicted_price,
          timestamp: new Date().toLocaleString()
        });
      }
      
      setBatchResults(results);
      toast.success(`Batch prediction completed for ${results.length} properties!`);
    } catch (error) {
      console.error('Batch prediction error:', error);
      toast.error(error.message || 'Batch prediction failed');
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

  const getLocationLabel = (locationValue) => {
    const location = locationOptions.find(loc => loc.value === parseInt(locationValue));
    return location ? location.label : `Location ${locationValue}`;
  };

  const clearHistory = () => {
    setPredictionHistory([]);
    localStorage.removeItem('housePricePredictions');
    toast.info('Prediction history cleared');
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 to-gray-800 py-12 px-4">
      <ToastContainer position="top-right" autoClose={3000} theme="dark" />
      
      <div className="max-w-7xl mx-auto">
        {/* Header Section */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-light text-white mb-2">HOUSE PRICE PREDICTOR</h1>
          <div className="w-24 h-1 bg-gradient-to-r from-green-400 to-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-300 max-w-2xl mx-auto">
            Advanced machine learning model to predict house prices based on key property features. 
            Get accurate price estimates for single properties or analyze multiple properties at once.
          </p>
        </div>

        {/* Navigation Tabs */}
        <div className="flex flex-wrap gap-2 mb-8 bg-gray-800/30 p-2 rounded-xl">
          {[
            { id: 'predict', label: 'Single Prediction', icon: '🏠' },
            { id: 'batch', label: 'Batch Analysis', icon: '🏘️' },
            { id: 'history', label: 'History', icon: '📋' },
            { id: 'info', label: 'Model Info', icon: 'ℹ️' }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                activeTab === tab.id
                  ? 'bg-green-600 text-white'
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
              <span>🏠</span> Property Price Prediction
            </h2>
            
            <div className="grid md:grid-cols-2 gap-8">
              <div className="space-y-6">
                <div>
                  <label className="block text-gray-300 mb-2">Size (Square Feet)</label>
                  <input
                    type="number"
                    min="100"
                    value={formData.size_sqft}
                    onChange={(e) => handleInputChange('size_sqft', e.target.value)}
                    placeholder="e.g., 2500"
                    className="w-full p-3 bg-gray-700 rounded-lg text-white focus:ring-2 focus:ring-green-500 focus:outline-none"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-gray-300 mb-2">Bedrooms</label>
                    <input
                      type="number"
                      min="0"
                      value={formData.bedrooms}
                      onChange={(e) => handleInputChange('bedrooms', e.target.value)}
                      placeholder="e.g., 3"
                      className="w-full p-3 bg-gray-700 rounded-lg text-white focus:ring-2 focus:ring-green-500 focus:outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-gray-300 mb-2">Bathrooms</label>
                    <input
                      type="number"
                      min="0"
                      step="0.5"
                      value={formData.bathrooms}
                      onChange={(e) => handleInputChange('bathrooms', e.target.value)}
                      placeholder="e.g., 2.5"
                      className="w-full p-3 bg-gray-700 rounded-lg text-white focus:ring-2 focus:ring-green-500 focus:outline-none"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-gray-300 mb-2">Location</label>
                  <select
                    value={formData.location}
                    onChange={(e) => handleInputChange('location', e.target.value)}
                    className="w-full p-3 bg-gray-700 rounded-lg text-white focus:ring-2 focus:ring-green-500 focus:outline-none"
                  >
                    <option value="">Select Location</option>
                    {locationOptions.map((option) => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-gray-300 mb-2">Age (Years)</label>
                  <input
                    type="number"
                    min="0"
                    value={formData.age_years}
                    onChange={(e) => handleInputChange('age_years', e.target.value)}
                    placeholder="e.g., 15"
                    className="w-full p-3 bg-gray-700 rounded-lg text-white focus:ring-2 focus:ring-green-500 focus:outline-none"
                  />
                </div>

                <button
                  onClick={handlePrediction}
                  disabled={isLoading}
                  className="w-full py-3 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded-lg transition-colors flex items-center justify-center gap-2"
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
                  <div className="bg-gradient-to-r from-green-900/50 to-blue-900/50 rounded-lg p-6 border border-green-500">
                    <h3 className="text-xl text-white mb-4 flex items-center gap-2">
                      <span>🎯</span> Prediction Result
                    </h3>
                    
                    <div className="text-center mb-6">
                      <div className="text-4xl font-bold text-green-400 mb-2">
                        {formatPrice(predictionResult.predicted_price)}
                      </div>
                      <div className="text-gray-300">Estimated Market Value</div>
                    </div>

                    <div className="space-y-3 text-sm">
                      <h4 className="text-white font-medium">Property Features:</h4>
                      <div className="grid grid-cols-2 gap-2">
                        <div className="flex justify-between">
                          <span className="text-gray-300">Size:</span>
                          <span className="text-white">{predictionResult.features_used.size_sqft.toLocaleString()} sqft</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-300">Bedrooms:</span>
                          <span className="text-white">{predictionResult.features_used.bedrooms}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-300">Bathrooms:</span>
                          <span className="text-white">{predictionResult.features_used.bathrooms}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-300">Age:</span>
                          <span className="text-white">{predictionResult.features_used.age_years} years</span>
                        </div>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-300">Location:</span>
                        <span className="text-white">{getLocationLabel(predictionResult.features_used.location)}</span>
                      </div>
                    </div>
                  </div>
                )}

                <div className="bg-gray-700 rounded-lg p-4">
                  <h4 className="text-white mb-3">💡 Tips for Accurate Predictions</h4>
                  <ul className="text-gray-300 text-sm space-y-1">
                    <li>• Enter precise square footage</li>
                    <li>• Include half-bathrooms (e.g., 2.5)</li>
                    <li>• Use specific location names</li>
                    <li>• Property age affects value significantly</li>
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
              <span>🏘️</span> Batch Property Analysis
            </h2>
            
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <p className="text-gray-300">Analyze multiple properties at once:</p>
                <button
                  onClick={addBatchPrediction}
                  className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg text-sm"
                >
                  + Add Property
                </button>
              </div>

              <div className="space-y-4">
                {batchPredictions.map((property, index) => (
                  <div key={index} className="bg-gray-700 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-white font-medium">Property {index + 1}</h3>
                      {batchPredictions.length > 1 && (
                        <button
                          onClick={() => removeBatchPrediction(index)}
                          className="p-1 bg-red-600 hover:bg-red-700 text-white rounded"
                        >
                          ✕
                        </button>
                      )}
                    </div>
                    
                    <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
                      <input
                        type="number"
                        placeholder="Size (sqft)"
                        value={property.size_sqft}
                        onChange={(e) => updateBatchPrediction(index, 'size_sqft', e.target.value)}
                        className="p-2 bg-gray-600 rounded text-white text-sm focus:ring-1 focus:ring-green-500 focus:outline-none"
                      />
                      <input
                        type="number"
                        placeholder="Bedrooms"
                        value={property.bedrooms}
                        onChange={(e) => updateBatchPrediction(index, 'bedrooms', e.target.value)}
                        className="p-2 bg-gray-600 rounded text-white text-sm focus:ring-1 focus:ring-green-500 focus:outline-none"
                      />
                      <input
                        type="number"
                        step="0.5"
                        placeholder="Bathrooms"
                        value={property.bathrooms}
                        onChange={(e) => updateBatchPrediction(index, 'bathrooms', e.target.value)}
                        className="p-2 bg-gray-600 rounded text-white text-sm focus:ring-1 focus:ring-green-500 focus:outline-none"
                      />
                      <select
                        value={property.location}
                        onChange={(e) => updateBatchPrediction(index, 'location', e.target.value)}
                        className="p-2 bg-gray-600 rounded text-white text-sm focus:ring-1 focus:ring-green-500 focus:outline-none"
                      >
                        <option value="">Location</option>
                        {locationOptions.map((option) => (
                          <option key={option.value} value={option.value}>
                            {option.label}
                          </option>
                        ))}
                      </select>
                      <input
                        type="number"
                        placeholder="Age (years)"
                        value={property.age_years}
                        onChange={(e) => updateBatchPrediction(index, 'age_years', e.target.value)}
                        className="p-2 bg-gray-600 rounded text-white text-sm focus:ring-1 focus:ring-green-500 focus:outline-none"
                      />
                    </div>
                  </div>
                ))}
              </div>

              <button
                onClick={handleBatchPrediction}
                disabled={isLoading}
                className="w-full py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded-lg transition-colors flex items-center justify-center gap-2"
              >
                {isLoading ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-t-2 border-b-2 border-white"></div>
                    Processing Batch...
                  </>
                ) : (
                  <>
                    <span>⚡</span> Analyze All Properties
                  </>
                )}
              </button>

              {batchResults.length > 0 && (
                <div className="bg-gray-700 rounded-lg p-6">
                  <h3 className="text-lg text-white mb-4">Batch Results ({batchResults.length} properties)</h3>
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="text-gray-300 border-b border-gray-600">
                          <th className="text-left p-2">Size</th>
                          <th className="text-left p-2">Bed/Bath</th>
                          <th className="text-left p-2">Location</th>
                          <th className="text-left p-2">Age</th>
                          <th className="text-left p-2">Predicted Price</th>
                        </tr>
                      </thead>
                      <tbody>
                        {batchResults.map((result, index) => (
                          <tr key={index} className="text-white border-b border-gray-600">
                            <td className="p-2">{result.size_sqft.toLocaleString()} sqft</td>
                            <td className="p-2">{result.bedrooms}/{result.bathrooms}</td>
                            <td className="p-2">{getLocationLabel(result.location)}</td>
                            <td className="p-2">{result.age_years}y</td>
                            <td className="p-2 font-semibold text-green-400">
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
                  <div key={prediction.id} className="bg-gray-700 rounded-lg p-4 border-l-4 border-green-500">
                    <div className="flex items-start justify-between mb-3">
                      <span className="text-gray-400 text-sm">{prediction.timestamp}</span>
                      <span className="text-2xl font-bold text-green-400">
                        {formatPrice(prediction.predicted_price)}
                      </span>
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                      <div>
                        <span className="text-gray-400">Size:</span>
                        <span className="text-white ml-2">{prediction.size_sqft.toLocaleString()} sqft</span>
                      </div>
                      <div>
                        <span className="text-gray-400">Bed/Bath:</span>
                        <span className="text-white ml-2">{prediction.bedrooms}/{prediction.bathrooms}</span>
                      </div>
                      <div>
                        <span className="text-gray-400">Location:</span>
                        <span className="text-white ml-2">{getLocationLabel(prediction.location)}</span>
                      </div>
                      <div>
                        <span className="text-gray-400">Age:</span>
                        <span className="text-white ml-2">{prediction.age_years} years</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center text-gray-400 py-12">
                <div className="text-6xl mb-4">🏠</div>
                <p className="text-xl">No predictions yet</p>
                <p className="mt-2">Start predicting house prices to see your history</p>
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
                      <span className="text-blue-400">Machine Learning Regression</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-300">Framework:</span>
                      <span className="text-blue-400">Scikit-learn</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-300">Model Format:</span>
                      <span className="text-blue-400">Joblib (.pkl)</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-300">API:</span>
                      <span className="text-blue-400">FastAPI</span>
                    </div>
                  </div>
                </div>

                <div className="bg-gray-700 rounded-lg p-4">
                  <h3 className="text-lg text-white mb-3">Input Features</h3>
                  <div className="space-y-2 text-sm">
                    <div className="flex items-center gap-2">
                      <span className="text-green-400">📐</span>
                      <span className="text-white">Size (sqft) - Property square footage</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-green-400">🛏️</span>
                      <span className="text-white">Bedrooms - Number of bedrooms</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-green-400">🚿</span>
                      <span className="text-white">Bathrooms - Number of bathrooms</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-green-400">📍</span>
                      <span className="text-white">Location - Property location type (0-5)</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-green-400">📅</span>
                      <span className="text-white">Age - Property age in years</span>
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
                      <span>More accurate data inputs lead to better predictions</span>
                    </div>
                    <div className="flex items-start gap-2">
                      <span className="text-green-400 mt-1">✅</span>
                      <span>Consider local market conditions and recent sales</span>
                    </div>
                    <div className="flex items-start gap-2">
                      <span className="text-purple-400 mt-1">🎯</span>
                      <span>Use for initial estimates, consult professionals for final decisions</span>
                    </div>
                  </div>
                </div>

                <div className="bg-gray-700 rounded-lg p-4">
                  <h3 className="text-lg text-white mb-3">API Endpoints</h3>
                  <div className="space-y-2 text-sm">
                    <div className="bg-gray-800 p-2 rounded font-mono text-green-400">
                      POST /api/house-price/predict
                    </div>
                    <div className="text-gray-300">
                      Accepts property features and returns predicted price in USD
                    </div>
                  </div>
                </div>

                <div className="bg-gradient-to-r from-green-900/50 to-blue-900/50 rounded-lg p-4 border border-green-500">
                  <h3 className="text-lg text-white mb-2">Ready to predict?</h3>
                  <p className="text-gray-300 text-sm mb-3">
                    Start with the Single Prediction tab to analyze one property or use Batch Analysis for multiple properties.
                  </p>
                  <button
                    onClick={() => setActiveTab('predict')}
                    className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded text-sm transition-colors"
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

export default HousePricePredictor;