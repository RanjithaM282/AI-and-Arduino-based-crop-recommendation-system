from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import pickle
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests

app = Flask(__name__)
CORS(app)

# ================= ML MODEL LOADING =================
print("🤖 Loading Crop Recommendation ML Model for price prediction...")

MODEL_FEATURES = ['nitrogen', 'phosphorus', 'potassium', 'ph', 'temperature', 'humidity']
crop_model_path = os.path.join(
    os.path.dirname(__file__), '..', 'crop_recommendation_model', 'crop_model.pkl'
)
crop_model = None

try:
    with open(crop_model_path, 'rb') as model_file:
        crop_model = pickle.load(model_file)
    print(f"✅ Crop ML Model loaded: {crop_model_path}")
    print(f"   Model type: {type(crop_model).__name__}")
    print(f"   Crops known to model: {list(crop_model.classes_)}")
except Exception as e:
    print(f"❌ Crop ML Model load error: {e}")
    crop_model = None


def suitability_label(score):
    if score >= 0.7:
        return 'Good'
    if score >= 0.4:
        return 'Moderate'
    return 'Poor'

from ai_service import generate_ai_suggestions

# ================= CROP DATA =================
# Growth time (in months), average yield per acre, cost per acre
crop_data = {
    "sugarcane": {
        "growth_time_months": 12,
        "yield_per_ton_per_acre": 40,
        "cost_per_acre": 25000,
        "market_price_per_ton": 3000,
        "description": "Sugarcane is a high-yield crop with long growth period"
    },
    "cotton": {
        "growth_time_months": 6,
        "yield_per_ton_per_acre": 2,
        "cost_per_acre": 15000,
        "market_price_per_ton": 6000,
        "description": "Cotton is a cash crop with moderate yield"
    },
    "pulses": {
        "growth_time_months": 4,
        "yield_per_ton_per_acre": 1.5,
        "cost_per_acre": 12000,
        "market_price_per_ton": 5000,
        "description": "Pulses are quick-growing with good market demand"
    },
    "wheat": {
        "growth_time_months": 5,
        "yield_per_ton_per_acre": 3,
        "cost_per_acre": 10000,
        "market_price_per_ton": 2000,
        "description": "Wheat is a staple crop with stable prices"
    },
    "rice": {
        "growth_time_months": 4,
        "yield_per_ton_per_acre": 4,
        "cost_per_acre": 15000,
        "market_price_per_ton": 2500,
        "description": "Rice is a high-demand staple crop"
    },
    "maize": {
        "growth_time_months": 3,
        "yield_per_ton_per_acre": 3.5,
        "cost_per_acre": 12000,
        "market_price_per_ton": 1800,
        "description": "Maize is a fast-growing versatile crop"
    },
    "corn": {
        "growth_time_months": 3,
        "yield_per_ton_per_acre": 3.5,
        "cost_per_acre": 12000,
        "market_price_per_ton": 1800,
        "description": "Corn (Maize) is a fast-growing versatile crop"
    },
    "tea": {
        "growth_time_months": 36,
        "yield_per_ton_per_acre": 1.2,
        "cost_per_acre": 35000,
        "market_price_per_ton": 25000,
        "description": "Tea is a high-value perennial crop suited to hilly, humid regions"
    },
    "apple": {
        "growth_time_months": 60,
        "yield_per_ton_per_acre": 8,
        "cost_per_acre": 40000,
        "market_price_per_ton": 45000,
        "description": "Apple is a high-value orchard crop with strong export demand"
    },
    "banana": {
        "growth_time_months": 9,
        "yield_per_ton_per_acre": 15,
        "cost_per_acre": 20000,
        "market_price_per_ton": 12000,
        "description": "Banana is a fast-growing fruit crop with steady local demand"
    },
    "blackgram": {
        "growth_time_months": 3,
        "yield_per_ton_per_acre": 0.8,
        "cost_per_acre": 10000,
        "market_price_per_ton": 7000,
        "description": "Blackgram is a short-duration pulse crop"
    },
    "chickpea": {
        "growth_time_months": 4,
        "yield_per_ton_per_acre": 1.2,
        "cost_per_acre": 11000,
        "market_price_per_ton": 5500,
        "description": "Chickpea is a popular protein-rich pulse crop"
    },
    "coconut": {
        "growth_time_months": 84,
        "yield_per_ton_per_acre": 6,
        "cost_per_acre": 30000,
        "market_price_per_ton": 8000,
        "description": "Coconut is a long-term plantation crop with multiple revenue streams"
    },
    "coffee": {
        "growth_time_months": 36,
        "yield_per_ton_per_acre": 0.6,
        "cost_per_acre": 45000,
        "market_price_per_ton": 180000,
        "description": "Coffee is a high-value plantation crop for suitable climates"
    },
    "grapes": {
        "growth_time_months": 6,
        "yield_per_ton_per_acre": 10,
        "cost_per_acre": 35000,
        "market_price_per_ton": 25000,
        "description": "Grapes are a profitable horticulture crop with export potential"
    },
    "jute": {
        "growth_time_months": 4,
        "yield_per_ton_per_acre": 2.5,
        "cost_per_acre": 9000,
        "market_price_per_ton": 4500,
        "description": "Jute is a fibre crop used in packaging and textiles"
    },
    "kidneybeans": {
        "growth_time_months": 3,
        "yield_per_ton_per_acre": 1.0,
        "cost_per_acre": 10000,
        "market_price_per_ton": 6000,
        "description": "Kidney beans are a short-duration pulse crop"
    },
    "lentil": {
        "growth_time_months": 4,
        "yield_per_ton_per_acre": 0.9,
        "cost_per_acre": 9500,
        "market_price_per_ton": 6500,
        "description": "Lentil is a nutritious pulse with stable market demand"
    },
    "mango": {
        "growth_time_months": 48,
        "yield_per_ton_per_acre": 8,
        "cost_per_acre": 35000,
        "market_price_per_ton": 20000,
        "description": "Mango is a high-value fruit crop with strong domestic demand"
    },
    "mothbeans": {
        "growth_time_months": 3,
        "yield_per_ton_per_acre": 0.7,
        "cost_per_acre": 9000,
        "market_price_per_ton": 6500,
        "description": "Moth beans are a drought-tolerant pulse crop"
    },
    "mungbean": {
        "growth_time_months": 3,
        "yield_per_ton_per_acre": 0.8,
        "cost_per_acre": 9500,
        "market_price_per_ton": 7000,
        "description": "Mung bean is a quick-growing pulse crop"
    },
    "muskmelon": {
        "growth_time_months": 3,
        "yield_per_ton_per_acre": 12,
        "cost_per_acre": 18000,
        "market_price_per_ton": 8000,
        "description": "Muskmelon is a seasonal fruit crop with good market prices"
    },
    "orange": {
        "growth_time_months": 48,
        "yield_per_ton_per_acre": 10,
        "cost_per_acre": 32000,
        "market_price_per_ton": 18000,
        "description": "Orange is a citrus fruit crop with year-round demand"
    },
    "papaya": {
        "growth_time_months": 9,
        "yield_per_ton_per_acre": 20,
        "cost_per_acre": 22000,
        "market_price_per_ton": 6000,
        "description": "Papaya is a fast-growing fruit crop"
    },
    "pigeonpeas": {
        "growth_time_months": 5,
        "yield_per_ton_per_acre": 1.1,
        "cost_per_acre": 10500,
        "market_price_per_ton": 5800,
        "description": "Pigeon peas are a hardy pulse crop"
    },
    "pomegranate": {
        "growth_time_months": 36,
        "yield_per_ton_per_acre": 7,
        "cost_per_acre": 38000,
        "market_price_per_ton": 35000,
        "description": "Pomegranate is a high-value horticulture crop"
    },
    "watermelon": {
        "growth_time_months": 3,
        "yield_per_ton_per_acre": 18,
        "cost_per_acre": 16000,
        "market_price_per_ton": 5000,
        "description": "Watermelon is a seasonal fruit crop with quick returns"
    }
}

