import ee
import pandas as pd
import numpy as np
import joblib
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.utils import class_weight
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Input, BatchNormalization
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau

print("🌍 INITIATING LOCAL EARTH ENGINE CONNECTION...")

try:
    ee.Initialize(project='mythical-runner-479015-f2')
    print("✅ Earth Engine Connected natively.")
except Exception as e:
    print("⚠️ Native auth failed. Please authenticate:")
    ee.Authenticate()
    ee.Initialize(project='mythical-runner-479015-f2')

print("🛰️ Commencing Global Pixel Extraction (Bypassing 5000-Pixel Limit)...")

BANDS = ['B01', 'B02', 'B3N', 'B04', 'B05', 'B06', 'B07', 'B08']
FEATURE_COLS = ['B01','B02','B3N','B04','B05','B06','B07','B08', 'NDVI', 'Brightness']

aster = ee.ImageCollection("ASTER/AST_L1T_003").filterDate('2000-01-01', '2007-12-31').median().select(BANDS)

# ==============================================================================
# 1. DISTRIBUTED SENSOR ARRAY (10 Zones x 4900 Pixels)
# ==============================================================================
target_zones = [
    # CLASS 0 (DEBRIS/URBAN/INDUSTRIAL)
    {'class_id': 0, 'lon': -118.25, 'lat': 33.73, 'radius': 5000, 'name': 'Port of LA'},
    {'class_id': 0, 'lon': -135.00, 'lat': 35.00, 'radius': 5000, 'name': 'Pacific Garbage Patch'},
    {'class_id': 0, 'lon': 120.98,  'lat': 14.50, 'radius': 5000, 'name': 'Manila Bay Coast'},

    # CLASS 1 (WATER)
    {'class_id': 1, 'lon': -155.00, 'lat': 20.00, 'radius': 5000, 'name': 'Deep Pacific'},
    {'class_id': 1, 'lon': 18.00,   'lat': 34.00, 'radius': 5000, 'name': 'Mediterranean Sea'},
    {'class_id': 1, 'lon': -40.00,  'lat': 30.00, 'radius': 5000, 'name': 'Mid-Atlantic Ocean'},
    {'class_id': 1, 'lon': 65.00,   'lat': -10.00, 'radius': 5000, 'name': 'Indian Ocean Clear'},

    # CLASS 2 (ALGAE/ORGANIC)
    {'class_id': 2, 'lon': -80.50,  'lat': 24.90, 'radius': 5000, 'name': 'Florida Keys'},
    {'class_id': 2, 'lon': -60.00,  'lat': 28.00, 'radius': 5000, 'name': 'Sargasso Sea'},
    {'class_id': 2, 'lon': 145.00,  'lat': -15.00, 'radius': 5000, 'name': 'Great Barrier Reef'}
]

all_rows = []
# Set safely below Google's 5000 limit
PIXELS_PER_ZONE = 4900 

for zone in target_zones:
    print(f"   -> Extracting {PIXELS_PER_ZONE} pixels from {zone['name']}...")
    roi = ee.Geometry.Point([zone['lon'], zone['lat']]).buffer(zone['radius'])
    
    # By asking for exactly 4900, we never trigger the Google API crash
    raw_data = aster.sample(region=roi, scale=30, numPixels=PIXELS_PER_ZONE, geometries=False).getInfo()
    
    for f in raw_data['features']:
        props = f['properties']
        if all(b in props for b in BANDS):
            row = [props[b] for b in BANDS] + [zone['class_id']]
            all_rows.append(row)

df = pd.DataFrame(all_rows, columns=BANDS + ['class_id'])
print(f"✅ MASSIVE DOWNLOAD COMPLETE: {len(df)} real global satellite pixels acquired.")

# ==============================================================================
# 2. FEATURE ENGINEERING & MATH
# ==============================================================================
print("⚙️ Applying atmospheric normalizations...")
for b in BANDS:
    b_min, b_max = df[b].min(), df[b].max()
    df[b] = (df[b] - b_min) / (b_max - b_min + 1e-8) if b_max > b_min else 0.0

df['NDVI'] = (df['B3N'] - df['B02']) / (df['B3N'] + df['B02'] + 1e-8)
df['Brightness'] = df[['B01','B02','B3N','B04']].mean(axis=1)

X = df[FEATURE_COLS].values
y = df['class_id'].values

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
joblib.dump(scaler, 'omni_scaler_global.pkl')
print("✅ Scaler saved locally to: omni_scaler_global.pkl")

# ==============================================================================
# 3. THE DEEP NEURAL NETWORK
# ==============================================================================
print("🧠 Constructing High-Capacity Deep Neural Architecture...")
model = Sequential([
    Input(shape=(10,)),
    Dense(512, activation='relu'),
    BatchNormalization(),
    Dropout(0.3),
    Dense(256, activation='relu'),
    BatchNormalization(),
    Dropout(0.3),
    Dense(128, activation='relu'),
    Dropout(0.2),
    Dense(64, activation='relu'),
    Dense(3, activation='softmax')
])

model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.001), 
              loss='sparse_categorical_crossentropy', 
              metrics=['accuracy'])

weights = class_weight.compute_class_weight('balanced', classes=np.unique(y_train), y=y_train)
class_weights = dict(enumerate(weights))

# ==============================================================================
# 4. ADVANCED TRAINING DYNAMICS
# ==============================================================================
checkpoint_saver = ModelCheckpoint('omni_brain_global.keras', monitor='val_accuracy', save_best_only=True, verbose=1)
lr_reducer = ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=5, min_lr=0.00001, verbose=1)
early_stop = EarlyStopping(monitor='val_loss', patience=15, restore_best_weights=True)

print("🔥 COMMENCING DEEP LEARNING ON GLOBAL DATASET...")
model.fit(
    X_train_scaled, y_train, 
    validation_data=(X_test_scaled, y_test), 
    epochs=150, 
    batch_size=256, 
    class_weight=class_weights,
    callbacks=[checkpoint_saver, lr_reducer, early_stop]
)

print("🏆 GLOBAL OMNI-MODEL TRAINING COMPLETE!")
print("Files 'omni_brain_global.keras' and 'omni_scaler_global.pkl' are saved in your folder.")