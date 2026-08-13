import React, { useState, useEffect, useCallback } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell, BarChart, Bar, AreaChart, Area, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from 'recharts';
import './PricePredictionDashboard.css';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D'];

const formatCurrency = (value) => {
  const amount = Number(value);
  if (!Number.isFinite(amount)) {
    return '0';
  }
  return Math.abs(amount).toLocaleString('en-IN');
};

const isValidPriceResponse = (data) => {
  const profit = data?.profit_data;
  if (!profit) {
    return false;
  }

  const requiredFields = [
    'profit',
    'total_revenue',
    'total_cost',
    'growth_time_months',
    'total_yield_tons',
    'market_price_per_ton',
    'acres',
    'profit_margin',
  ];

  return requiredFields.every((field) => Number.isFinite(Number(profit[field])));
};

const PricePredictionDashboard = ({ cropName, acres = 1, mlFeatures = null, mlScore = null }) => {
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
        body: JSON.stringify({
          crop_name: cropName,
          acres,
          ...(mlFeatures || {}),
          ...(mlScore != null ? { ml_score: mlScore } : {}),
        }),
      });
      const data = await response.json();
      if (!response.ok) {
        setError(data.error || 'Failed to fetch price prediction');
        return;
      }
      if (data.status === 'success' && isValidPriceResponse(data)) {
        setPriceData(data);
      } else {
        setError(data.error || 'Invalid price prediction data received from server');
      }
    } catch (err) {
      setError('Failed to connect to price prediction server');
    } finally {
      setLoading(false);
    }
  }, [cropName, acres, mlFeatures, mlScore]);

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

  const { profit_data, price_trend = [], crop_details = {}, ai_insights = [], ml_prediction = null, model_used } = priceData;

  const insightPayload = ai_insights?.suggestions
    ? ai_insights
    : { suggestions: Array.isArray(ai_insights) ? ai_insights : [], source: null, status: 'error' };
  const insightItems = insightPayload.suggestions || [];
  const insightSource = insightPayload.source;
  const insightStatus = insightPayload.status;

  const growthTimeMonths = Math.max(Number(profit_data.growth_time_months) || 1, 1);
  const totalRevenue = Number(profit_data.total_revenue) || 0;
  const totalCost = Number(profit_data.total_cost) || 0;
  const profit = Number(profit_data.profit) || 0;
  const costPerAcre = Number(crop_details.cost_per_acre ?? totalCost / (Number(profit_data.acres) || 1)) || 0;

  // Prepare data for charts
  const profitBreakdown = [
    { name: 'Revenue', value: totalRevenue },
    { name: 'Cost', value: totalCost },
    { name: 'Profit', value: profit }
  ];

  // Monthly profit projection
  const monthlyProfit = [];
  const monthlyRevenue = totalRevenue / growthTimeMonths;
  const monthlyCost = totalCost / growthTimeMonths;
  const monthlyNet = monthlyRevenue - monthlyCost;
  
  for (let i = 1; i <= growthTimeMonths; i++) {
    monthlyProfit.push({
      month: `Month ${i}`,
      revenue: Math.round(monthlyRevenue),
      cost: Math.round(monthlyCost),
      profit: Math.round(monthlyNet)
    });
  }

  // Crop comparison radar data
  const radarData = [
    { subject: 'Profit', A: profit / 10000, fullMark: 10 },
    { subject: 'Yield', A: (Number(profit_data.total_yield_tons) || 0) / 10, fullMark: 5 },
    { subject: 'Growth Time', A: 12 / growthTimeMonths, fullMark: 2 },
    { subject: 'Market Price', A: (Number(profit_data.market_price_per_ton) || 0) / 1000, fullMark: 5 },
    { subject: 'Cost Efficiency', A: totalCost > 0 ? (profit / totalCost) * 10 : 0, fullMark: 5 }
  ];

  // ROI calculation
  const roi = totalCost > 0 ? ((profit / totalCost) * 100).toFixed(2) : '0.00';
  const breakEvenMonths = monthlyNet !== 0 ? Math.ceil(totalCost / monthlyNet) : growthTimeMonths;

  return (
    <div className={`price-dashboard-container ${darkMode ? 'dark-mode' : 'light-mode'}`}>
      <div className="dashboard-header">
        <div className="header-left">
          <h2>💰 Price Prediction & Profit Analysis</h2>
          <p className="crop-badge">{cropName.toUpperCase()}</p>
          {model_used === 'machine_learning' && ml_prediction?.available && (
            <p className="ml-badge">
              🤖 ML Model: {ml_prediction.confidence_percent}% suitability ({ml_prediction.suitability})
            </p>
          )}
        </div>
        <button 
          className="theme-toggle"
          onClick={() => setDarkMode(!darkMode)}
        >
          {darkMode ? '☀️ Light Mode' : '🌙 Dark Mode'}
        </button>
      </div>

      {model_used === 'machine_learning' && ml_prediction?.available && (
        <div className="ml-prediction-section">
          <h3>🤖 ML Model Prediction</h3>
          <div className="roi-grid">
            <div className="roi-card">
              <span className="roi-label">Model Confidence</span>
              <span className="roi-value">{ml_prediction.confidence_percent}%</span>
              <span className="roi-sub">{ml_prediction.suitability} suitability for your soil & climate</span>
            </div>
            <div className="roi-card">
              <span className="roi-label">Yield Adjustment</span>
              <span className="roi-value">{(profit_data.yield_multiplier * 100).toFixed(0)}%</span>
              <span className="roi-sub">Expected yield scaled by ML score</span>
            </div>
            <div className="roi-card">
              <span className="roi-label">Base Yield</span>
              <span className="roi-value">{profit_data.base_yield_tons || profit_data.total_yield_tons} tons</span>
              <span className="roi-sub">Before ML adjustment</span>
            </div>
            <div className="roi-card">
              <span className="roi-label">Predicted Yield</span>
              <span className="roi-value">{profit_data.total_yield_tons} tons</span>
              <span className="roi-sub">ML-adjusted for {profit_data.acres} acres</span>
            </div>
          </div>
        </div>
      )}

      {/* Key Metrics Cards */}
      <div className="metrics-grid">
        <div className="metric-card profit-card">
          <div className="metric-icon">📈</div>
          <div className="metric-content">
            <p className="metric-label">Total Profit</p>
            <p className="metric-value">₹{formatCurrency(profit)}</p>
            <p className="metric-sub">{Math.abs(Number(profit_data.profit_margin) || 0)}% margin</p>
          </div>
        </div>

        <div className="metric-card revenue-card">
          <div className="metric-icon">💵</div>
          <div className="metric-content">
            <p className="metric-label">Total Revenue</p>
            <p className="metric-value">₹{formatCurrency(totalRevenue)}</p>
            <p className="metric-sub">{profit_data.total_yield_tons} tons yield</p>
          </div>
        </div>

        <div className="metric-card cost-card">
          <div className="metric-icon">💸</div>
          <div className="metric-content">
            <p className="metric-label">Total Cost</p>
            <p className="metric-value">₹{formatCurrency(totalCost)}</p>
            <p className="metric-sub">{profit_data.acres} acres</p>
          </div>
        </div>

        <div className="metric-card time-card">
          <div className="metric-icon">⏱️</div>
          <div className="metric-content">
            <p className="metric-label">Growth Time</p>
            <p className="metric-value">{growthTimeMonths} months</p>
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
              <Tooltip formatter={(value) => `₹${formatCurrency(value)}`} />
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
              <Tooltip formatter={(value) => `₹${formatCurrency(value)}`} />
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
            <span className="roi-value">₹{formatCurrency(Math.round(monthlyNet))}</span>
            <span className="roi-sub">Average monthly earnings</span>
          </div>
          <div className="roi-card">
            <span className="roi-label">Annual Projection</span>
            <span className="roi-value">₹{formatCurrency(monthlyNet * 12)}</span>
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
            <span className="detail-value">{crop_details.description || 'No description available'}</span>
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
            <span className="detail-value">₹{formatCurrency(crop_details.cost_per_acre ?? costPerAcre)}</span>
          </div>
        </div>
      </div>

      {/* About Section */}
      <div className="about-section">
        <h3>ℹ️ About This Analysis</h3>
        <div className="about-content">
          <p>
            This price prediction dashboard uses the trained crop recommendation ML model
            (<strong>{ml_prediction?.model_type || 'RandomForestClassifier'}</strong>) to adjust
            yield and profit based on your soil nutrients, pH, temperature, and humidity.
            Profit projections combine ML suitability scores with market price data.
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
            <strong> ₹{formatCurrency(totalCost)}</strong>. With a growth period of 
            <strong> {growthTimeMonths} months</strong>, you can expect a total yield of 
            <strong> {profit_data.total_yield_tons} tons</strong>. At current market prices, this will generate 
            <strong> ₹{formatCurrency(totalRevenue)}</strong> in revenue, resulting in a net profit of 
            <strong> ₹{formatCurrency(profit)}</strong> ({profit_data.profit_margin}% profit margin).
          </p>
        </div>
      </div>

      {/* AI Insights Section */}
      <div className="ai-insights-section">
        <div className="insights-header">
          <h3>🤖 AI-Powered Investment Insights</h3>
          <p className="insights-subtitle">
            {insightSource
              ? `Generated by ${insightSource} AI using your field and profit data`
              : insightStatus === 'no_api_key'
                ? 'Add GROQ_API_KEY in backend/.env for live AI suggestions'
                : insightStatus === 'error'
                  ? (insightPayload.message || 'AI suggestions could not be loaded')
                  : 'Loading AI recommendations...'}
          </p>
        </div>
        <div className="insights-grid">
          {insightItems.length > 0 ? insightItems.map((insight, index) => (
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
          )) : (
            <div className="insight-card">
              <div className="insight-content">
                <p>{insightPayload.message || 'No AI suggestions available yet. Restart backend servers after adding your API key.'}</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default PricePredictionDashboard;