# Crop aliases for common names
crop_aliases = {
    "corn": "maize",
    "maize": "maize",
    "sugarcane": "sugarcane",
    "cotton": "cotton",
    "pulses": "pulses",
    "wheat": "wheat",
    "rice": "rice",
    "tea": "tea",
    "pigeonpeas": "pigeonpeas",
    "pigeon peas": "pigeonpeas",
    "black gram": "blackgram",
    "mung bean": "mungbean",
    "kidney beans": "kidneybeans",
    "moth beans": "mothbeans",
    "muskmelon": "muskmelon",
    "water melon": "watermelon"
}

# ================= PRICE TREND DATA =================
# Simulated historical price trends (last 12 months)
def get_price_trend(crop_name):
    """Generate simulated price trend data for the last 12 months"""
    # Normalize crop name using aliases
    crop_key = crop_aliases.get(crop_name.lower(), crop_name.lower())
    base_price = crop_data.get(crop_key, {}).get("market_price_per_ton", 3000)
    trend = []
    for i in range(12):
        # Add some random variation to simulate market fluctuations
        variation = np.random.uniform(-10, 10)  # ±10% variation
        price = base_price * (1 + variation / 100)
        trend.append({
            "month": i + 1,
            "price": round(price, 2)
        })
    return trend

# ================= AI INSIGHTS =================
def _get_rule_based_insights(crop_name, profit_data, price_trend):
    """Fallback insights when AI API is unavailable."""
    print(f"🤖 Generating rule-based insights for {crop_name}...")
    
    crop_lower = crop_name.lower()
    profit_margin = profit_data['profit_margin']
    acres = profit_data['acres']
    growth_time = profit_data['growth_time_months']
    market_price = profit_data['market_price_per_ton']
    total_yield = profit_data['total_yield_tons']
    
    insights = []
    
    # Generate insights based on crop type and profit margin
    if profit_margin > 70:
        # High profit margin
        insights.append(f"Excellent profit margin of {profit_margin:.1f}% for {crop_name} indicates strong market demand. Consider expanding cultivation area by 20-30% to maximize returns.")
        insights.append(f"With {acres} acres of {crop_name}, your expected yield of {total_yield:.1f} tons at ₹{market_price}/ton generates significant revenue. Secure long-term contracts with buyers to lock in favorable prices.")
        
        if crop_lower == 'sugarcane':
            insights.append(f"Sugarcane's 12-month growth cycle requires substantial initial investment. Consider intercropping with legumes like groundnut or soybean during early growth stages to generate additional income and improve soil nitrogen levels.")
            insights.append(f"High sugarcane yields benefit from efficient irrigation. Invest in drip irrigation systems to reduce water costs by 40% and improve sugar recovery rates. Implement fertigation for precise nutrient delivery.")
            insights.append(f"Practice crop rotation after 2-3 ratoons. Rotate with legumes or cereals to break pest cycles and maintain soil health. This reduces disease pressure and improves long-term sustainability.")
        elif crop_lower == 'cotton':
            insights.append(f"Cotton prices fluctuate with global textile demand. Monitor international cotton futures and sell during peak demand seasons (October-December) for better prices. Consider forward contracts to lock in prices.")
            insights.append(f"Implement integrated pest management for cotton to reduce pesticide costs by 30% while maintaining yield quality. Use pheromone traps, biological controls, and Bt cotton varieties for sustainable pest control.")
            insights.append(f"Practice crop rotation with cereals like wheat or maize to break pest cycles and reduce soil-borne diseases. This improves soil structure and reduces fertilizer requirements for subsequent crops.")
        elif crop_lower == 'pulses':
            insights.append(f"Pulses have strong domestic demand due to protein-rich diet trends. Focus on quality certification to access premium markets and government procurement schemes. Ensure proper storage to maintain quality.")
            insights.append(f"Pulse crops fix nitrogen in soil. Rotate {crop_name} with cereals like wheat or rice to reduce fertilizer costs for subsequent crops by 25%. This natural nitrogen fixation improves soil fertility sustainably.")
            insights.append(f"Implement conservation agriculture practices like minimum tillage to preserve soil structure and moisture. Use mulching to reduce water evaporation and suppress weeds naturally.")
        elif crop_lower == 'rice':
            insights.append(f"Rice cultivation benefits from government MSP support. Enroll in procurement schemes to guarantee minimum price protection against market volatility. Stay updated on policy changes.")
            insights.append(f"Consider System of Rice Intensification (SRI) method to reduce seed requirements by 80% while maintaining or increasing yield per acre. This method also reduces water usage significantly.")
            insights.append(f"Practice rice-fallow or rice-pulse rotation systems to improve soil health. After rice harvest, grow short-duration pulses like green gram to utilize residual moisture and fix nitrogen.")
        else:
            insights.append(f"Monitor {crop_name} market trends during harvest season. Implement proper storage facilities to sell when prices peak rather than at harvest time. Consider cold storage for perishable crops.")
            insights.append(f"Diversify {crop_name} varieties to spread risk across different market segments and price points. Include both early and late-maturing varieties to extend harvest window.")
            insights.append(f"Implement soil testing every 2-3 years to monitor nutrient levels and pH. Adjust fertilization based on soil test results to optimize input costs and maintain soil health.")
            
    elif profit_margin > 50:
        # Medium profit margin
        insights.append(f"Good profit margin of {profit_margin:.1f}% for {crop_name} shows solid returns. Optimize input costs through bulk purchasing and efficient resource management to improve margins further.")
        insights.append(f"Your {acres} acres of {crop_name} producing {total_yield:.1f} tons has room for optimization. Implement precision farming techniques to reduce input costs by 15-20%.")
        
        if crop_lower == 'sugarcane':
            insights.append(f"Sugarcane requires significant water and fertilizer. Use soil testing to apply nutrients precisely, reducing fertilizer costs while maintaining yield. Split nitrogen applications for better uptake.")
            insights.append(f"Consider {crop_name} variety selection based on your region's climate. Early-maturing varieties can reduce water requirements and allow multiple ratoons. Choose varieties with high sugar recovery.")
            insights.append(f"Implement green manuring by incorporating legume crops like sunnhemp before planting. This adds organic matter and fixes nitrogen, reducing fertilizer requirements by 20-30%.")
        elif crop_lower == 'cotton':
            insights.append(f"Cotton production costs are high due to pesticides and labor. Adopt mechanized harvesting and integrated pest management to reduce operational expenses. Use drone technology for precise spraying.")
            insights.append(f"Monitor cotton quality parameters like staple length and micronaire. Premium quality cotton commands 15-20% higher prices in the market. Implement proper harvesting and ginning practices.")
            insights.append(f"Practice crop rotation with groundnut or soybean to break pest cycles and improve soil fertility. Legume rotation reduces nitrogen fertilizer needs for subsequent cotton crops.")
        elif crop_lower == 'pulses':
            insights.append(f"Pulse crops are sensitive to weather patterns. Invest in weather monitoring and adjust planting schedules to avoid yield losses from extreme conditions. Use weather forecasts for irrigation planning.")
            insights.append(f"Focus on pulse varieties with shorter maturity periods to reduce risk exposure and enable multiple cropping cycles per year. This maximizes land utilization and annual returns.")
            insights.append(f"Implement ridge and furrow planting for better drainage and root development. Use seed treatment with biofertilizers to improve germination and early plant vigor.")
        elif crop_lower == 'rice':
            insights.append(f"Rice cultivation water costs can be optimized. Use alternate wetting and drying (AWD) technique to reduce water usage by 30% without affecting yield. This also reduces methane emissions.")
            insights.append(f"Consider direct-seeded rice (DSR) to reduce labor costs by 40% compared to traditional transplanting methods. DSR also saves water and reduces greenhouse gas emissions.")
            insights.append(f"Implement rice-fish farming systems in suitable areas. Fish cultivation in rice fields provides additional income, controls pests naturally, and improves soil fertility through fish waste.")
        else:
            insights.append(f"Analyze {crop_name} production costs breakdown. Identify the highest cost components and implement efficiency measures to improve profitability. Track costs per acre regularly.")
            insights.append(f"Explore value-added processing for {crop_name} to capture more margin from the supply chain rather than selling raw produce. Consider local processing units or partnerships.")
            insights.append(f"Implement integrated nutrient management combining organic and inorganic fertilizers. Use compost, vermicompost, and green manures to reduce chemical fertilizer dependency.")
            
    else:
        # Low profit margin
        insights.append(f"Profit margin of {profit_margin:.1f}% for {crop_name} needs improvement. Focus on cost reduction through efficient input management and yield optimization strategies.")
        insights.append(f"With current margins, consider reducing {crop_name} acreage or switching to higher-margin crops. Alternatively, implement intensive farming techniques to boost yield per acre.")
        
        if crop_lower == 'sugarcane':
            insights.append(f"Sugarcane's long growth cycle ties up capital for 12 months. Consider shorter-duration crops or intercropping to improve cash flow and overall profitability. Intercrop with vegetables or pulses.")
            insights.append(f"Evaluate sugarcane variety for sugar recovery percentage. Switch to high-recovery varieties to increase revenue per ton without additional cultivation costs. Consult local research stations.")
            insights.append(f"Implement trash mulching after harvest to retain soil moisture, suppress weeds, and add organic matter. This reduces irrigation needs and fertilizer requirements for the next crop.")
        elif crop_lower == 'cotton':
            insights.append(f"Cotton margins are squeezed by high input costs. Explore contract farming arrangements with textile companies to secure better prices and reduce market risk. Consider group marketing.")
            insights.append(f"Consider organic cotton production which commands premium prices. Though yield may be lower initially, the 30-50% price premium can significantly improve margins. Requires 3-year transition period.")
            insights.append(f"Implement trap cropping with marigold or sunflower to attract pests away from cotton. This reduces pesticide use and costs while maintaining yield through natural pest control.")
        elif crop_lower == 'pulses':
            insights.append(f"Pulse crops often have lower yields but good prices. Focus on yield improvement through better seed varieties, proper spacing, and timely irrigation to boost production. Use certified seeds.")
            insights.append(f"Explore government schemes and subsidies for pulse cultivation. Many states offer incentives for pulse production to reduce import dependence. Check with local agricultural departments.")
            insights.append(f"Implement rhizobium seed treatment to enhance nitrogen fixation naturally. This biological inoculant reduces nitrogen fertilizer requirements by 50% while improving plant growth.")
        elif crop_lower == 'rice':
            insights.append(f"Rice margins can be improved by reducing cultivation costs. Use laser land leveling to reduce water and fertilizer requirements by 20-25%. This precision technique optimizes field topography.")
            insights.append(f"Consider aromatic or specialty rice varieties like Basmati which command 2-3 times higher prices than common rice varieties. These varieties have export potential and premium domestic markets.")
            insights.append(f"Implement aerobic rice cultivation in suitable areas to reduce water usage by 50% compared to flooded rice. This method is suitable for well-drained soils and reduces labor costs.")
        else:
            insights.append(f"Conduct detailed cost-benefit analysis for {crop_name}. Identify non-essential expenses and eliminate them to improve profit margins. Focus on high-impact cost reduction areas.")
            insights.append(f"Consider forming farmer cooperatives for {crop_name} to achieve economies of scale in purchasing inputs and negotiating better selling prices. Collective bargaining improves market power.")
            insights.append(f"Implement conservation agriculture principles: minimum soil disturbance, permanent soil cover, and crop rotation. These practices reduce input costs over time while maintaining productivity.")
    
    # Add soil health and sustainability insights
    soil_insights = [
        f"Conduct comprehensive soil testing before planting season to determine nutrient status and pH. Apply lime if soil is acidic or sulfur if alkaline to optimize pH for {crop_name}.",
        f"Implement organic matter addition through compost, farmyard manure, or green manures. This improves soil structure, water retention, and nutrient availability for {crop_name}.",
        f"Practice crop rotation to break pest and disease cycles. Rotate {crop_name} with crops from different families to maintain soil health and reduce chemical input requirements.",
        f"Use cover crops during fallow periods to prevent soil erosion and add organic matter. Legume cover crops also fix nitrogen, reducing fertilizer costs for subsequent {crop_name} crops.",
        f"Implement precision agriculture techniques like GPS-guided equipment and variable rate technology to optimize input application. This reduces waste and improves cost efficiency for {crop_name}."
    ]
    
    # Add seasonal and weather-related insights
    seasonal_insights = [
        f"Plan planting schedule based on monsoon patterns for {crop_name}. Early planting with onset of monsoon maximizes growing season and reduces irrigation requirements.",
        f"Implement rainwater harvesting structures like farm ponds or check dams to capture runoff. This provides supplemental irrigation during dry spells critical for {crop_name}.",
        f"Use weather forecasting tools to anticipate extreme weather events. Have contingency plans for drought, floods, or pest outbreaks that commonly affect {crop_name} cultivation.",
        f"Adjust planting dates based on long-term weather patterns for your region. Avoid planting during peak pest pressure periods or extreme temperature windows for {crop_name}.",
        f"Implement climate-smart agriculture practices like stress-tolerant varieties, improved water management, and agroforestry to build resilience against climate variability affecting {crop_name}."
    ]
    
    # Add market trend insight
    if price_trend and len(price_trend) > 0:
        recent_price = price_trend[-1]['price']
        avg_price = sum(p['price'] for p in price_trend) / len(price_trend)
        if recent_price > avg_price * 1.05:
            insights.append(f"Current {crop_name} price of ₹{recent_price}/ton is 5% above 12-month average. Consider selling now to capitalize on favorable market conditions.")
        elif recent_price < avg_price * 0.95:
            insights.append(f"Current {crop_name} price of ₹{recent_price}/ton is below 12-month average. Consider storing produce if facilities are available, or wait for price recovery.")
        else:
            insights.append(f"{crop_name} prices are stable around the 12-month average. Monitor market signals and be ready to act when price movements indicate favorable selling opportunities.")
    
    # Add one soil health insight
    insights.append(soil_insights[len(insights) % len(soil_insights)])
    
    # Add one seasonal insight
    insights.append(seasonal_insights[len(insights) % len(seasonal_insights)])
    
    print(f"✅ Rule-based insights generated: {len(insights)} recommendations")
    return insights[:4]


