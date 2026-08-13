import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMapEvents, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import axios from 'axios';
import TeaPredictionDashboard from './TeaPredictionDashboard';
import './TeaPrediction.css';

// Fix Leaflet default icon issue
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});

const TeaPrediction = ({ onNavigate }) => {
  const [selectedLocation, setSelectedLocation] = useState(null);
  const [predictionData, setPredictionData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchSuggestions, setSearchSuggestions] = useState([]);
  const [selectedMonth, setSelectedMonth] = useState(new Date().getMonth() + 1);
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());
  const [targetLocation, setTargetLocation] = useState(null);
  const [searchTimeout, setSearchTimeout] = useState(null);

  const indiaBounds = [
    [6.7, 68.7],
    [37.1, 97.4]
  ];

  const defaultCenter = [20.5937, 78.9629];
  const defaultZoom = 5;

  // Component to handle map clicks
  const MapClickHandler = () => {
    useMapEvents({
      click: (e) => {
        const { lat, lng } = e.latlng;
        handleLocationSelect(lat, lng);
      },
    });
    return null;
  };

  // Component to handle auto-zoom
  const MapZoomHandler = () => {
    const map = useMap();
    
    useEffect(() => {
      if (targetLocation) {
        map.setView([targetLocation.lat, targetLocation.lng], 10);
        setTargetLocation(null);
      }
    }, [targetLocation, map]);
    
    return null;
  };

  const handleLocationSelect = async (lat, lng) => {
    setSelectedLocation({ latitude: lat, longitude: lng });
    setPredictionData(null);
    setError(null);
    setTargetLocation({ lat, lng });
    await fetchPrediction(lat, lng, selectedMonth, selectedYear);
  };

  const handleLocationSearch = async () => {
    if (!searchQuery.trim()) return;
    
    try {
      const response = await axios.get(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(searchQuery)}&limit=5`);
      setSearchSuggestions(response.data);
      
      // Auto-select first result if exact match found
      if (response.data.length === 1) {
        const suggestion = response.data[0];
        handleSuggestionSelect(suggestion);
      }
    } catch (err) {
      console.error('Location search failed:', err);
      setError('Location search failed. Please try again.');
    }
  };

  const handleLocationInput = async (e) => {
    const query = e.target.value;
    setSearchQuery(query);
    
    // Auto-search when user stops typing for 500ms
    if (searchTimeout) {
      clearTimeout(searchTimeout);
    }
    
    if (query.trim().length > 2) {
      const timeoutId = setTimeout(async () => {
        try {
          const response = await axios.get(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&limit=3`);
          setSearchSuggestions(response.data);
          
          // Auto-select if exact match found
          if (response.data.length === 1) {
            const suggestion = response.data[0];
            handleSuggestionSelect(suggestion);
          }
        } catch (err) {
          console.error('Auto-search failed:', err);
        }
      }, 500);
      setSearchTimeout(timeoutId);
    } else {
      setSearchSuggestions([]);
    }
  };

  const handleSuggestionSelect = (suggestion) => {
    const lat = suggestion.lat || suggestion.lat_lon?.split(',')[0] || 0;
    const lon = suggestion.lon || suggestion.lat_lon?.split(',')[1] || 0;
    setSearchQuery(suggestion.display_name);
    setSearchSuggestions([]);
    handleLocationSelect(parseFloat(lat), parseFloat(lon));
  };

  const handleUseMyLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const { latitude, longitude } = position.coords;
          if (
            latitude >= 6.7 &&
            latitude <= 37.1 &&
            longitude >= 68.7 &&
            longitude <= 97.4
          ) {
            setTargetLocation({ lat: latitude, lng: longitude });
            handleLocationSelect(latitude, longitude);
          } else {
            setError('Your location is outside India. Please select a location within India.');
          }
        },
        (error) => {
          setError('Unable to get your location. Please enable location services or search for a location.');
        }
      );
    } else {
      setError('Geolocation is not supported by your browser.');
    }
  };

  const fetchPrediction = async (lat, lng, month, year) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.post('http://127.0.0.1:5002/tea-predict', {
        latitude: lat,
        longitude: lng,
        month: month
      });
      
      setPredictionData(response.data);
      
      // Log for debugging
      console.log('📊 Prediction Response:', response.data);
      console.log('🌤️ Weather Data:', response.data.weather_data);
      console.log('🧮 Calculated Features:', response.data.calculated_features);
      
    } catch (err) {
      console.error('❌ Prediction Error:', err);
      setError(err.response?.data?.error || 'Failed to fetch prediction');
    } finally {
      setLoading(false);
    }
  };

  const months = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];

  const currentYear = new Date().getFullYear();
  const currentMonth = new Date().getMonth() + 1;
  const years = Array.from({ length: 3 }, (_, i) => currentYear - 2 + i);

  return (
    <div className="tea-prediction">
      {/* Header */}
      <div className="tea-header">
        <button className="back-button" onClick={() => onNavigate('dashboard')}>
          ← Back to Dashboard
        </button>
        <h1 className="tea-title">🍃 Tea Production Prediction</h1>
        <p className="tea-subtitle">Predict tea crop yield based on location and weather conditions</p>
      </div>

      <div className="tea-content">
        {/* Controls Section */}
        <div className="controls-section">
          {/* Location Search Card */}
          <div className="location-card">
            <div className="card-header">
              <h3>📍 Select Location</h3>
              <p>Choose your tea plantation location</p>
            </div>
            
            <div className="location-options">
              {/* Quick Location Buttons */}
              <div className="quick-locations">
                <h4>🌍 Popular Tea Regions</h4>
                <div className="location-buttons-grid">
                  <button 
                    className="quick-location-btn"
                    onClick={() => handleLocationSelect(26.5, 92.7)}
                  >
                    <span className="location-icon">🍃</span>
                    <span className="location-name">Assam</span>
                    <span className="location-coords">26.5°N, 92.7°E</span>
                  </button>
                  <button 
                    className="quick-location-btn"
                    onClick={() => handleLocationSelect(27.0, 88.0)}
                  >
                    <span className="location-icon">🍃</span>
                    <span className="location-name">Darjeeling</span>
                    <span className="location-coords">27.0°N, 88.0°E</span>
                  </button>
                  <button 
                    className="quick-location-btn"
                    onClick={() => handleLocationSelect(13.0, 80.0)}
                  >
                    <span className="location-icon">🍃</span>
                    <span className="location-name">Nilgiri</span>
                    <span className="location-coords">13.0°N, 80.0°E</span>
                  </button>
                  <button 
                    className="quick-location-btn"
                    onClick={() => handleLocationSelect(10.0, 77.0)}
                  >
                    <span className="location-icon">🍃</span>
                    <span className="location-name">Munnar</span>
                    <span className="location-coords">10.0°N, 77.0°E</span>
                  </button>
                </div>
              </div>

              {/* Custom Location Search */}
              <div className="custom-location">
                <h4>🔍 Custom Location</h4>
                <div className="search-container">
                  <div className="search-input-wrapper">
                    <input
                      type="text"
                      placeholder="Search any location (city, state, country)"
                      value={searchQuery}
                      onChange={handleLocationInput}
                      className="location-search-input"
                      onKeyPress={(e) => e.key === 'Enter' && handleLocationSearch()}
                    />
                    <button 
                      className="search-action-btn"
                      onClick={handleLocationSearch}
                      disabled={!searchQuery.trim()}
                    >
                      🔍
                    </button>
                  </div>
                  
                  {searchSuggestions.length > 0 && (
                    <div className="suggestions-dropdown">
                      {searchSuggestions.map((suggestion, index) => (
                        <div
                          key={index}
                          className="suggestion-item"
                          onClick={() => handleSuggestionSelect(suggestion)}
                        >
                          <div className="suggestion-info">
                            <span className="suggestion-name">{suggestion.display_name}</span>
                            <span className="suggestion-details">
                              {typeof suggestion.lat === 'number' ? suggestion.lat.toFixed(4) : parseFloat(suggestion.lat || 0).toFixed(4)}°N, {typeof suggestion.lon === 'number' ? suggestion.lon.toFixed(4) : parseFloat(suggestion.lon || 0).toFixed(4)}°E
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* Current Location Button */}
                <button 
                  className="current-location-btn"
                  onClick={handleUseMyLocation}
                >
                  <span className="btn-icon">📍</span>
                  <span className="btn-text">Use My Current Location</span>
                </button>
              </div>
            </div>
          </div>

          {/* Date Selection Card */}
          <div className="date-card">
            <div className="card-header">
              <h3>📅 Select Time Period</h3>
              <p>Choose month and year for prediction</p>
            </div>
            
            <div className="date-selection">
              <div className="date-picker">
                <label className="date-label">
                  <span className="label-icon">📆</span>
                  <span className="label-text">Month</span>
                </label>
                <select 
                  value={selectedMonth} 
                  onChange={(e) => setSelectedMonth(parseInt(e.target.value))}
                  className="date-select"
                >
                  {months.map((month, index) => (
                    <option key={index} value={index + 1}>{month}</option>
                  ))}
                </select>
              </div>
              
              <div className="date-picker">
                <label className="date-label">
                  <span className="label-icon">📅</span>
                  <span className="label-text">Year</span>
                </label>
                <select 
                  value={selectedYear} 
                  onChange={(e) => setSelectedYear(parseInt(e.target.value))}
                  className="date-select"
                >
                  {years.map(year => (
                    <option key={year} value={year}>{year}</option>
                  ))}
                </select>
              </div>
            </div>

            {/* Selected Location Display */}
            {selectedLocation && (
              <div className="selected-location-display">
                <h4>📍 Calculated Location Coordinates</h4>
                <div className="location-details">
                  <div className="location-coord">
                    <span className="coord-label">🌍 Latitude:</span>
                    <span className="coord-value">{selectedLocation.latitude.toFixed(4)}°N</span>
                    <span className="coord-badge">Auto-Calculated</span>
                  </div>
                  <div className="location-coord">
                    <span className="coord-label">🌍 Longitude:</span>
                    <span className="coord-value">{selectedLocation.longitude.toFixed(4)}°E</span>
                    <span className="coord-badge">Auto-Calculated</span>
                  </div>
                </div>
              </div>
            )}

            {/* Weather Details Display */}
            {predictionData && (
              <div className="weather-details-display">
                <h4>
                  {predictionData.weather_data ? '🌤️ Current Weather Conditions' : '🔧 Weather Data Unavailable (Using Calculated Values)'}
                </h4>
                <div className="weather-grid">
                  <div className="weather-item">
                    <span className="weather-icon">🌡️</span>
                    <div className="weather-info">
                      <span className="weather-value">
                        {predictionData.weather_data ? 
                          (predictionData.weather_data.temperature?.toFixed(1) || 'N/A') :
                          (predictionData.all_features?.Temperature_C?.toFixed(1) || 'N/A')
                        }°C
                      </span>
                      <span className="weather-label">Temperature</span>
                    </div>
                  </div>
                  <div className="weather-item">
                    <span className="weather-icon">💧</span>
                    <div className="weather-info">
                      <span className="weather-value">
                        {predictionData.weather_data ? 
                          (predictionData.weather_data.humidity?.toFixed(1) || 'N/A') :
                          (predictionData.all_features?.Humidity_Percent?.toFixed(1) || 'N/A')
                        }%
                      </span>
                      <span className="weather-label">Humidity</span>
                    </div>
                  </div>
                  <div className="weather-item">
                    <span className="weather-icon">🌧️</span>
                    <div className="weather-info">
                      <span className="weather-value">
                        {predictionData.weather_data ? 
                          (predictionData.weather_data.precipitation?.toFixed(2) || 'N/A') :
                          (predictionData.all_features?.Precipitation_mm_day?.toFixed(2) || 'N/A')
                        } mm
                      </span>
                      <span className="weather-label">Precipitation</span>
                    </div>
                  </div>
                  <div className="weather-item">
                    <span className="weather-icon">☀️</span>
                    <div className="weather-info">
                      <span className="weather-value">
                        {predictionData.weather_data ? 
                          (predictionData.weather_data.solar_radiation?.toFixed(2) || 'N/A') :
                          (predictionData.all_features?.Solar_Radiation_MJ_m2_day?.toFixed(2) || 'N/A')
                        } MJ/m²
                      </span>
                      <span className="weather-label">Solar Radiation</span>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Map Section */}
        <div className="map-section">
          <div className="map-container">
            <MapContainer
              center={selectedLocation ? [selectedLocation.latitude, selectedLocation.longitude] : defaultCenter}
              zoom={selectedLocation ? 10 : defaultZoom}
              bounds={indiaBounds}
              style={{ height: '500px', width: '100%' }}
            >
              <TileLayer
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
              />
              <MapClickHandler />
              <MapZoomHandler />
              {selectedLocation && (
                <Marker position={[selectedLocation.latitude, selectedLocation.longitude]}>
                  <Popup>
                    <div className="popup-content">
                      <strong>Selected Location</strong><br />
                      Lat: {selectedLocation.latitude.toFixed(4)}<br />
                      Lng: {selectedLocation.longitude.toFixed(4)}
                    </div>
                  </Popup>
                </Marker>
              )}
            </MapContainer>
          </div>
        </div>

        {/* Main Prediction Button */}
        <div className="main-prediction-section">
          <h2>🍃 Tea Production Prediction</h2>
          <button 
            className="main-predict-button"
            onClick={() => selectedLocation && fetchPrediction(selectedLocation.latitude, selectedLocation.longitude, selectedMonth, selectedYear)}
            disabled={loading || !selectedLocation}
          >
            {loading ? '🔄 Predicting...' : '🚀 Get Tea Production Prediction'}
          </button>
        </div>

        {/* Results Section */}
        <div className="results-section">
          {loading && (
            <div className="loading">
              <p>Analyzing location and predicting tea production...</p>
            </div>
          )}

          {error && (
            <div className="error">
              <span className="error-icon">❌</span>
              <p>{error}</p>
            </div>
          )}

          <TeaPredictionDashboard 
            predictionData={predictionData}
            loading={loading}
            error={error}
          />
        </div>
      </div>
    </div>
  );
};

export default TeaPrediction;
