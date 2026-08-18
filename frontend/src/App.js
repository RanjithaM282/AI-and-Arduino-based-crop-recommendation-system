import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';

// Import components
import Navbar from './components/Navbar/Navbar';

// Import pages
import HomePage from './pages/HomePage';
import MyFarm from './pages/MyFarm';
import CropRecommendation from './components/CropRecommendation';
import MarketPrices from './pages/MarketPrices';
import CropCalendar from './pages/CropCalendar';
import FarmActivities from './pages/FarmActivities';
import CropHealth from './pages/CropHealth';
import Weather from './pages/Weather';
import ProfitAnalytics from './pages/ProfitAnalytics';
import SellProduce from './pages/SellProduce';
import FarmerAssistant from './pages/FarmerAssistant';
import Profile from './pages/Profile';
import Help from './pages/Help';

function App() {
  return (
    <Router>
      <div className="App">
        <Navbar />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/my-farm" element={<MyFarm />} />
            <Route path="/crop-recommendation" element={<CropRecommendation />} />
            <Route path="/market-prices" element={<MarketPrices />} />
            <Route path="/crop-calendar" element={<CropCalendar />} />
            <Route path="/farm-activities" element={<FarmActivities />} />
            <Route path="/crop-health" element={<CropHealth />} />
            <Route path="/weather" element={<Weather />} />
            <Route path="/profit-analytics" element={<ProfitAnalytics />} />
            <Route path="/sell-produce" element={<SellProduce />} />
            <Route path="/farmer-assistant" element={<FarmerAssistant />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="/help" element={<Help />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