def get_ai_insights(crop_name, profit_data, price_trend, ml_prediction=None, input_data=None):
    """Generate real AI investment insights."""
    ml_text = "ML model not used for this crop"
    if ml_prediction and ml_prediction.get("available"):
        ml_text = (
            f"ML suitability score: {ml_prediction.get('confidence_percent')}% "
            f"({ml_prediction.get('suitability')}), "
            f"yield multiplier: {ml_prediction.get('yield_multiplier')}"
        )

    soil_text = "Soil/sensor data not provided"
    if input_data:
        soil_text = json.dumps(input_data, indent=2)

    system_prompt = (
        "You are an expert agricultural economist and farm investment advisor in India. "
        "Give practical, specific advice for farmers. Keep each insight under 35 words."
    )
    user_prompt = f"""
Crop: {crop_name}
Acres: {profit_data.get('acres')}
Growth time (months): {profit_data.get('growth_time_months')}
Predicted yield (tons): {profit_data.get('total_yield_tons')}
Base yield (tons): {profit_data.get('base_yield_tons', profit_data.get('total_yield_tons'))}
Total revenue (INR): {profit_data.get('total_revenue')}
Total cost (INR): {profit_data.get('total_cost')}
Profit (INR): {profit_data.get('profit')}
Profit margin (%): {profit_data.get('profit_margin')}
Market price (INR/ton): {profit_data.get('market_price_per_ton')}
{ml_text}

Field conditions:
{soil_text}

Write exactly 4 numbered investment and farming recommendations for this crop and field situation.
Focus on profit improvement, risk reduction, and timing.
"""

    return generate_ai_suggestions(system_prompt, user_prompt, max_items=4)

