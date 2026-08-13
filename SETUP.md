# Quick Setup Guide

## Step 1: Install dependencies

```bash
cd backend
pip install -r requirements.txt

cd ../frontend
npm install
```

## Step 2: Configure API keys

```bash
cd backend
copy .env.example .env
```

Edit `.env` and add:

- `GROQ_API_KEY` — for AI suggestions ([console.groq.com](https://console.groq.com/))
- `OPENWEATHER_API_KEY` — for tea prediction weather ([openweathermap.org](https://openweathermap.org/api))

## Step 3: Start backend servers

Open 3 terminals in the `backend` folder:

```bash
python crop_recommendation.py
python tea_prediction.py
python price_prediction.py
```

## Step 4: Start frontend

```bash
cd frontend
npm start
```

Open http://localhost:3000

## Step 5: Connect Arduino

1. Upload `hardware/arduino_final_code.ino`
2. Connect Arduino via USB
3. Go to **Crop Recommendation** page — sensor data should appear automatically

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Port 5001 in use | Stop other Flask apps or change port in the `.py` file |
| Arduino not connected | Check COM port in Device Manager, try different USB port |
| AI suggestions empty | Add `GROQ_API_KEY` to `backend/.env` and restart servers |
| Tea model error | Place `model.pkl` in the `backend/` folder |
