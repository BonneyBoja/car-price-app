import pandas as pd
import random
import datetime

# 1. Define the parameters for our realistic dataset
num_rows = 2500

brands = ['Toyota', 'Honda', 'Ford', 'Chevrolet', 'BMW', 'Mercedes-Benz', 'Audi', 'Nissan', 'Volkswagen', 'Hyundai']
fuel_types = ['Gasoline', 'Diesel', 'Hybrid', 'Electric']
transmissions = ['Automatic', 'Manual', 'CVT', 'Dual Clutch']

# 2. Exact column names 
data = {
    'brand': [],
    'model_year': [],
    'milage': [],          
    'fuel_type': [],
    'horsepower': [],
    'car_age': [],
    'accident_reported': [],
    'has_clean_title': [],
    'transmission': [] 
}

# 3. Generate realistic data
print(f"Generating {num_rows} realistic car records...")
for _ in range(num_rows):
    brand = random.choice(brands)
    year = random.randint(2005, 2024)
    
    # Calculate age 
    age = 2024 - year
    
    # Calculate milage 
    milage = age * random.randint(8000, 15000) + random.randint(100, 5000)
    
    fuel = random.choice(fuel_types)
    hp = random.randint(110, 450)
    trans = random.choice(transmissions) 
    
    # 👇 THE FIX: Using 1s and 0s instead of 'Yes' and 'No' 👇
    accident = random.choice([1, 0])
    clean_title = random.choice([1, 0])
    
    # Append to the lists
    data['brand'].append(brand)
    data['model_year'].append(year)
    data['milage'].append(milage)
    data['fuel_type'].append(fuel)
    data['horsepower'].append(hp)
    data['car_age'].append(age)
    data['accident_reported'].append(accident)
    data['has_clean_title'].append(clean_title)
    data['transmission'].append(trans) 

# 4. Create a DataFrame and save it as a UNIQUE CSV
df = pd.DataFrame(data)

timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"dealership_bulk_test_data_{timestamp}.csv"

df.to_csv(filename, index=False)

print(f"✅ Success! Saved {num_rows} rows to a brand new file: {filename}")
#run  python generate_test_data.py in the terminal to generate the test data CSV file.