# ================= CROP LOOKUP =================
def resolve_crop_key(crop_name):
    """Normalize crop name using aliases."""
    return crop_aliases.get(crop_name.lower(), crop_name.lower())


def build_feature_vector(data):
    """Build the ML feature vector from request data."""
    missing = [feature for feature in MODEL_FEATURES if data.get(feature) is None]
    if missing:
        return None, missing

    return np.array(
        [float(data.get(feature)) for feature in MODEL_FEATURES]
    ).reshape(1, -1), []


def get_ml_prediction(crop_name, data):
    """Run the trained crop model and return suitability for the requested crop."""
    if crop_model is None:
        return {
            "available": False,
            "message": "ML model not loaded"
        }

    features, missing = build_feature_vector(data)
    if features is None:
        return {
            "available": False,
            "message": f"Missing ML features: {missing}",
            "required_features": MODEL_FEATURES
        }

    probabilities = crop_model.predict_proba(features)[0]
    classes = [str(crop).lower() for crop in crop_model.classes_]
    crop_key = resolve_crop_key(crop_name)

    if crop_key not in classes:
        return {
            "available": False,
            "message": f"Crop '{crop_name}' is not supported by the ML model",
            "model_classes": [crop.title() for crop in classes]
        }

    crop_index = classes.index(crop_key)
    confidence_score = float(probabilities[crop_index])
    top_index = int(np.argmax(probabilities))

    return {
        "available": True,
        "model_used": "machine_learning",
        "model_type": type(crop_model).__name__,
        "crop": crop_name.title(),
        "confidence_score": round(confidence_score, 4),
        "confidence_percent": round(confidence_score * 100, 1),
        "suitability": suitability_label(confidence_score),
        "yield_multiplier": round(0.5 + confidence_score * 0.5, 4),
        "top_model_prediction": classes[top_index].title(),
        "input_features": {
            feature: float(data.get(feature)) for feature in MODEL_FEATURES
        }
    }


