# İmmün Yetmezlik Risk Değerlendirme ML Servisi

Bu servis, makine öğrenmesi modeli kullanarak hastaların immün yetmezlik riskini değerlendirir.

## Kurulum

### Yerel Geliştirme

```bash
# Sanal ortam oluştur
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Bağımlılıkları yükle
pip install -r requirements.txt

# Servisi başlat
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Model Dosyası

`modelV1.pkl` dosyasını bu klasöre kopyalayın. Model dosyası olmadan servis başlar ama tahmin yapamaz.

## API Endpoints

### GET /health
Servisin çalışıp çalışmadığını kontrol eder.

**Yanıt:**
```json
{
  "status": "ok",
  "model_loaded": true
}
```

### POST /predict
Hasta verilerine göre risk tahmini yapar.

**İstek:**
```json
{
  "otit_sayisi_ge_4": 1,
  "sinuzit_sayisi_ge_2": 0,
  "iki_aydan_fazla_ab": 1,
  "pnomoni_ge_2": 0,
  "kilo_alamama": 0,
  "tekrarlayan_apse": 0,
  "pamukcuk_mantar": 0,
  "iv_antibiyotik": 0,
  "derin_enf_ge_2": 0,
  "aile_oykusu_boy": 1,
  "cinsiyet": 1,
  "yas": 5.5,
  "hastane_yatis": 1,
  "bcg_lenfadenopati": 0,
  "kronik_cilt": 0,
  "gobek_kordon_gunu": 7,
  "konjenital_kalp": 0,
  "kronik_ishal": 0,
  "yogun_bakim": 0,
  "akrabalik": 1,
  "aile_erken_olum": 0
}
```

**Yanıt:**
```json
{
  "prediction": 1,
  "probability": 0.75,
  "risk_level": "Yüksek Risk",
  "message": "Pediatrik immünoloji konsültasyonu önerilir."
}
```

## Render'da Deploy

1. Yeni bir Web Service oluşturun
2. Bu klasörü içeren repo'yu bağlayın
3. Aşağıdaki ayarları yapın:
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

## Alan Açıklamaları

| Alan | Açıklama | Tip |
|------|----------|-----|
| otit_sayisi_ge_4 | 1 Yıl İçinde Otit Sayısı ≥4 | 0/1 |
| sinuzit_sayisi_ge_2 | 1 Yıl İçinde Sinüzit Sayısı ≥2 | 0/1 |
| iki_aydan_fazla_ab | 2 Aydan Fazla Oral Antibiyotik Kullanımı | 0/1 |
| pnomoni_ge_2 | 1 yıl içinde ≥2 pnomoni | 0/1 |
| kilo_alamama | Bebeğin Kilo Alamaması | 0/1 |
| tekrarlayan_apse | Tekrarlayan Derin Apseler | 0/1 |
| pamukcuk_mantar | Kalıcı Pamukçuk/Mantar | 0/1 |
| iv_antibiyotik | IV Antibiyotik Gereksinimi | 0/1 |
| derin_enf_ge_2 | ≥2 Derin Enfeksiyon | 0/1 |
| aile_oykusu_boy | Ailede İmmün Yetmezlik | 0/1 |
| cinsiyet | Cinsiyet (0=Kadın, 1=Erkek) | 0/1 |
| yas | Yaş (yıl) | float |
| hastane_yatis | Hastaneye Yatış | 0/1 |
| bcg_lenfadenopati | BCG Sonrası Lenfadenopati | 0/1 |
| kronik_cilt | Kronik Cilt Problemleri | 0/1 |
| gobek_kordon_gunu | Göbek Kordonunun Düşme Günü | int |
| konjenital_kalp | Konjenital Kalp Hastalığı | 0/1 |
| kronik_ishal | Kronik İshal | 0/1 |
| yogun_bakim | Yoğun Bakım Yatışı | 0/1 |
| akrabalik | Anne-Baba Akrabalığı | 0/1 |
| aile_erken_olum | Ailede Erken Ölüm | 0/1 |

