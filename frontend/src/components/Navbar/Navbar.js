import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import './Navbar.css';

const Navbar = () => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const location = useLocation();

  const navItems = [
    { path: '/', label: 'Home', icon: '🏠' },
    { path: '/my-farm', label: 'My Farm', icon: '🌾' },
    { path: '/crop-recommendation', label: 'Crop Recommendation', icon: '🌱' },
    { path: '/market-prices', label: 'Market Prices', icon: '💰' },
    { path: '/crop-calendar', label: 'Crop Calendar', icon: '📅' },
    { path: '/farm-activities', label: 'Activities', icon: '📝' },
    { path: '/crop-health', label: 'Crop Health', icon: '📷' },
    { path: '/weather', label: 'Weather', icon: '🌦️' },
    { path: '/profit-analytics', label: 'Analytics', icon: '📊' },
    { path: '/sell-produce', label: 'Sell Produce', icon: '🚜' },
    { path: '/farmer-assistant', label: 'Assistant', icon: '🤖' },
    { path: '/profile', label: 'Profile', icon: '👤' },
  ];

  const toggleMobileMenu = () => {
    setMobileMenuOpen(!mobileMenuOpen);
  };

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <div className="navbar-brand">
          <Link to="/" className="brand-link">
            <span className="brand-icon">🌱</span>
            <span className="brand-text">Smart Farmer</span>
          </Link>
        </div>

        <button 
          className="mobile-menu-toggle"
          onClick={toggleMobileMenu}
          aria-label="Toggle menu"
        >
          <span className="hamburger"></span>
        </button>

        <ul className={`navbar-nav ${mobileMenuOpen ? 'mobile-open' : ''}`}>
          {navItems.map((item) => (
            <li key={item.path} className="nav-item">
              <Link
                to={item.path}
                className={`nav-link ${location.pathname === item.path ? 'active' : ''}`}
                onClick={() => setMobileMenuOpen(false)}
              >
                <span className="nav-icon">{item.icon}</span>
                <span className="nav-label">{item.label}</span>
              </Link>
            </li>
          ))}
        </ul>
      </div>
    </nav>
  );
};

export default Navbar;