def get_crop_details(crop_name):
    """Return crop metadata, using the same fallback logic as profit calculation."""
    crop_key = resolve_crop_key(crop_name)
    crop = crop_data.get(crop_key)
    if crop:
        return crop

    profit_data = calculate_profit(crop_name, 1)
    return {
        "growth_time_months": profit_data["growth_time_months"],
        "yield_per_ton_per_acre": round(profit_data["total_yield_tons"], 2),
        "cost_per_acre": profit_data["total_cost"],
        "market_price_per_ton": profit_data["market_price_per_ton"],
        "description": f"{crop_name} - using estimated values"
    }


# ================= PROFIT CALCULATION =================
def calculate_profit(crop_name, acres=1, ml_score=None):
    """Calculate profit for a given crop, optionally adjusted by ML suitability score."""
    # Normalize crop name using aliases
    crop_key = resolve_crop_key(crop_name)
    crop = crop_data.get(crop_key, {})
    
    # Fallback for unknown crops - use reasonable default values
    if not crop:
        print(f"⚠️ Crop '{crop_name}' not in database, using default values")
        crop = {
            "growth_time_months": 4,  # Average growth time
            "yield_per_ton_per_acre": 2.5,  # Average yield
            "cost_per_acre": 15000,  # Average cost
            "market_price_per_ton": 3000,  # Average price
            "description": f"{crop_name} - using estimated values"
        }
    
    growth_time = crop["growth_time_months"]
    yield_per_acre = crop["yield_per_ton_per_acre"]
    cost_per_acre = crop["cost_per_acre"]
    market_price = crop["market_price_per_ton"]
    
    # Calculate total yield and revenue
    base_yield = yield_per_acre * acres
    yield_multiplier = 1.0
    if ml_score is not None:
        yield_multiplier = 0.5 + (float(ml_score) * 0.5)

    total_yield = base_yield * yield_multiplier
    total_revenue = total_yield * market_price
    total_cost = cost_per_acre * acres
    
    # Calculate profit
    profit = total_revenue - total_cost
    profit_margin = (profit / total_revenue) * 100 if total_revenue > 0 else 0
    
    return {
        "crop": crop_name,
        "acres": acres,
        "growth_time_months": growth_time,
        "base_yield_tons": round(base_yield, 2),
        "total_yield_tons": round(total_yield, 2),
        "yield_multiplier": round(yield_multiplier, 4),
        "ml_adjusted": ml_score is not None,
        "total_revenue": round(total_revenue, 2),
        "total_cost": round(total_cost, 2),
        "profit": round(profit, 2),
        "profit_margin": round(profit_margin, 2),
        "market_price_per_ton": market_price
    }

