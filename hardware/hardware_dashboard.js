/**
 * Hardware Dashboard Component
 * Real-time IoT sensor data visualization
 */

import React, { useState, useEffect } from 'react';
import axios from 'axios';

const HardwareDashboard = () => {
  const [devices, setDevices] = useState([]);
  const [sensorData, setSensorData] = useState({});
  const [selectedDevice, setSelectedDevice] = useState(null);
  const [loading, setLoading] = useState(true);
  const [connectionStatus, setConnectionStatus] = useState('connected');

  // Fetch devices and sensor data
  useEffect(() => {
    fetchDevices();
    fetchLatestSensorData();
    
    // Set up real-time updates
    const interval = setInterval(() => {
      fetchLatestSensorData();
    }, 30000); // Update every 30 seconds
    
    return () => clearInterval(interval);
  }, []);

  const fetchDevices = async () => {
    try {
      const response = await axios.get('http://localhost:5001/api/devices');
      setDevices(response.data.devices || []);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching devices:', error);
      setConnectionStatus('disconnected');
      setLoading(false);
    }
  };

  const fetchLatestSensorData = async () => {
    try {
      const response = await axios.get('http://localhost:5001/api/sensor-data/latest');
      const data = response.data.data || [];
      
      // Organize data by device
      const organizedData = {};
      data.forEach(item => {
        organizedData[item.device_id] = item;
      });
      
      setSensorData(organizedData);
      setConnectionStatus('connected');
    } catch (error) {
      console.error('Error fetching sensor data:', error);
      setConnectionStatus('disconnected');
    }
  };

  const fetchDeviceHistory = async (deviceId) => {
    try {
      const response = await axios.get(
        `http://localhost:5001/api/sensor-data/history?device_id=${deviceId}&hours=24`
      );
      return response.data.data || [];
    } catch (error) {
      console.error('Error fetching device history:', error);
      return [];
    }
  };

  const getStatusColor = (battery) => {
    if (battery > 3.7) return '#4CAF50'; // Green
    if (battery > 3.3) return '#FF9800'; // Orange
    return '#F44336'; // Red
  };

  const getSignalStrength = (lastSeen) => {
    const now = new Date();
    const lastSeenTime = new Date(lastSeen);
    const diffMinutes = (now - lastSeenTime) / (1000 * 60);
    
    if (diffMinutes < 5) return { strength: 'Strong', color: '#4CAF50' };
    if (diffMinutes < 30) return { strength: 'Medium', color: '#FF9800' };
    return { strength: 'Weak', color: '#F44336' };
  };

  const DeviceCard = ({ device }) => {
    const deviceData = sensorData[device.id];
    const signal = getSignalStrength(device.last_seen);
    
    return (
      <div 
        className="device-card"
        onClick={() => setSelectedDevice(device)}
        style={{ cursor: 'pointer' }}
      >
        <div className="device-header">
          <h3>{device.name || `Device ${device.id}`}</h3>
          <div className="device-status">
            <span className="signal-indicator" style={{ color: signal.color }}>
              {signal.strength}
            </span>
            <span className="battery-indicator" style={{ color: getStatusColor(device.battery_level) }}>
              {device.battery_level ? `${device.battery_level.toFixed(1)}V` : 'N/A'}
            </span>
          </div>
        </div>
        
        <div className="device-location">
          <span>Lat: {device.latitude?.toFixed(4) || 'N/A'}</span>
          <span>Lng: {device.longitude?.toFixed(4) || 'N/A'}</span>
        </div>
        
        {deviceData && (
          <div className="sensor-readings">
            <div className="reading-item">
              <span className="reading-label">Temp:</span>
              <span className="reading-value">{deviceData.temperature?.toFixed(1)}°C</span>
            </div>
            <div className="reading-item">
              <span className="reading-label">Humidity:</span>
              <span className="reading-value">{deviceData.humidity?.toFixed(1)}%</span>
            </div>
            <div className="reading-item">
              <span className="reading-label">Soil:</span>
              <span className="reading-value">{deviceData.soil_moisture?.toFixed(1)}%</span>
            </div>
            <div className="reading-item">
              <span className="reading-label">Rain:</span>
              <span className="reading-value">{deviceData.rainfall?.toFixed(1)}mm</span>
            </div>
          </div>
        )}
        
        <div className="device-footer">
          <span className="last-seen">
            Last seen: {new Date(device.last_seen).toLocaleString()}
          </span>
        </div>
      </div>
    );
  };

  const SensorChart = ({ deviceId }) => {
    const [chartData, setChartData] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
      if (deviceId) {
        loadChartData();
      }
    }, [deviceId]);

    const loadChartData = async () => {
      setLoading(true);
      const history = await fetchDeviceHistory(deviceId);
      setChartData(history.reverse()); // Show oldest to newest
      setLoading(false);
    };

    if (loading) return <div className="chart-loading">Loading chart data...</div>;

    return (
      <div className="sensor-chart">
        <h4>24-Hour Sensor History</h4>
        <div className="chart-container">
          {chartData.map((data, index) => (
            <div key={index} className="chart-data-point">
              <span className="timestamp">
                {new Date(data.timestamp).toLocaleTimeString()}
              </span>
              <span className="temp">{data.temperature?.toFixed(1)}°C</span>
              <span className="humidity">{data.humidity?.toFixed(1)}%</span>
              <span className="soil">{data.soil_moisture?.toFixed(1)}%</span>
            </div>
          ))}
        </div>
      </div>
    );
  };

  return (
    <div className="hardware-dashboard">
      <div className="dashboard-header">
        <h2>IoT Hardware Dashboard</h2>
        <div className="connection-status">
          <span className={`status-indicator ${connectionStatus}`}>
            {connectionStatus === 'connected' ? 'Connected' : 'Disconnected'}
          </span>
        </div>
      </div>

      <div className="dashboard-content">
        <div className="devices-panel">
          <h3>Active Devices ({devices.length})</h3>
          <div className="devices-grid">
            {devices.map(device => (
              <DeviceCard key={device.id} device={device} />
            ))}
          </div>
          
          {devices.length === 0 && !loading && (
            <div className="no-devices">
              <p>No devices connected. Check hardware setup.</p>
            </div>
          )}
          
          {loading && (
            <div className="loading-devices">
              <p>Loading devices...</p>
            </div>
          )}
        </div>

        <div className="details-panel">
          {selectedDevice ? (
            <div className="device-details">
              <h3>{selectedDevice.name || `Device ${selectedDevice.id}`}</h3>
              
              <div className="device-info">
                <div className="info-section">
                  <h4>Location</h4>
                  <p>Latitude: {selectedDevice.latitude?.toFixed(6)}</p>
                  <p>Longitude: {selectedDevice.longitude?.toFixed(6)}</p>
                </div>
                
                <div className="info-section">
                  <h4>Current Readings</h4>
                  {sensorData[selectedDevice.id] && (
                    <div className="current-readings">
                      <div className="reading">
                        <span>Temperature:</span>
                        <span>{sensorData[selectedDevice.id].temperature?.toFixed(1)}°C</span>
                      </div>
                      <div className="reading">
                        <span>Humidity:</span>
                        <span>{sensorData[selectedDevice.id].humidity?.toFixed(1)}%</span>
                      </div>
                      <div className="reading">
                        <span>Soil Moisture:</span>
                        <span>{sensorData[selectedDevice.id].soil_moisture?.toFixed(1)}%</span>
                      </div>
                      <div className="reading">
                        <span>Rainfall:</span>
                        <span>{sensorData[selectedDevice.id].rainfall?.toFixed(1)}mm</span>
                      </div>
                      <div className="reading">
                        <span>Light Intensity:</span>
                        <span>{sensorData[selectedDevice.id].light_intensity?.toFixed(0)} lux</span>
                      </div>
                      <div className="reading">
                        <span>Soil pH:</span>
                        <span>{sensorData[selectedDevice.id].soil_ph?.toFixed(1)}</span>
                      </div>
                      <div className="reading">
                        <span>Battery:</span>
                        <span>{sensorData[selectedDevice.id].battery_level?.toFixed(1)}V</span>
                      </div>
                    </div>
                  )}
                </div>
              </div>
              
              <SensorChart deviceId={selectedDevice.id} />
            </div>
          ) : (
            <div className="no-device-selected">
              <p>Select a device to view details</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default HardwareDashboard;
