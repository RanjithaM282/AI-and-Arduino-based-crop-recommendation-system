import React from 'react';
import { Link } from 'react-router-dom';
import './HomePage.css';

const HomePage = () => {
  const quickActions = [
    { id: 'crop-recommendation', title: 'Recommend Crop', icon: '🌱', description: 'Get AI-powered crop recommendations', link: '/crop-recommendation' },
    { id: 'market-prices', title: 'Market Prices', icon: '💰', description: 'Check real-time market prices', link: '/market-prices' },
    { id: 'crop-health', title: 'Crop Health', icon: '📷', description: 'Monitor crop health with AI', link: '/crop-health' },
    { id: 'farm-activities', title: 'Farm Activities', icon: '📅', description: 'Track farming activities', link: '/farm-activities' },
    { id: 'weather', title: 'Weather', icon: '🌦️', description: 'Check weather forecast', link: '/weather' },
    { id: 'profit-analytics', title: 'Farm Analytics', icon: '📊', description: 'View farm performance', link: '/profit-analytics' },
  ];

  const farmerJourney = [
    { step: 1, title: 'Location & Soil', description: 'Analyze your farm location and soil' },
    { step: 2, title: 'Crop Selection', description: 'Get AI-powered crop recommendations' },
    { step: 3, title: 'Planting', description: 'Record planting date and details' },
    { step: 4, title: 'Crop Monitoring', description: 'Track growth and health' },
    { step: 5, title: 'Activities', description: 'Manage fertilizer, irrigation, activities' },
    { step: 6, title: 'Harvest', description: 'Prepare for harvest time' },
    { step: 7, title: 'Market Price', description: 'Check current market prices' },
    { step: 8, title: 'Sell Produce', description: 'List and sell your produce' },
  ];

  return (
    <div className="home-page">
      {/* Hero Section */}
      <section className="hero-section">
        <div className="hero-content">
          <h1 className="hero-title">Your Smart Farming Companion</h1>
          <p className="hero-subtitle">From planting to selling — get intelligent guidance for every stage of farming</p>
          <div className="hero-buttons">
            <Link to="/crop-recommendation" className="btn btn-primary">Start Farming</Link>
            <Link to="/profile" className="btn btn-secondary">Setup Farm</Link>
          </div>
        </div>
      </section>

      {/* Quick Actions */}
      <section className="quick-actions-section">
        <h2 className="section-title">Quick Actions</h2>
        <div className="quick-actions-grid">
          {quickActions.map((action) => (
            <Link key={action.id} to={action.link} className="action-card">
              <div className="action-icon">{action.icon}</div>
              <h3 className="action-title">{action.title}</h3>
              <p className="action-description">{action.description}</p>
            </Link>
          ))}
        </div>
      </section>

      {/* Farmer Journey */}
      <section className="farmer-journey-section">
        <h2 className="section-title">Your Farming Journey</h2>
        <div className="journey-timeline">
          {farmerJourney.map((item) => (
            <div key={item.step} className="journey-item">
              <div className="journey-step">Step {item.step}</div>
              <div className="journey-content">
                <h3 className="journey-title">{item.title}</h3>
                <p className="journey-description">{item.description}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta-section">
        <div className="cta-content">
          <h2 className="cta-title">Ready to Transform Your Farm?</h2>
          <p className="cta-subtitle">Join thousands of farmers using AI to make better decisions</p>
          <Link to="/profile" className="btn btn-primary btn-large">Get Started Now</Link>
        </div>
      </section>
    </div>
  );
};

export default HomePage;