# ================= API ENDPOINTS =================
@app.route('/price-predict', methods=['POST'])
def predict_price():
    """Predict price and profit for a recommended crop"""
    try:
        data = request.json
        crop_name = data.get('crop_name', '')
        acres = data.get('acres', 1)
        
        if not crop_name:
            return jsonify({"error": "crop_name is required"}), 400

        # Run ML model prediction using soil + sensor features
        ml_prediction = get_ml_prediction(crop_name, data)
        ml_score = None
        model_used = "static_estimates"

        if ml_prediction.get("available"):
            ml_score = ml_prediction["confidence_score"]
            model_used = "machine_learning"
            print(
                f"🤖 ML prediction for {crop_name}: "
                f"{ml_prediction['confidence_percent']}% ({ml_prediction['suitability']})"
            )
        elif data.get("ml_score") is not None:
            ml_score = float(data["ml_score"])
            model_used = "machine_learning"
            ml_prediction = {
                "available": True,
                "model_used": "machine_learning",
                "crop": crop_name.title(),
                "confidence_score": round(ml_score, 4),
                "confidence_percent": round(ml_score * 100, 1),
                "suitability": suitability_label(ml_score),
                "yield_multiplier": round(0.5 + ml_score * 0.5, 4),
                "source": "crop_recommendation_response"
            }
            print(f"🤖 Using ML score from crop recommendation: {ml_score:.2%}")
        else:
            print(f"⚠️ ML prediction unavailable: {ml_prediction.get('message')}")
        
        # Calculate profit (yield adjusted by ML suitability when available)
        profit_data = calculate_profit(crop_name, acres, ml_score=ml_score)
        
        if not profit_data:
            return jsonify({"error": f"Crop '{crop_name}' not found in database"}), 404
        
        # Get price trend
        price_trend = get_price_trend(crop_name)
        
        # Get AI insights
        ai_insights = get_ai_insights(
            crop_name,
            profit_data,
            price_trend,
            ml_prediction=ml_prediction if ml_prediction.get("available") else None,
            input_data=ml_prediction.get("input_features") if ml_prediction.get("available") else None,
        )
        
        # Get crop details (with alias + fallback support)
        crop_details = get_crop_details(crop_name)
        
        return jsonify({
            "status": "success",
            "model_used": model_used,
            "ml_prediction": ml_prediction,
            "profit_data": profit_data,
            "price_trend": price_trend,
            "crop_details": crop_details,
            "ai_insights": ai_insights
        })
    
    except Exception as e:
        print(f"❌ Price prediction error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/crop-list', methods=['GET'])
def get_crop_list():
    """Get list of available crops with their data"""
    return jsonify({
        "status": "success",
        "crops": crop_data
    })

@app.route('/compare-crops', methods=['POST'])
def compare_crops():
    """Compare multiple crops for profit analysis"""
    try:
        data = request.json
        crop_names = data.get('crop_names', [])
        acres = data.get('acres', 1)
        
        if not crop_names:
            return jsonify({"error": "crop_names is required"}), 400
        
        comparison = []
        for crop_name in crop_names:
            profit_data = calculate_profit(crop_name, acres)
            if profit_data:
                comparison.append(profit_data)
        
        # Sort by profit (descending)
        comparison.sort(key=lambda x: x['profit'], reverse=True)
        
        return jsonify({
            "status": "success",
            "comparison": comparison,
            "acres": acres
        })
    
    except Exception as e:
        print(f"❌ Crop comparison error: {e}")
        return jsonify({"error": str(e)}), 500

# ================= MAIN APPLICATION =================
if __name__ == '__main__':
    print("💰 Starting Price Prediction Server...")
    print("🌐 Server starting on http://127.0.0.1:5003")
    print("🌐 Price Prediction endpoint: POST /price-predict")
    print("🌐 Crop List endpoint: GET /crop-list")
    print("🌐 Crop Comparison endpoint: POST /compare-crops")
    try:
        app.run(debug=True, host='0.0.0.0', port=5003)
    except Exception as e:
        print(f"❌ Server startup error: {e}")
        print("🔧 Try running: python price_prediction.py")
        print("🔧 Or check if port 5003 is already in use")
