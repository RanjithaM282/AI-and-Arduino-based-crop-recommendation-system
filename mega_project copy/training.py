import pandas as pd
import numpy as np
import pickle   # ✅ ADD THIS

from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error

from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.svm import SVR

from xgboost import XGBRegressor

# =========================
# LOAD DATA
# =========================
df = pd.read_csv("my_data.csv")

# =========================
# FEATURES & TARGET
# =========================
X = df.drop("Production_MKgs", axis=1)
y = df["Production_MKgs"]

# =========================
# TIME SERIES SPLIT
# =========================
split = int(len(df) * 0.8)

X_train, X_test = X[:split], X[split:]
y_train, y_test = y[:split], y[split:]

# =========================
# MODELS
# =========================
models = {
    "Linear Regression": LinearRegression(),
    "Random Forest": RandomForestRegressor(n_estimators=200),
    "Gradient Boosting": GradientBoostingRegressor(),
    "SVR": SVR(),
    "XGBoost": XGBRegressor(
        n_estimators=500,
        learning_rate=0.03,
        max_depth=6,
        subsample=0.8,
        colsample_bytree=0.8
    )
}

# =========================
# TRAIN & EVALUATE
# =========================
results = {}
best_model = None
best_score = -np.inf

for name, model in models.items():
    model.fit(X_train, y_train)
    preds = model.predict(X_test)

    r2 = r2_score(y_test, preds)
    mae = mean_absolute_error(y_test, preds)

    results[name] = r2

    print(f"{name}")
    print(f"R2 Score: {r2:.4f}")
    print(f"MAE: {mae:.4f}")
    print("-" * 30)

    # ✅ Track best model
    if r2 > best_score:
        best_score = r2
        best_model = model
        best_model_name = name

# =========================
# BEST MODEL
# =========================
print(f"\nBest Model: {best_model_name}")
print(f"Best Accuracy (R2): {best_score:.4f}")

# =========================
# SAVE MODEL AS PICKLE
# =========================
with open("model.pkl", "wb") as f:
    pickle.dump(best_model, f)

print("\n✅ Model saved successfully as model.pkl")