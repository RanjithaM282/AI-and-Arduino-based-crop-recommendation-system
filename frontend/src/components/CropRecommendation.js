import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './CropRecommendation.css';
import PricePredictionDashboard from './PricePredictionDashboard';

const CropRecommendation = ({ onNavigate }) => {
  const [soilData, setSoilData] = useState({
    nitrogen: '',
    phosphorus: '',
    potassium: '',
    ph: ''
  });
  
  const [arduinoSensors, setArduinoSensors] = useState({
    temperature: null,
    humidity: null,
    soil_moisture: null,
    timestamp: null
  });
  
  const [arduinoStatus, setArduinoStatus] = useState({
    connected: false,
    message: 'Not initialized'
  });
  
  const [recommendations, setRecommendations] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [sensorLoading, setSensorLoading] = useState(false);
  const [pumpStatus, setPumpStatus] = useState('OFF');
  const [showPriceDashboard, setShowPriceDashboard] = useState(false);
  const [acres, setAcres] = useState(1);

  // Fetch Arduino sensor data on component mount
  useEffect(() => {
    fetchArduinoSensors();
    // Set up interval to refresh sensor data every 2 seconds
    const interval = setInterval(fetchArduinoSensors, 2000);
    return () => clearInterval(interval);
  }, []);

  const fetchArduinoSensors = async () => {
    try {
      setSensorLoading(true);
      const response = await axios.get('http://127.0.0.1:5001/sensor');
      
      // Update Arduino sensor data
      setArduinoSensors(response.data.arduino_data || {
        temperature: null,
        humidity: null,
        soil_moisture: null,
        timestamp: null
      });
      
      // Update Arduino connection status
      setArduinoStatus(response.data.arduino_status || {
        connected: false,
        message: 'Status not available'
      });
      
      console.log('Arduino Status:', response.data.arduino_status);
      console.log('Arduino Data:', response.data.arduino_data);
      
    } catch (err) {
      console.error('Failed to fetch Arduino sensors:', err);
      setArduinoStatus({
        connected: false,
        message: 'Failed to connect to backend'
      });
    } finally {
      setSensorLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setSoilData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleRecommendCrop = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.post('http://127.0.0.1:5001/crop-recommend', {
        nitrogen: parseFloat(soilData.nitrogen),
        phosphorus: parseFloat(soilData.phosphorus),
        potassium: parseFloat(soilData.potassium),
        ph: parseFloat(soilData.ph),
        temperature: parseFloat(arduinoSensors.temperature),
        humidity: parseFloat(arduinoSensors.humidity),
        soil_moisture: parseFloat(arduinoSensors.soil_moisture)
      });
      
      setRecommendations(response.data);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to get crop recommendations');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    handleRecommendCrop();
  };

  const controlPump = async (command) => {
    try {
      const response = await axios.post('/pump', { command });
      if (response.data.status === 'success') {
        setPumpStatus(command);
        console.log(`Pump turned ${command}`);
      }
    } catch (err) {
      console.error('Failed to control pump:', err);
    }
  };

  const cropImages = {
    wheat: 'https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=400&h=300&fit=crop&crop=center',
    rice: 'https://images.unsplash.com/photo-1586771107445-d3ca888129ff?w=400&h=300&fit=crop&crop=center',
    corn: 'https://images.unsplash.com/photo-1551754655-cd27e38d2076?w=400&h=300&fit=crop&crop=center',
    cotton: '/images/cotton.png',
    sugarcane: '/images/sugarcane.png',
    pulses: '/images/pulses.png',
    vegetables: 'https://images.unsplash.com/photo-1540420773420-3366772f4999?w=400&h=300&fit=crop&crop=center',
    fruits: 'https://images.unsplash.com/photo-1610832958506-aa56368176cf?w=400&h=300&fit=crop&crop=center'
  };

  const cropEmojis = {
    wheat: '🌾',
    rice: '🌾',
    corn: '🌽',
    cotton: '☁️',
    sugarcane: '🎋',
    pulses: '🫘',
    vegetables: '🥬',
    fruits: '🍎'
  };

  const getSuitabilityColor = (suitability) => {
    switch(suitability) {
      case 'Good': return '#4ade80';
      case 'Moderate': return '#fbbf24';
      case 'Poor': return '#f87171';
      default: return '#94a3b8';
    }
  };

  const getScoreColor = (score) => {
    if (score >= 0.7) return '#4ade80';
    if (score >= 0.4) return '#fbbf24';
    return '#f87171';
  };

  return (
    <div className="crop-recommendation">
      {/* Header */}
      <div className="crop-header">
        <button className="back-button" onClick={() => onNavigate('dashboard')}>
          ← Back to Dashboard
        </button>
        <h1 className="crop-title">🌾 Smart Crop Recommendation</h1>
        <p className="crop-subtitle">Enter NPK & pH values + Arduino sensor data for crop recommendations</p>
      </div>

      <div className="crop-content">
        {/* Arduino Sensor Display */}
        <div className="sensor-section">
          <div className="sensor-card">
            <h2>🌡️ Live Arduino Sensors</h2>
            
            {/* Arduino Connection Status */}
            <div className={`arduino-status ${arduinoStatus.connected ? 'connected' : 'disconnected'}`}>
              {arduinoStatus.connected ? '✅ ' : '❌ '}
              {arduinoStatus.message || (arduinoStatus.connected ? 'Arduino Connected' : 'Waiting for real Arduino values...')}
            </div>
            
            <div className="sensor-grid">
              <div className="sensor-item">
                <span className="sensor-icon">🌡️</span>
                <div className="sensor-info">
                  <div className="sensor-value">
                    {sensorLoading ? '...' : 
                     arduinoSensors.temperature !== null ? `${arduinoSensors.temperature.toFixed(1)}°C` : 
                     'Waiting for Arduino...'}
                  </div>
                  <div className="sensor-label">Temperature</div>
                </div>
              </div>
              <div className="sensor-item">
                <span className="sensor-icon">💧</span>
                <div className="sensor-info">
                  <div className="sensor-value">
                    {sensorLoading ? '...' : 
                     arduinoSensors.humidity !== null ? `${arduinoSensors.humidity.toFixed(1)}%` : 
                     'Waiting for Arduino...'}
                  </div>
                  <div className="sensor-label">Humidity</div>
                </div>
              </div>
              <div className="sensor-item">
                <span className="sensor-icon">🌱</span>
                <div className="sensor-info">
                  <div className="sensor-value">
                    {sensorLoading ? '...' : 
                     arduinoSensors.soil_moisture !== null ? `${arduinoSensors.soil_moisture.toFixed(1)}%` : 
                     'Waiting for Arduino...'}
                  </div>
                  <div className="sensor-label">Soil Moisture</div>
                </div>
              </div>
            </div>
            {arduinoSensors.timestamp && (
              <div className="sensor-timestamp">
                Last updated: {new Date(arduinoSensors.timestamp).toLocaleString()}
              </div>
            )}
          </div>
        </div>

        {/* Pump Control */}
        <div className="pump-section">
          <div className="pump-card">
            <h2>🚰 Pump Control</h2>
            <div className="pump-controls">
              <button 
                className={`pump-button ${pumpStatus === 'ON' ? 'active' : ''}`}
                onClick={() => controlPump('ON')}
                disabled={pumpStatus === 'ON'}
              >
                💧 Turn ON
              </button>
              <button 
                className={`pump-button ${pumpStatus === 'OFF' ? 'active' : ''}`}
                onClick={() => controlPump('OFF')}
                disabled={pumpStatus === 'OFF'}
              >
                ⏹️ Turn OFF
              </button>
            </div>
            <div className="pump-status">
              Current Status: <span className={`status-indicator ${pumpStatus.toLowerCase()}`}>{pumpStatus}</span>
            </div>
          </div>
        </div>

        {/* Input Form */}
        <div className="input-section">
          <div className="input-card">
            <h2>🧪 Soil Analysis Input (User Input)</h2>
            <form onSubmit={handleSubmit} className="soil-form">
              <div className="form-grid">
                <div className="form-group">
                  <label htmlFor="nitrogen">Nitrogen (mg/kg)</label>
                  <input
                    type="number"
                    id="nitrogen"
                    name="nitrogen"
                    value={soilData.nitrogen}
                    onChange={handleInputChange}
                    min="0"
                    max="200"
                    step="0.1"
                    required
                    placeholder="0-200"
                    className="form-input"
                  />
                  <span className="input-hint">Typical range: 0-200 mg/kg</span>
                </div>

                <div className="form-group">
                  <label htmlFor="phosphorus">Phosphorus (mg/kg)</label>
                  <input
                    type="number"
                    id="phosphorus"
                    name="phosphorus"
                    value={soilData.phosphorus}
                    onChange={handleInputChange}
                    min="0"
                    max="100"
                    step="0.1"
                    required
                    placeholder="0-100"
                    className="form-input"
                  />
                  <span className="input-hint">Typical range: 0-100 mg/kg</span>
                </div>

                <div className="form-group">
                  <label htmlFor="potassium">Potassium (mg/kg)</label>
                  <input
                    type="number"
                    id="potassium"
                    name="potassium"
                    value={soilData.potassium}
                    onChange={handleInputChange}
                    min="0"
                    max="300"
                    step="0.1"
                    required
                    placeholder="0-300"
                    className="form-input"
                  />
                  <span className="input-hint">Typical range: 0-300 mg/kg</span>
                </div>

                <div className="form-group">
                  <label htmlFor="ph">pH Level</label>
                  <input
                    type="number"
                    id="ph"
                    name="ph"
                    value={soilData.ph}
                    onChange={handleInputChange}
                    min="4"
                    max="10"
                    step="0.1"
                    required
                    placeholder="4.0-10.0"
                    className="form-input"
                  />
                  <span className="input-hint">Typical range: 4.0-10.0</span>
                </div>
              </div>

              <button type="submit" className="submit-button" disabled={loading || !arduinoStatus.connected}>
                {loading ? (
                  <>
                    <span className="button-spinner"></span>
                    Analyzing Soil...
                  </>
                ) : (
                  <>
                    🌱 Get Recommendations
                  </>
                )}
              </button>
              {!arduinoStatus.connected && (
                <div className="arduino-warning">
                  ⚠️ Arduino not connected. Real sensor data required for recommendations.
                </div>
              )}
            </form>
          </div>
        </div>

        {/* Results Section */}
        <div className="results-section">
          {loading && (
            <div className="loading">
              <div className="loading-animation">
                <div className="soil-particle"></div>
                <div className="soil-particle"></div>
                <div className="soil-particle"></div>
              </div>
              <p>Analyzing your soil data and finding best crops...</p>
            </div>
          )}

          {error && (
            <div className="error">
              <span className="error-icon">❌</span>
              <p>{error}</p>
            </div>
          )}

          {recommendations && !loading && (
            <div className="recommendations-results">
              {/* Top Recommendation */}
              <div className="top-recommendation">
                <h2>🏆 Top Recommendation</h2>
                <div className="top-crop-card">
                  <div className="top-crop-image">
                    <img 
                      src={cropImages[recommendations.top_recommendation.toLowerCase()]} 
                      alt={recommendations.top_recommendation}
                    />
                    <div className="crop-emoji">
                      {cropEmojis[recommendations.top_recommendation.toLowerCase()]}
                    </div>
                  </div>
                  <div className="top-crop-info">
                    <h3>{recommendations.top_recommendation}</h3>
                    <div className="top-crop-stats">
                      <div className="stat">
                        <span className="stat-label">Suitability:</span>
                        <span 
                          className="stat-value"
                          style={{ color: getSuitabilityColor(
                            recommendations.crop_recommendations[0]?.suitability
                          )}}
                        >
                          {recommendations.crop_recommendations[0]?.suitability}
                        </span>
                      </div>
                      <div className="stat">
                        <span className="stat-label">Score:</span>
                        <span 
                          className="stat-value"
                          style={{ color: getScoreColor(
                            recommendations.crop_recommendations[0]?.score
                          )}}
                        >
                          {((recommendations.crop_recommendations[0]?.score || 0) * 100).toFixed(1)}%
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* All Recommendations */}
              <div className="all-recommendations">
                <h2>📊 All Crop Recommendations</h2>
                <div className="crops-grid">
                  {recommendations.crop_recommendations.map((crop, index) => (
                    <div key={index} className="crop-card">
                      <div className="crop-image">
                        <img 
                          src={cropImages[crop.name.toLowerCase()]} 
                          alt={crop.name}
                        />
                        <div className="crop-emoji">
                          {cropEmojis[crop.name.toLowerCase()]}
                        </div>
                        <div className="crop-rank">#{index + 1}</div>
                      </div>
                      <div className="crop-info">
                        <h3>{crop.name}</h3>
                        <div className="crop-score">
                          <div className="score-bar">
                            <div 
                              className="score-fill"
                              style={{ 
                                width: `${(crop.score || 0) * 100}%`,
                                backgroundColor: getScoreColor(crop.score || 0)
                              }}
                            ></div>
                          </div>
                          <span className="score-text">{((crop.score || 0) * 100).toFixed(1)}%</span>
                        </div>
                        <div className="suitability-badge" style={{ 
                          backgroundColor: getSuitabilityColor(crop.suitability),
                          color: 'white'
                        }}>
                          {crop.suitability}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Soil Analysis */}
              <div className="soil-analysis">
                <h2>🧪 Soil Analysis Summary</h2>
                <div className="analysis-grid">
                  <div className="analysis-item">
                    <span className="analysis-label">User Input - Nitrogen:</span>
                    <span className="analysis-value">{recommendations.input_data?.nitrogen_mg_kg} mg/kg</span>
                  </div>
                  <div className="analysis-item">
                    <span className="analysis-label">User Input - Phosphorus:</span>
                    <span className="analysis-value">{recommendations.input_data?.phosphorus_mg_kg} mg/kg</span>
                  </div>
                  <div className="analysis-item">
                    <span className="analysis-label">User Input - Potassium:</span>
                    <span className="analysis-value">{recommendations.input_data?.potassium_mg_kg} mg/kg</span>
                  </div>
                  <div className="analysis-item">
                    <span className="analysis-label">User Input - pH:</span>
                    <span className="analysis-value">{recommendations.input_data?.ph_value}</span>
                  </div>
                  <div className="analysis-item">
                    <span className="analysis-label">Arduino - Temperature:</span>
                    <span className="analysis-value">{recommendations.input_data?.temperature_c}°C</span>
                  </div>
                  <div className="analysis-item">
                    <span className="analysis-label">Arduino - Humidity:</span>
                    <span className="analysis-value">{recommendations.input_data?.humidity_percent}%</span>
                  </div>
                  <div className="analysis-item">
                    <span className="analysis-label">Arduino - Soil Moisture:</span>
                    <span className="analysis-value">{recommendations.input_data?.soil_moisture_percent}%</span>
                  </div>
                </div>
              </div>

              {/* Price Prediction Button */}
              <div className="price-prediction-section">
                <h2>💰 Price Prediction & Profit Analysis</h2>
                <div className="price-input-section">
                  <div className="acres-input">
                    <label htmlFor="acres">Number of Acres:</label>
                    <input
                      type="number"
                      id="acres"
                      value={acres}
                      onChange={(e) => setAcres(parseFloat(e.target.value) || 1)}
                      min="1"
                      max="100"
                      step="0.5"
                      className="acres-input-field"
                    />
                  </div>
                  <button 
                    className="price-button"
                    onClick={() => setShowPriceDashboard(true)}
                  >
                    📊 View Price Prediction for {recommendations.top_recommendation}
                  </button>
                </div>
              </div>

              {/* Price Prediction Dashboard */}
              {showPriceDashboard && (
                <div className="price-dashboard-wrapper">
                  <button 
                    className="close-dashboard-button"
                    onClick={() => setShowPriceDashboard(false)}
                  >
                    ✕ Close Price Dashboard
                  </button>
                  <PricePredictionDashboard 
                    cropName={recommendations.top_recommendation} 
                    acres={acres}
                  />
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CropRecommendation;
