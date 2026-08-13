import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { MapContainer, TileLayer, Marker, useMapEvents } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import './App.css';

function App() {
  const [selectedLocation, setSelectedLocation] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [weatherData, setWeatherData] = useState(null);
  const [features, setFeatures] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchSuggestions, setSearchSuggestions] = useState([]);
  const [selectedMonth, setSelectedMonth] = useState(new Date().getMonth() + 1);
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());

  // India boundaries
  const indiaBounds = [
    [6.7, 68.7],   // Southwest corner
    [37.1, 97.4]   // Northeast corner
  ];
  
  // Default center (center of India)
  const defaultCenter = [20.5937, 78.9629];

  const handleLocationSelect = async (lat, lng) => {
    setSelectedLocation({ latitude: lat, longitude: lng });
    setPrediction(null);
    setError(null);
    setWeatherData(null);
    setFeatures(null);
    await fetchPrediction(lat, lng, selectedMonth, selectedYear);
  };

  const handleUseMyLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const { latitude, longitude } = position.coords;
          // Check if location is within India
          if (latitude >= 6.7 && latitude <= 37.1 && longitude >= 68.7 && longitude <= 97.4) {
            handleLocationSelect(latitude, longitude);
          } else {
            setError('Location is outside India. Please select a location within India.');
          }
        },
        (error) => {
          setError('Unable to get your location. Please try selecting manually.');
        }
      );
    } else {
      setError('Geolocation is not supported by your browser.');
    }
  };

  const handleMapClick = (e) => {
    const { lat, lng } = e.latlng;
    handleLocationSelect(lat, lng);
  };

  const handleLocationSearch = async (query) => {
    if (query.length < 3) {
      setSearchSuggestions([]);
      return;
    }

    try {
      const response = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&countrycodes=in&limit=5`);
      const data = await response.json();
      
      if (data && data.length > 0) {
        setSearchSuggestions(data.map(item => ({
          name: item.display_name,
          lat: parseFloat(item.lat),
          lng: parseFloat(item.lon)
        })));
      } else {
        setSearchSuggestions([]);
      }
    } catch (err) {
      console.error('Search error:', err);
      setSearchSuggestions([]);
    }
  };

  const handleSuggestionClick = (suggestion) => {
    setSearchQuery(suggestion.name);
    setSearchSuggestions([]);
    handleLocationSelect(suggestion.lat, suggestion.lng);
  };

  useEffect(() => {
    const timeoutId = setTimeout(() => {
      handleLocationSearch(searchQuery);
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [searchQuery]);

  const fetchPrediction = async (lat, lng, month, year) => {
    setLoading(true);
    setError(null);

    try {
      const response = await axios.post('http://127.0.0.1:5002/tea-predict', {
        temperature: 25.5,
        humidity: 75.2,
        rainfall: 150.0,
        nitrogen: 45.0,
        phosphorus: 35.0,
        potassium: 50.0,
        ph: 6.5,
        soil_moisture: 65.0,
        wind_speed: 12.5,
        sunlight_hours: 8.0,
        altitude: 1200.0,
        latitude: lat,
        longitude: lng,
        soil_type: 2.0,
        season: month,
        fertilizer_used: 1.0,
        irrigation: 1.0
      });

      const data = response.data;
      setPrediction(data.prediction);
      setWeatherData(data.weather);
      setFeatures(data.features);
    } catch (err) {
      console.error('Prediction error:', err);
      if (err.response) {
        setError(err.response.data.error || 'Server error occurred');
      } else if (err.request) {
        setError('Unable to connect to the server. Please make sure the backend is running.');
      } else {
        setError('An unexpected error occurred');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <div className="container">
        <header className="header">
          <h1>🌧️ Rainfall-Based Tea Production Predictor</h1>
          <p>Predict tea production using historical rainfall patterns and location data</p>
        </header>

        <div className="main-content">
          <div className="map-section">
            <div className="map-controls">
              <div className="search-container">
                <input
                  type="text"
                  className="location-search"
                  placeholder="🔍 Search for a location in India..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
                {searchSuggestions.length > 0 && (
                  <div className="search-suggestions">
                    {searchSuggestions.map((suggestion, index) => (
                      <div 
                        key={index}
                        className="suggestion-item"
                        onClick={() => handleSuggestionClick(suggestion)}
                      >
                        {suggestion.name}
                      </div>
                    ))}
                  </div>
                )}
              </div>
              
              <div className="control-buttons">
                <div className="date-selection">
                  <label htmlFor="month-select">📅 Month:</label>
                  <select 
                    id="month-select"
                    className="month-select"
                    value={selectedMonth}
                    onChange={(e) => setSelectedMonth(parseInt(e.target.value))}
                    disabled={loading}
                  >
                    <option value={1}>January</option>
                    <option value={2}>February</option>
                    <option value={3}>March</option>
                    <option value={4}>April</option>
                    <option value={5}>May</option>
                    <option value={6}>June</option>
                    <option value={7}>July</option>
                    <option value={8}>August</option>
                    <option value={9}>September</option>
                    <option value={10}>October</option>
                    <option value={11}>November</option>
                    <option value={12}>December</option>
                  </select>
                  
                  <label htmlFor="year-select">📅 Year:</label>
                  <select 
                    id="year-select"
                    className="year-select"
                    value={selectedYear}
                    onChange={(e) => setSelectedYear(parseInt(e.target.value))}
                    disabled={loading}
                  >
                    <option value={2020}>2020</option>
                    <option value={2021}>2021</option>
                    <option value={2022}>2022</option>
                    <option value={2023}>2023</option>
                    <option value={2024}>2024</option>
                  </select>
                </div>
                
                <button 
                  className="gps-button" 
                  onClick={handleUseMyLocation}
                  disabled={loading}
                >
                  📍 Use My Location
                </button>
                {selectedLocation && (
                  <div className="selected-coords">
                    <strong>Selected Location:</strong><br />
                    Lat: {selectedLocation.latitude.toFixed(4)}, 
                    Lng: {selectedLocation.longitude.toFixed(4)}
                  </div>
                )}
              </div>
            </div>
            
            <div className="map-container">
              <MapContainer 
                center={defaultCenter} 
                zoom={5} 
                bounds={indiaBounds}
                maxBounds={indiaBounds}
                maxBoundsViscosity={1.0}
                style={{ height: '400px', width: '100%' }}
              >
                <TileLayer
                  url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                  attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                />
                {selectedLocation && (
                  <Marker 
                    position={[selectedLocation.latitude, selectedLocation.longitude]}
                  />
                )}
                <useMapEvents
                  eventHandlers={{
                    click: handleMapClick,
                  }}
                />
              </MapContainer>
            </div>
          </div>

          <div className="results-section">
            {loading && (
              <div className="loading">
                <div className="spinner"></div>
                <p>Analyzing weather data and predicting tea production...</p>
              </div>
            )}

            {error && (
              <div className="error">
                <strong>Error:</strong> {error}
                </div>
            )}

            {weatherData && !loading && (
              <div className="weather-card">
                <h3>🌧️ Rainfall Data (Primary Factor)</h3>
                <div className="weather-grid">
                  <div className="weather-item rainfall-primary">
                    <span className="weather-label">Total Rainfall:</span>
                    <span className="weather-value rainfall-highlight">{weatherData.rainfall} mm</span>
                  </div>
                  <div className="weather-item">
                    <span className="weather-label">Temperature:</span>
                    <span className="weather-value">{weatherData.temperature}°C</span>
                  </div>
                  <div className="weather-item">
                    <span className="weather-label">Humidity:</span>
                    <span className="weather-value">{weatherData.humidity}%</span>
                  </div>
                </div>
                <div className="data-source">
                  <span className="source-indicator">
                    {weatherData.rainfall !== 0 ? '📊 Historical Data' : '🌡️ Current Weather'}
                  </span>
                  <span className="source-text">
                    {weatherData.rainfall !== 0 ? `Using ${selectedMonth}/${selectedYear} historical rainfall` : 'Using current weather data'}
                  </span>
                </div>
              </div>
            )}

            {features && !loading && (
              <div className="features-card">
                <h3>🌧️ Rainfall-Focused ML Features</h3>
                <div className="features-grid">
                  <div className="feature-category primary-factor">
                    <h4>🌧️ PRIMARY FACTOR</h4>
                    <div className="feature-item rainfall-main">
                      <span className="feature-name">Total Rainfall:</span>
                      <span className="feature-value rainfall-primary">{features.Rainfall_mm} mm</span>
                    </div>
                    <div className="feature-item">
                      <span className="feature-name">Rainfall × Humidity:</span>
                      <span className="feature-value">{features.Rainfall_Humidity}</span>
                    </div>
                    <div className="feature-item">
                      <span className="feature-name">Heat Index:</span>
                      <span className="feature-value">{features.Heat_Index}</span>
                    </div>
                    <div className="feature-item">
                      <span className="feature-name">Temp × Humidity:</span>
                      <span className="feature-value">{features.Temp_Humidity}</span>
                    </div>
                  </div>
                  
                  <div className="feature-category secondary">
                    <h4>📍 Supporting Data</h4>
                    <div className="feature-item">
                      <span className="feature-name">Temperature:</span>
                      <span className="feature-value">{features.Temperature_C}°C</span>
                    </div>
                    <div className="feature-item">
                      <span className="feature-name">Humidity:</span>
                      <span className="feature-value">{features.Humidity_Percent}%</span>
                    </div>
                    <div className="feature-item">
                      <span className="feature-name">Latitude:</span>
                      <span className="feature-value">{features.Latitude}°</span>
                    </div>
                    <div className="feature-item">
                      <span className="feature-name">Longitude:</span>
                      <span className="feature-value">{features.Longitude}°</span>
                    </div>
                    <div className="feature-item">
                      <span className="feature-name">Elevation:</span>
                      <span className="feature-value">{features.Elevation_m} m</span>
                    </div>
                  </div>
                  
                  <div className="feature-category constant">
                    <h4>⚙️ Constant Values</h4>
                    <div className="feature-item">
                      <span className="feature-name">Solar Radiation:</span>
                      <span className="feature-value">15.0 MJ/m²</span>
                    </div>
                    <div className="feature-item">
                      <span className="feature-name">Temp × Solar:</span>
                      <span className="feature-value">{features.Temp_Solar}</span>
                    </div>
                    <div className="feature-item">
                      <span className="feature-name">Prev Month Production:</span>
                      <span className="feature-value">{features.Prev_Month_Production} MKgs</span>
                    </div>
                    <div className="feature-item">
                      <span className="feature-name">Prev 2-Month Production:</span>
                      <span className="feature-value">{features.Prev_2Month_Production} MKgs</span>
                    </div>
                    <div className="feature-item">
                      <span className="feature-name">3-Month Rolling Avg:</span>
                      <span className="feature-value">{features.Rolling_3Month_Avg} MKgs</span>
                    </div>
                    <div className="feature-item">
                      <span className="feature-name">State Encoded:</span>
                      <span className="feature-value">{features.State_Encoded}</span>
                    </div>
                    <div className="feature-item">
                      <span className="feature-name">Month (Sin):</span>
                      <span className="feature-value">{features.Month_Sin}</span>
                    </div>
                    <div className="feature-item">
                      <span className="feature-name">Month (Cos):</span>
                      <span className="feature-value">{features.Month_Cos}</span>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {prediction && !loading && (
              <div className="prediction-card">
                <h3>🍵 Production Prediction</h3>
                <div className="prediction-result">
                  <div className="prediction-value">
                    {prediction.production.toFixed(2)}
                  </div>
                  <div className="prediction-unit">
                    Metric Tons per Hectare
                  </div>
                  <p className="prediction-note">
                    Expected tea production based on current weather conditions and location
                  </p>
                </div>
              </div>
            )}

            {!selectedLocation && !loading && (
              <div className="instructions">
                <h3>How to Use:</h3>
                <ol>
                  <li>Click anywhere on map to select a location, or</li>
                  <li>Click "Use My Location" for automatic GPS detection</li>
                  <li>Wait for system to fetch weather data and predict production</li>
                </ol>
                <p className="note">
                  <strong>Note:</strong> The prediction uses historical rainfall data and a trained 
                  machine learning model to estimate expected tea production.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
