import React, { useState, useEffect, useCallback } from 'react';
import './App.css';

// Import components
import Dashboard from './components/Dashboard';
import TeaPrediction from './components/TeaPrediction';
import CropRecommendation from './components/CropRecommendation';

const DEFAULT_VIEW = 'dashboard';

function App() {
  const [currentView, setCurrentView] = useState(
    () => window.history.state?.view || DEFAULT_VIEW
  );

  // Keep the browser history in sync with the current view so the browser's
  // back button returns to the previous view instead of leaving the app
  useEffect(() => {
    window.history.replaceState({ view: currentView }, '');

    const handlePopState = (event) => {
      setCurrentView(event.state?.view || DEFAULT_VIEW);
    };

    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const navigate = useCallback((view) => {
    if (view !== window.history.state?.view) {
      window.history.pushState({ view }, '');
    }
    setCurrentView(view);
  }, []);

  const renderCurrentView = () => {
    switch (currentView) {
      case 'dashboard':
        return <Dashboard onNavigate={navigate} />;
      case 'tea-prediction':
        return <TeaPrediction onNavigate={navigate} />;
      case 'crop-recommendation':
        return <CropRecommendation onNavigate={navigate} />;
      default:
        return <Dashboard onNavigate={navigate} />;
    }
  };

  return (
    <div className="App">
      {renderCurrentView()}
    </div>
  );
}

export default App;
