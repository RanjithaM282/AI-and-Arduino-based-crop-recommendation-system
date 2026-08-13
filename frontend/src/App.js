import React, { useState } from 'react';
import './App.css';

// Import components
import Dashboard from './components/Dashboard';
import TeaPrediction from './components/TeaPrediction';
import CropRecommendation from './components/CropRecommendation';

function App() {
  const [currentView, setCurrentView] = useState('dashboard');

  const renderCurrentView = () => {
    switch (currentView) {
      case 'dashboard':
        return <Dashboard onNavigate={setCurrentView} />;
      case 'tea-prediction':
        return <TeaPrediction onNavigate={setCurrentView} />;
      case 'crop-recommendation':
        return <CropRecommendation onNavigate={setCurrentView} />;
      default:
        return <Dashboard onNavigate={setCurrentView} />;
    }
  };

  return (
    <div className="App">
      {renderCurrentView()}
    </div>
  );
}

export default App;
