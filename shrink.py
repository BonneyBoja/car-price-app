import joblib

# 1. Load your original model
model = joblib.load('model.pkl')

# 2. Save it using joblib with compression
joblib.dump(model, 'car_price_model.joblib', compress=3)

print("Model successfully compressed with joblib!")
