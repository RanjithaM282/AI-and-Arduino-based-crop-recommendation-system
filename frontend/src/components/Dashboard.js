import React from 'react';
import './Dashboard.css';

const Dashboard = ({ onNavigate }) => {
  const features = [
    {
      id: 'tea-prediction',
      title: 'Tea Production Prediction',
      description: 'Predict tea crop yield based on weather conditions and location',
      icon: '🍃',
      color: 'linear-gradient(135deg, #059669 0%, #10b981 100%)',
      features: [
        'Location-based predictions',
        'Weather data integration',
        'Historical analysis',
        'Real-time forecasting'
      ]
    },
    {
      id: 'crop-recommendation',
      title: 'Smart Crop Recommendation',
      description: 'Get personalized crop recommendations based on soil NPK and pH values',
      icon: '🌾',
      color: 'linear-gradient(135deg, #2563eb 0%, #3b82f6 100%)',
      features: [
        'NPK analysis',
        'pH suitability scoring',
        '22 crop types supported',
        'Beautiful crop images'
      ]
    }
  ];

  return (
    <div className="dashboard">
      {/* Header */}
      <div className="dashboard-header">
        <div className="header-content">
          <h1 className="dashboard-title">
            🌱 Smart Agriculture System
          </h1>
          <p className="dashboard-subtitle">
            AI-powered crop prediction and recommendation platform
          </p>
        </div>
      </div>

      {/* Features Grid */}
      <div className="features-container">
        <div className="features-grid">
          {features.map((feature) => (
            <div
              key={feature.id}
              className="feature-card"
              onClick={() => onNavigate(feature.id)}
              style={{ background: feature.color }}
            >
              <div className="feature-icon">
                <span className="icon-emoji">{feature.icon}</span>
              </div>
              <div className="feature-content">
                <h3 className="feature-title">{feature.title}</h3>
                <p className="feature-description">{feature.description}</p>
                
                <div className="feature-list">
                  {feature.features.map((item, index) => (
                    <div key={index} className="feature-item">
                      <span className="check-icon">✓</span>
                      <span>{item}</span>
                    </div>
                  ))}
                </div>
                
                <button className="feature-button">
                  Get Started →
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Stats Section */}
      <div className="stats-section">
        <div className="stats-container">
          <div className="stat-item">
            <div className="stat-number">95%</div>
            <div className="stat-label">Accuracy Rate</div>
          </div>
          <div className="stat-item">
            <div className="stat-number">22</div>
            <div className="stat-label">Crop Types</div>
          </div>
          <div className="stat-item">
            <div className="stat-number">24/7</div>
            <div className="stat-label">Available</div>
          </div>
          <div className="stat-item">
            <div className="stat-number">AI</div>
            <div className="stat-label">Powered</div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="dashboard-footer">
        <p>🌍 Sustainable Agriculture for Better Tomorrow</p>
      </div>
    </div>
  );
};

export default Dashboard;
