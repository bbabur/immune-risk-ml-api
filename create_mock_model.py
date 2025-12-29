"""
Test için basit bir mock model oluşturur.
Gerçek modeliniz (modelV1.pkl) varsa bu dosyayı çalıştırmanıza gerek yok.
"""
import pickle
from sklearn.ensemble import RandomForestClassifier
import numpy as np

# Basit bir random forest model oluştur
model = RandomForestClassifier(n_estimators=10, random_state=42)

# Örnek veri ile eğit (21 özellik)
n_samples = 100
n_features = 21

X = np.random.randint(0, 2, size=(n_samples, n_features)).astype(float)
# 12. sütun (yaş) için gerçekçi değerler
X[:, 11] = np.random.uniform(0, 18, n_samples)
# 15. sütun (göbek kordon günü) için gerçekçi değerler  
X[:, 15] = np.random.randint(5, 21, n_samples)

# Basit bir kural ile etiket oluştur
y = ((X[:, 0] + X[:, 1] + X[:, 2] + X[:, 9] + X[:, 19]) >= 2).astype(int)

model.fit(X, y)

# Modeli kaydet
with open('modelV1.pkl', 'wb') as f:
    pickle.dump(model, f)

print("Mock model 'modelV1.pkl' olarak kaydedildi!")
print(f"Model özellikleri: {n_features} özellik, {n_samples} örnek ile eğitildi")

