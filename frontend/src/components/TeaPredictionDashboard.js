import React from 'react';
import './TeaPredictionDashboard.css';

const TeaPredictionDashboard = ({ predictionData, loading, error, aiSuggestions }) => {
  if (loading) {
    return (
      <div className="dashboard-container">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>🍵 Analyzing tea growing conditions...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-container">
        <div className="error-message">
          <span className="error-icon">❌</span>
          <p>{error}</p>
        </div>
      </div>
    );
  }

  if (!predictionData) {
    return (
      <div className="dashboard-container">
        <div className="welcome-message">
          <span className="welcome-icon">🍵</span>
          <h2>Tea Crop Prediction Dashboard</h2>
          <p>Select a location on the map to get started</p>
        </div>
      </div>
    );
  }

  const { prediction, location, weather_data, calculated_features, all_features, feature_details } = predictionData;

  const getFeatureIcon = (feature) => {
    const icons = {
      Temperature_C: '🌡️',
      Precipitation_mm_day: '🌧️',
      Humidity_Percent: '💧',
      Solar_Radiation_MJ_m2_day: '☀️',
      Latitude: '📍',
      Longitude: '📍',
      Elevation_m: '⛰️',
      Month_Sin: '�',
      Month_Cos: '�',
      Heat_Index: '�',
      Temp_Humidity: '🌡️💧',
      Rainfall_Humidity: '🌧️💧',
      Temp_Solar: '🌡️☀️',
      Prev_Month_Production: '�',
      Prev_2Month_Production: '📈',
      Rolling_3Month_Avg: '📉',
      State_Encoded: '�️'
    };
    return icons[feature] || '📊';
  };

  const getFeatureLabel = (feature) => {
    const labels = {
      Temperature_C: 'Temperature (°C)',
      Precipitation_mm_day: 'Precipitation (mm/day)',
      Humidity_Percent: 'Humidity (%)',
      Solar_Radiation_MJ_m2_day: 'Solar Radiation (MJ/m²/day)',
      Latitude: 'Latitude',
      Longitude: 'Longitude',
      Elevation_m: 'Elevation (m)',
      Month_Sin: 'Month (Sine)',
      Month_Cos: 'Month (Cosine)',
      Heat_Index: 'Heat Index',
      Temp_Humidity: 'Temp × Humidity',
      Rainfall_Humidity: 'Rainfall × Humidity',
      Temp_Solar: 'Temp × Solar',
      Prev_Month_Production: 'Previous Month Production',
      Prev_2Month_Production: 'Previous 2-Month Production',
      Rolling_3Month_Avg: '3-Month Rolling Average',
      State_Encoded: 'State Code'
    };
    return labels[feature] || feature;
  };

  const getFeatureUnit = (feature) => {
    const units = {
      Temperature_C: '°C',
      Precipitation_mm_day: 'mm/day',
      Humidity_Percent: '%',
      Solar_Radiation_MJ_m2_day: 'MJ/m²/day',
      Latitude: '°',
      Longitude: '°',
      Elevation_m: 'm',
      Month_Sin: '',
      Month_Cos: '',
      Heat_Index: '',
      Temp_Humidity: '',
      Rainfall_Humidity: '',
      Temp_Solar: '',
      Prev_Month_Production: 'tons',
      Prev_2Month_Production: 'tons',
      Rolling_3Month_Avg: 'tons',
      State_Encoded: ''
    };
    return units[feature] || '';
  };

  const getSeasonName = (season) => {
    const seasons = ['', 'Spring', 'Summer', 'Autumn', 'Winter'];
    return seasons[season] || 'Unknown';
  };

  const getPredictionQuality = (value) => {
    // Based on actual dataset ranges (11-38 metric tons)
    if (value >= 30) return { color: '#4CAF50', label: 'Excellent', icon: '🟢' };
    if (value >= 25) return { color: '#8BC34A', label: 'Good', icon: '🟡' };
    if (value >= 15) return { color: '#FF9800', label: 'Fair', icon: '🟠' };
    return { color: '#F44336', label: 'Low', icon: '🔴' };
  };

  const predictionQuality = getPredictionQuality(prediction);

  return (
    <div className="dashboard-container">
      {/* Header Section */}
      <div className="dashboard-header">
        <div className="prediction-result">
          <h2>🍵 Tea Crop Prediction</h2>
          <div className="prediction-score" style={{ borderColor: predictionQuality.color }}>
            <span className="score-icon">{predictionQuality.icon}</span>
            <span className="score-value">{prediction.toFixed(1)}</span>
            <span className="score-label">{predictionQuality.label}</span>
          </div>
        </div>
        
        <div className="location-info">
          <h3>📍 Location</h3>
          <p>Lat: {location.latitude.toFixed(4)}°, Lon: {location.longitude.toFixed(4)}°</p>
          <p>Month: {location.month} ({getSeasonName(calculated_features.season)})</p>
        </div>
      </div>

      {/* Weather Data Section */}
      <div className="dashboard-section">
        <h3>🌤️ Weather Data</h3>
        <div className="weather-grid">
          {weather_data ? (
            <>
              <div className="weather-item">
                <span className="weather-icon">🌡️</span>
                <div>
                  <p className="weather-value">{weather_data.temperature.toFixed(1)}°C</p>
                  <p className="weather-label">Temperature</p>
                </div>
              </div>
              <div className="weather-item">
                <span className="weather-icon">💧</span>
                <div>
                  <p className="weather-value">{weather_data.humidity.toFixed(1)}%</p>
                  <p className="weather-label">Humidity</p>
                </div>
              </div>
              <div className="weather-item">
                <span className="weather-icon">🌧️</span>
                <div>
                  <p className="weather-value">{weather_data.rainfall.toFixed(1)}mm</p>
                  <p className="weather-label">Rainfall</p>
                </div>
              </div>
              <div className="weather-item">
                <span className="weather-icon">💨</span>
                <div>
                  <p className="weather-value">{weather_data.wind_speed.toFixed(1)}km/h</p>
                  <p className="weather-label">Wind Speed</p>
                </div>
              </div>
            </>
          ) : (
            <p className="weather-unavailable">Weather data unavailable (using calculated values)</p>
          )}
        </div>
      </div>

      {/* Features Section */}
      <div className="dashboard-section">
        <h3>🧮 Calculated Features</h3>
        
        {/* Weather Primary Features */}
        <div className="feature-group">
          <h4>🌤️ Weather Data</h4>
          <div className="features-grid">
            {feature_details.weather_primary.map(feature => (
              <div key={feature} className="feature-card">
                <span className="feature-icon">{getFeatureIcon(feature)}</span>
                <div className="feature-info">
                  <p className="feature-value">
                    {all_features[feature].toFixed(2)}{getFeatureUnit(feature)}
                  </p>
                  <p className="feature-label">{getFeatureLabel(feature)}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Location Features */}
        <div className="feature-group">
          <h4>📍 Location & Geographic</h4>
          <div className="features-grid">
            {feature_details.location.map(feature => {
              let displayValue = all_features[feature];
              if (feature === 'State_Encoded') {
                const stateNames = ['Assam', 'West Bengal', 'Tamil Nadu', 'Kerala', 'Karnataka'];
                displayValue = stateNames[displayValue] || `State ${displayValue}`;
              }
              
              return (
                <div key={feature} className="feature-card">
                  <span className="feature-icon">{getFeatureIcon(feature)}</span>
                  <div className="feature-info">
                    <p className="feature-value">
                      {feature === 'State_Encoded' ? displayValue : `${displayValue.toFixed(2)}${getFeatureUnit(feature)}`}
                    </p>
                    <p className="feature-label">{getFeatureLabel(feature)}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Temporal Features */}
        <div className="feature-group">
          <h4>📅 Temporal Features</h4>
          <div className="features-grid">
            {feature_details.temporal.map(feature => (
              <div key={feature} className="feature-card">
                <span className="feature-icon">{getFeatureIcon(feature)}</span>
                <div className="feature-info">
                  <p className="feature-value">
                    {all_features[feature].toFixed(3)}{getFeatureUnit(feature)}
                  </p>
                  <p className="feature-label">{getFeatureLabel(feature)}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Derived Indices */}
        <div className="feature-group">
          <h4>🔥 Derived Indices</h4>
          <div className="features-grid">
            {feature_details.derived_indices.map(feature => (
              <div key={feature} className="feature-card">
                <span className="feature-icon">{getFeatureIcon(feature)}</span>
                <div className="feature-info">
                  <p className="feature-value">
                    {all_features[feature].toFixed(2)}{getFeatureUnit(feature)}
                  </p>
                  <p className="feature-label">{getFeatureLabel(feature)}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Feature Interactions */}
        <div className="feature-group">
          <h4>🧮 Feature Interactions</h4>
          <div className="features-grid">
            {feature_details.feature_interactions.map(feature => (
              <div key={feature} className="feature-card">
                <span className="feature-icon">{getFeatureIcon(feature)}</span>
                <div className="feature-info">
                  <p className="feature-value">
                    {all_features[feature].toFixed(2)}{getFeatureUnit(feature)}
                  </p>
                  <p className="feature-label">{getFeatureLabel(feature)}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Historical Production */}
        <div className="feature-group">
          <h4>📊 Historical Production</h4>
          <div className="features-grid">
            {feature_details.historical_production.map(feature => (
              <div key={feature} className="feature-card">
                <span className="feature-icon">{getFeatureIcon(feature)}</span>
                <div className="feature-info">
                  <p className="feature-value">
                    {all_features[feature].toFixed(2)}{getFeatureUnit(feature)}
                  </p>
                  <p className="feature-label">{getFeatureLabel(feature)}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Summary Section */}
      <div className="dashboard-section summary-section">
        <h3>📊 Analysis Summary</h3>
        <div className="summary-grid">
          <div className="summary-item">
            <h4>🌡️ Temperature</h4>
            <p>{all_features.Temperature_C.toFixed(1)}°C - {all_features.Temperature_C > 25 ? 'Warm' : all_features.Temperature_C > 15 ? 'Moderate' : 'Cool'}</p>
          </div>
          <div className="summary-item">
            <h4>🌧️ Precipitation</h4>
            <p>{all_features.Precipitation_mm_day.toFixed(1)}mm/day - {all_features.Precipitation_mm_day > 5 ? 'High' : all_features.Precipitation_mm_day > 2 ? 'Medium' : 'Low'}</p>
          </div>
          <div className="summary-item">
            <h4>💧 Humidity</h4>
            <p>{all_features.Humidity_Percent.toFixed(1)}% - {all_features.Humidity_Percent > 70 ? 'High' : all_features.Humidity_Percent > 50 ? 'Medium' : 'Low'}</p>
          </div>
          <div className="summary-item">
            <h4>⛰️ Elevation</h4>
            <p>{all_features.Elevation_m.toFixed(0)}m - {all_features.Elevation_m > 130 ? 'High' : all_features.Elevation_m > 125 ? 'Medium' : 'Low'}</p>
          </div>
        </div>
      </div>

      {/* AI Suggestions Section */}
      {predictionData.ai_suggestions && (
        <div className="dashboard-section ai-suggestions-section">
          <h3>🤖 AI-Powered Growing Suggestions</h3>
          <div className="suggestions-container">
            {predictionData.ai_suggestions.source ? (
              <p className="insights-subtitle">Generated by {predictionData.ai_suggestions.source} AI</p>
            ) : (
              <p className="insights-subtitle">{predictionData.ai_suggestions.message || 'AI suggestions unavailable'}</p>
            )}
            <div className="suggestions-grid">
              {predictionData.ai_suggestions.suggestions.map((suggestion, index) => (
                <div key={index} className="suggestion-card">
                  <span className="suggestion-number">{index + 1}</span>
                  <div className="suggestion-content">
                    <p className="suggestion-text">{suggestion.text || suggestion}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TeaPredictionDashboard;
