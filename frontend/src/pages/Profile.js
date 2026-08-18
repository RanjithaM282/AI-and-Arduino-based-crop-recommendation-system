import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import './Profile.css';

const Profile = () => {
  const [formData, setFormData] = useState({
    name: '',
    phone: '',
    state: '',
    district: '',
    taluk: '',
    village: '',
    farmSize: '',
    soilType: '',
    irrigationType: '',
    currentCrop: '',
    previousCrops: '',
  });

  const [useGPS, setUseGPS] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log('Profile data:', formData);
    // TODO: Send to backend API
    alert('Profile saved successfully!');
  };

  const handleGPSLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          console.log('GPS Location:', position.coords);
          setUseGPS(true);
          alert('Location captured successfully!');
        },
        (error) => {
          console.error('GPS Error:', error);
          alert('Could not get GPS location. Please enter manually.');
        }
      );
    } else {
      alert('Geolocation is not supported by your browser.');
    }
  };

  return (
    <div className="profile-page">
      <div className="profile-container">
        <div className="profile-header">
          <h1>Farmer Profile Setup</h1>
          <p>Tell us about yourself and your farm to get personalized recommendations</p>
        </div>

        <form className="profile-form" onSubmit={handleSubmit}>
          {/* Personal Information */}
          <section className="form-section">
            <h2>👤 Personal Information</h2>
            <div className="form-grid">
              <div className="form-group">
                <label htmlFor="name">Full Name *</label>
                <input
                  type="text"
                  id="name"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  required
                  placeholder="Enter your full name"
                />
              </div>

              <div className="form-group">
                <label htmlFor="phone">Phone Number *</label>
                <input
                  type="tel"
                  id="phone"
                  name="phone"
                  value={formData.phone}
                  onChange={handleChange}
                  required
                  placeholder="Enter phone number"
                />
              </div>
            </div>
          </section>

          {/* Location Information */}
          <section className="form-section">
            <h2>📍 Farm Location</h2>
            <div className="location-options">
              <button
                type="button"
                className={`gps-button ${useGPS ? 'active' : ''}`}
                onClick={handleGPSLocation}
              >
                📍 Use Current GPS Location
              </button>
              <span className="or-divider">OR</span>
            </div>

            <div className="form-grid">
              <div className="form-group">
                <label htmlFor="state">State *</label>
                <select

                  id="state"
                  name="state"
                  value={formData.state}
                  onChange={handleChange}
                  required
                >
                  <option value="">Select State</option>
                  <option value="Karnataka">Karnataka</option>
                  <option value="Tamil Nadu">Tamil Nadu</option>
                  <option value="Kerala">Kerala</option>
                  <option value="Andhra Pradesh">Andhra Pradesh</option>
                  <option value="Maharashtra">Maharashtra</option>
                  <option value="Other">Other</option>
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="district">District *</label>
                <input
                  type="text"
                  id="district"
                  name="district"
                  value={formData.district}
                  onChange={handleChange}
                  required
                  placeholder="Enter district"
                />
              </div>

              <div className="form-group">
                <label htmlFor="taluk">Taluk</label>
                <input
                  type="text"
                  id="taluk"
                  name="taluk"
                  value={formData.taluk}
                  onChange={handleChange}
                  placeholder="Enter taluk"
                />
              </div>

              <div className="form-group">
                <label htmlFor="village">Village</label>
                <input
                  type="text"
                  id="village"
                  name="village"
                  value={formData.village}
                  onChange={handleChange}
                  placeholder="Enter village"
                />
              </div>
            </div>
          </section>

          {/* Farm Information */}
          <section className="form-section">
            <h2>🌾 Farm Details</h2>
            <div className="form-grid">
              <div className="form-group">
                <label htmlFor="farmSize">Farm Size (Acres) *</label>
                <input
                  type="number"
                  id="farmSize"
                  name="farmSize"
                  value={formData.farmSize}
                  onChange={handleChange}
                  required
                  placeholder="Enter farm size in acres"
                  min="0"
                  step="0.1"
                />
              </div>

              <div className="form-group">
                <label htmlFor="soilType">Soil Type *</label>
                <select
                  id="soilType"
                  name="soilType"
                  value={formData.soilType}
                  onChange={handleChange}
                  required
                >
                  <option value="">Select Soil Type</option>
                  <option value="Red Soil">Red Soil</option>
                  <option value="Black Soil">Black Soil</option>
                  <option value="Alluvial Soil">Alluvial Soil</option>
                  <option value="Laterite Soil">Laterite Soil</option>
                  <option value="Sandy Soil">Sandy Soil</option>
                  <option value="Clay Soil">Clay Soil</option>
                  <option value="Loamy Soil">Loamy Soil</option>
                  <option value="Other">Other</option>
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="irrigationType">Irrigation Type *</label>
                <select
                  id="irrigationType"
                  name="irrigationType"
                  value={formData.irrigationType}
                  onChange={handleChange}
                  required
                >
                  <option value="">Select Irrigation Type</option>
                  <option value="Rainfed">Rainfed</option>
                  <option value="Well Irrigation">Well Irrigation</option>
                  <option value="Canal Irrigation">Canal Irrigation</option>
                  <option value="Drip Irrigation">Drip Irrigation</option>
                  <option value="Sprinkler Irrigation">Sprinkler Irrigation</option>
                  <option value="Tank Irrigation">Tank Irrigation</option>
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="currentCrop">Current Crop</label>
                <input
                  type="text"
                  id="currentCrop"
                  name="currentCrop"
                  value={formData.currentCrop}
                  onChange={handleChange}
                  placeholder="Enter current crop (if any)"
                />
              </div>

              <div className="form-group full-width">
                <label htmlFor="previousCrops">Previous Crops</label>
                <textarea
                  id="previousCrops"
                  name="previousCrops"
                  value={formData.previousCrops}
                  onChange={handleChange}
                  placeholder="List previous crops grown (comma separated)"
                  rows="3"
                />
              </div>
            </div>
          </section>

          {/* Form Actions */}
          <div className="form-actions">
            <button type="submit" className="btn btn-primary">
              Save Profile
            </button>
            <Link to="/" className="btn btn-secondary">
              Cancel
            </Link>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Profile;
