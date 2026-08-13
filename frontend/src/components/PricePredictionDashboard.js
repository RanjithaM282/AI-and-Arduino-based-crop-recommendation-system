import React, { useState, useEffect, useCallback } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell, BarChart, Bar, AreaChart, Area, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from 'recharts';
import './PricePredictionDashboard.css';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D'];

const PricePredictionDashboard = ({ cropName, acres = 1 }) => {
  const [priceData, setPriceData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [darkMode, setDarkMode] = useState(true);

  const fetchPricePrediction = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('http://127.0.0.1:5003/price-predict', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ crop_name: cropName, acres: acres }),
      });
      const data = await response.json();
      if (data.status === 'success') {
        setPriceData(data);
      } else {
        setError(data.error || 'Failed to fetch price prediction');
      }
    } catch (err) {
      setError('Failed to connect to price prediction server');
    } finally {
      setLoading(false);
    }
  }, [cropName, acres]);

  useEffect(() => {
    if (cropName) {
      fetchPricePrediction();
    }
  }, [cropName, acres, fetchPricePrediction]);

  if (loading) {
    return (
      <div className="price-dashboard-container">
        <p>Loading price prediction...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="price-dashboard-container">
        <div className="error-message">
          <span className="error-icon">⚠️</span>
          <p>{error}</p>
        </div>
      </div>
    );
  }

  if (!priceData) {
    return (
      <div className="price-dashboard-container">
        <div className="no-data">
          <p>Select a crop to see price prediction and profit analysis</p>
        </div>
      </div>
    );
  }

  const { profit_data, price_trend, crop_details, ai_insights } = priceData;

  // Prepare data for charts
  const profitBreakdown = [
    { name: 'Revenue', value: profit_data.total_revenue },
    { name: 'Cost', value: profit_data.total_cost },
    { name: 'Profit', value: profit_data.profit }
  ];

  // Monthly profit projection
  const monthlyProfit = [];
  const monthlyRevenue = profit_data.total_revenue / profit_data.growth_time_months;
  const monthlyCost = profit_data.total_cost / profit_data.growth_time_months;
  const monthlyNet = monthlyRevenue - monthlyCost;
  
  for (let i = 1; i <= profit_data.growth_time_months; i++) {
    monthlyProfit.push({
      month: `Month ${i}`,
      revenue: Math.round(monthlyRevenue),
      cost: Math.round(monthlyCost),
      profit: Math.round(monthlyNet)
    });
  }

  // Crop comparison radar data
  const radarData = [
    { subject: 'Profit', A: profit_data.profit / 10000, fullMark: 10 },
    { subject: 'Yield', A: profit_data.total_yield_tons / 10, fullMark: 5 },
    { subject: 'Growth Time', A: 12 / profit_data.growth_time_months, fullMark: 2 },
    { subject: 'Market Price', A: profit_data.market_price_per_ton / 1000, fullMark: 5 },
    { subject: 'Cost Efficiency', A: (profit_data.profit / profit_data.total_cost) * 10, fullMark: 5 }
  ];

  // ROI calculation
  const roi = ((profit_data.profit / profit_data.total_cost) * 100).toFixed(2);
  const breakEvenMonths = Math.ceil(profit_data.total_cost / monthlyNet);

  return (
    <div className={`price-dashboard-container ${darkMode ? 'dark-mode' : 'light-mode'}`}>
      <div className="dashboard-header">
        <div className="header-left">
          <h2>💰 Price Prediction & Profit Analysis</h2>
          <p className="crop-badge">{cropName.toUpperCase()}</p>
        </div>
        <button 
          className="theme-toggle"
          onClick={() => setDarkMode(!darkMode)}
        >
          {darkMode ? '☀️ Light Mode' : '🌙 Dark Mode'}
        </button>
      </div>

      {/* Key Metrics Cards */}
      <div className="metrics-grid">
        <div className="metric-card profit-card">
          <div className="metric-icon">📈</div>
          <div className="metric-content">
            <p className="metric-label">Total Profit</p>
            <p className="metric-value">₹{Math.abs(profit_data.profit).toLocaleString()}</p>
            <p className="metric-sub">{Math.abs(profit_data.profit_margin)}% margin</p>
          </div>
        </div>

        <div className="metric-card revenue-card">
          <div className="metric-icon">💵</div>
          <div className="metric-content">
            <p className="metric-label">Total Revenue</p>
            <p className="metric-value">₹{profit_data.total_revenue.toLocaleString()}</p>
            <p className="metric-sub">{profit_data.total_yield_tons} tons yield</p>
          </div>
        </div>

        <div className="metric-card cost-card">
          <div className="metric-icon">💸</div>
          <div className="metric-content">
            <p className="metric-label">Total Cost</p>
            <p className="metric-value">₹{profit_data.total_cost.toLocaleString()}</p>
            <p className="metric-sub">{profit_data.acres} acres</p>
          </div>
        </div>

        <div className="metric-card time-card">
          <div className="metric-icon">⏱️</div>
          <div className="metric-content">
            <p className="metric-label">Growth Time</p>
            <p className="metric-value">{profit_data.growth_time_months} months</p>
            <p className="metric-sub">Harvest period</p>
          </div>
        </div>
      </div>

      {/* Charts Section */}
      <div className="charts-section">
        {/* Price Trend Chart */}
        <div className="chart-container">
          <h3>📊 Price Trend (Last 12 Months)</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={price_trend}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" label={{ value: 'Month', position: 'insideBottom', offset: -5 }} />
              <YAxis label={{ value: 'Price (₹/ton)', angle: -90, position: 'insideLeft' }} />
              <Tooltip 
                formatter={(value) => [`₹${value.toFixed(2)}`, 'Price']}
                labelFormatter={(label) => `Month ${label}`}
              />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="price" 
                stroke="#8884d8" 
                strokeWidth={2}
                name="Market Price"
                dot={{ fill: '#8884d8' }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Profit Breakdown Pie Chart */}
        <div className="chart-container">
          <h3>🥧 Profit Breakdown</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={profitBreakdown}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {profitBreakdown.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip formatter={(value) => `₹${value.toLocaleString()}`} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Additional Charts Section */}
      <div className="charts-section">
        {/* Monthly Profit Area Chart */}
        <div className="chart-container">
          <h3>📈 Monthly Profit Projection</h3>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={monthlyProfit}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis label={{ value: 'Amount (₹)', angle: -90, position: 'insideLeft' }} />
              <Tooltip formatter={(value) => `₹${value.toLocaleString()}`} />
              <Legend />
              <Area type="monotone" dataKey="revenue" stackId="1" stroke="#8884d8" fill="#8884d8" name="Revenue" />
              <Area type="monotone" dataKey="cost" stackId="1" stroke="#82ca9d" fill="#82ca9d" name="Cost" />
              <Area type="monotone" dataKey="profit" stackId="2" stroke="#ffc658" fill="#ffc658" name="Net Profit" />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Radar Chart */}
        <div className="chart-container">
          <h3>🎯 Crop Performance Radar</h3>
          <ResponsiveContainer width="100%" height={300}>
            <RadarChart data={radarData}>
              <PolarGrid />
              <PolarAngleAxis dataKey="subject" />
              <PolarRadiusAxis />
              <Radar name={cropName} dataKey="A" stroke="#8884d8" fill="#8884d8" fillOpacity={0.6} />
              <Legend />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* ROI Calculator Section */}
      <div className="roi-section">
        <h3>💹 ROI & Investment Analysis</h3>
        <div className="roi-grid">
          <div className="roi-card">
            <span className="roi-label">ROI</span>
            <span className="roi-value">{Math.abs(roi)}%</span>
            <span className="roi-sub">Excellent investment potential</span>
          </div>
          <div className="roi-card">
            <span className="roi-label">Break-Even Point</span>
            <span className="roi-value">{Math.abs(breakEvenMonths)} months</span>
            <span className="roi-sub">Time to recover investment</span>
          </div>
          <div className="roi-card">
            <span className="roi-label">Monthly Profit</span>
            <span className="roi-value">₹{Math.abs(Math.round(monthlyNet)).toLocaleString()}</span>
            <span className="roi-sub">Average monthly earnings</span>
          </div>
          <div className="roi-card">
            <span className="roi-label">Annual Projection</span>
            <span className="roi-value">₹{Math.abs(monthlyNet * 12).toLocaleString()}</span>
            <span className="roi-sub">Yearly profit estimate</span>
          </div>
        </div>
      </div>

      {/* Crop Details Section */}
      <div className="crop-details-section">
        <h3>🌾 Crop Information</h3>
        <div className="details-grid">
          <div className="detail-item">
            <span className="detail-label">Description:</span>
            <span className="detail-value">{crop_details.description}</span>
          </div>
          <div className="detail-item">
            <span className="detail-label">Market Price:</span>
            <span className="detail-value">₹{profit_data.market_price_per_ton}/ton</span>
          </div>
          <div className="detail-item">
            <span className="detail-label">Yield per Acre:</span>
            <span className="detail-value">{crop_details.yield_per_ton_per_acre} tons</span>
          </div>
          <div className="detail-item">
            <span className="detail-label">Cost per Acre:</span>
            <span className="detail-value">₹{crop_details.cost_per_acre.toLocaleString()}</span>
          </div>
        </div>
      </div>

      {/* About Section */}
      <div className="about-section">
        <h3>ℹ️ About This Analysis</h3>
        <div className="about-content">
          <p>
            This price prediction dashboard provides comprehensive financial analysis for <strong>{cropName}</strong> cultivation. 
            The system uses advanced machine learning models and real-time market data to generate accurate profit projections.
          </p>
          <p>
            <strong>Key Features:</strong>
          </p>
          <ul>
            <li>📊 Price trend analysis based on historical market data</li>
            <li>💰 ROI calculation with break-even analysis</li>
            <li>🎯 Crop performance radar chart for multi-dimensional analysis</li>
            <li>🤖 AI-powered investment insights using Groq's Llama 3 model</li>
            <li>📈 Monthly profit projections for better financial planning</li>
          </ul>
          <p>
            <strong>Data Sources:</strong> Market prices are based on agricultural commodity exchanges and regional market data. 
            Yield estimates consider soil conditions, climate factors, and farming practices.
          </p>
          <p className="disclaimer">
            <em>Disclaimer: These projections are estimates based on available data. Actual results may vary due to market conditions, weather patterns, and other factors. Please consult with agricultural experts before making investment decisions.</em>
          </p>
        </div>
      </div>

      {/* Profit Summary */}
      <div className="profit-summary">
        <div className="summary-header">
          <h3>💡 Investment Summary</h3>
        </div>
        <div className="summary-content">
          <p>
            Investing in <strong>{cropName}</strong> for <strong>{profit_data.acres} acres</strong> will require an initial investment of 
            <strong> ₹{profit_data.total_cost.toLocaleString()}</strong>. With a growth period of 
            <strong> {profit_data.growth_time_months} months</strong>, you can expect a total yield of 
            <strong> {profit_data.total_yield_tons} tons</strong>. At current market prices, this will generate 
            <strong> ₹{profit_data.total_revenue.toLocaleString()}</strong> in revenue, resulting in a net profit of 
            <strong> ₹{profit_data.profit.toLocaleString()}</strong> ({profit_data.profit_margin}% profit margin).
          </p>
        </div>
      </div>

      {/* AI Insights Section */}
      <div className="ai-insights-section">
        <div className="insights-header">
          <h3>🤖 AI-Powered Investment Insights</h3>
          <p className="insights-subtitle">Strategic recommendations based on market analysis</p>
        </div>
        <div className="insights-grid">
          {ai_insights && ai_insights.map((insight, index) => (
            <div key={index} className="insight-card">
              <div className="insight-icon">
                {index === 0 && '📊'}
                {index === 1 && '⏰'}
                {index === 2 && '💡'}
                {index === 3 && '🎯'}
              </div>
              <div className="insight-content">
                <p>{insight}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default PricePredictionDashboard;
