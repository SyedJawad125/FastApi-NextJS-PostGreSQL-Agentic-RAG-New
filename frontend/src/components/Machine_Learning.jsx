import React, { useState } from 'react';
import { FaBrain, FaChevronDown, FaChevronUp } from 'react-icons/fa';
import Link from 'next/link';

const MachineLearning = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [selectedModel, setSelectedModel] = useState(null);

  const models = [
    { 
      id: 1, 
      name: 'BerT Model', 
      description: 'Seneiment Analysis',
      link: '/bert_modelpage' // Add your specific route here
    },
    { 
      id: 2, 
      name: 'House Prediction', 
      description: 'Linear Regression Model',
      link: '/house_prediction' // Add your specific route here
    },
    { 
      id: 3, 
      name: 'Car Price Prediction ', 
      description: 'Clustering Model',
      link: '/car_price_prediction' // Add your specific route here
    },
    { 
      id: 4, 
      name: 'CNN Prediction Model', 
      description: 'Deep Learning Model',
      link: '/cnn_model' // Add your specific route here
    },
    { 
      id: 5, 
      name: 'ML5', 
      description: 'Deep Learning Model',
      link: '/ml5-page' // Add your specific route here
    },
  ];

  const toggleDropdown = () => {
    setIsOpen(!isOpen);
  };

  const handleModelSelect = (model) => {
    setSelectedModel(model);
    setIsOpen(false);
    console.log(`Selected model: ${model.name} - ${model.description}`);
  };

  return (
    <div className="bg-black text-white p-6 rounded-lg shadow-xl max-w-md mx-auto my-8">
      <h2 className="text-2xl font-serif font-semibold mb-6 text-center flex items-center justify-center">
        <FaBrain className="mr-3 text-red-600" />
        Machine Learning Models
      </h2>
      
      <div className="relative">
        <button
          onClick={toggleDropdown}
          className="w-full bg-gray-900 hover:bg-gray-800 text-white font-medium py-4 px-6 rounded-lg flex items-center justify-between transition-all duration-300"
        >
          <span>
            {selectedModel ? `Selected: ${selectedModel.name}` : 'Select ML Model'}
          </span>
          {isOpen ? <FaChevronUp /> : <FaChevronDown />}
        </button>
        
        {isOpen && (
          <div className="absolute z-10 w-full mt-2 bg-gray-800 border border-gray-700 rounded-lg shadow-lg overflow-hidden">
            {models.map((model) => (
              <Link
                key={model.id}
                href={model.link}
                passHref
              >
                <div
                  onClick={() => handleModelSelect(model)}
                  className="w-full text-left px-6 py-4 hover:bg-gray-700 transition-colors duration-200 flex items-center cursor-pointer"
                >
                  <span className="font-mono bg-red-700 text-white rounded-full w-8 h-8 flex items-center justify-center mr-3">
                    {model.id}
                  </span>
                  <div>
                    <div className="font-medium">{model.name}</div>
                    <div className="text-sm text-gray-400">{model.description}</div>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
      
      {selectedModel && (
        <div className="mt-6 p-4 bg-gray-900 rounded-lg">
          <h3 className="font-serif text-lg mb-2">Current Selection:</h3>
          <div className="flex items-center">
            <span className="font-mono bg-red-700 text-white rounded-full w-10 h-10 flex items-center justify-center mr-4">
              {selectedModel.id}
            </span>
            <div>
              <p className="font-medium text-xl">{selectedModel.name}</p>
              <p className="text-gray-400">{selectedModel.description}</p>
            </div>
          </div>
          <Link href={selectedModel.link} passHref>
            <button className="mt-4 bg-red-700 hover:bg-red-600 text-white py-2 px-6 rounded-md transition-colors w-full">
              Go to {selectedModel.name} Page
            </button>
          </Link>
        </div>
      )}
      
      <div className="mt-8 text-center text-gray-400 text-sm">
        <p>Select and navigate to specialized machine learning models</p>
      </div>
    </div>
  );
};

export default MachineLearning;