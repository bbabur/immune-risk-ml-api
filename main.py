from __future__ import annotations

import pickle
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


# Orijinal model kolon adlari alias olarak saklaniyor, Python-friendly alanlar kullaniliyor.
class Features(BaseModel):
    otit_sayisi_ge_4: int = Field(alias="1 Yıl İçinde Otit Sayısı ≥4", default=0)
    sinuzit_sayisi_ge_2: int = Field(alias="1 Yıl İçinde Sinüzit Sayısı  ≥2", default=0)
    iki_aydan_fazla_ab: int = Field(alias="2 Aydan Fazla Oral Antibiyotik Kullanımı", default=0)
    pnomoni_ge_2: int = Field(alias="1 yıl içinde ≥2 pnomoni", default=0)
    kilo_alamama: int = Field(alias="Bir Bebeğin Kilo Alamaması veya Normal Büyümemesi", default=0)
    tekrarlayan_apse: int = Field(alias="Tekrarlayan, Derin Cilt veya Organ Apseleri", default=0)
    pamukcuk_mantar: int = Field(alias="Ağızda veya Deride Kalıcı Pamukçuk yada Mantar Enfeksiyonu", default=0)
    iv_antibiyotik: int = Field(alias="İntravenoz Antibiyotik Gerektiren Enfeksiyonlar", default=0)
    derin_enf_ge_2: int = Field(alias="Septisemi Dâhil ≥2 Derin Enfeksiyon", default=0)
    aile_oykusu_boy: int = Field(alias="Ailede Doğuştan İmmün Yetmezlik oyküsü", default=0)
    cinsiyet: int = Field(alias="CİNSİYET  ", default=0)
    yas: float = Field(alias="YAŞ ", default=0.0)
    hastane_yatis: int = Field(alias="Hastaneye Yatış Varlığı", default=0)
    bcg_lenfadenopati: int = Field(alias="BCG Aşısı Sonrası Lenfadenopati", default=0)
    kronik_cilt: int = Field(alias="Kronik Cilt (deri) Problemleri", default=0)
    gobek_kordon_gunu: int = Field(alias="Gobek Kordonunun Düşme Günü", default=0)
    konjenital_kalp: int = Field(alias="Konjenital Kalp Hastalığı", default=0)
    kronik_ishal: int = Field(alias="Kronik İshal", default=0)
    yogun_bakim: int = Field(alias="Yoğun Bakımda Yatış", default=0)
    akrabalik: int = Field(alias="Anne-Baba Arasında Akrabalık Varlığı", default=0)
    aile_erken_olum: int = Field(alias="Ailede Erken olüm oyküsü", default=0)

    class Config:
        populate_by_name = True


class PredictionResponse(BaseModel):
    prediction: int
    probability: Optional[float] = None
    risk_level: str
    message: str


app = FastAPI(
    title="İmmün Yetmezlik Risk Değerlendirme API",
    version="1.0.0",
    description="Makine öğrenmesi tabanlı immün yetmezlik risk değerlendirme servisi"
)

# CORS ayarları - Next.js uygulamasından erişim için
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://immune-risk-next.onrender.com",
        "https://*.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def load_model() -> object:
    """Model dosyasını yükle"""
    model_path = Path(__file__).resolve().parent / "modelV1.pkl"
    if not model_path.exists():
        raise FileNotFoundError(f"Model dosyasi bulunamadi: {model_path}")

    with model_path.open("rb") as f:
        return pickle.load(f)


def get_risk_level(prediction: int, probability: Optional[float]) -> tuple[str, str]:
    """Tahmin sonucuna göre risk seviyesi ve mesaj döndür"""
    if prediction == 1:
        if probability and probability >= 0.8:
            return "Çok Yüksek Risk", "Acil pediatrik immünoloji konsültasyonu gereklidir!"
        elif probability and probability >= 0.6:
            return "Yüksek Risk", "Pediatrik immünoloji konsültasyonu önerilir."
        else:
            return "Orta Risk", "Takip ve ek testler önerilir."
    else:
        if probability and probability <= 0.2:
            return "Düşük Risk", "Rutin takip önerilir."
        else:
            return "Düşük-Orta Risk", "Rutin takip ve gerekirse kontrol önerilir."


# Modeli uygulama başlarken 1 kez yükle
MODEL = None
MODEL_LOADED = False

try:
    MODEL = load_model()
    MODEL_LOADED = True
    print("Model başarıyla yüklendi!")
except Exception as exc:
    print(f"Model yüklenemedi: {exc}")
    MODEL_LOADED = False


@app.get("/")
def root() -> dict:
    """Ana sayfa"""
    return {
        "service": "İmmün Yetmezlik Risk Değerlendirme API",
        "version": "1.0.0",
        "status": "running",
        "model_loaded": MODEL_LOADED
    }


@app.get("/health")
def health() -> dict:
    """Sağlık kontrolü endpoint'i"""
    return {
        "status": "ok",
        "model_loaded": MODEL_LOADED
    }


@app.post("/predict", response_model=PredictionResponse)
def predict(features: Features) -> dict:
    """
    Hasta özelliklerine göre immün yetmezlik riski tahmini yapar.
    
    - **prediction**: 1 = İmmün yetmezlik riski var, 0 = Risk yok
    - **probability**: Tahmin olasılığı (0-1 arası)
    - **risk_level**: Risk seviyesi açıklaması
    - **message**: Değerlendirme mesajı
    """
    if not MODEL_LOADED or MODEL is None:
        raise HTTPException(
            status_code=503,
            detail="Model henüz yüklenmedi. Lütfen model dosyasını kontrol edin."
        )

    # Modelin beklediği kolon sırası ile aynı sırada özellik vektörü oluşturuluyor
    vector: List[float] = [
        features.otit_sayisi_ge_4,
        features.sinuzit_sayisi_ge_2,
        features.iki_aydan_fazla_ab,
        features.pnomoni_ge_2,
        features.kilo_alamama,
        features.tekrarlayan_apse,
        features.pamukcuk_mantar,
        features.iv_antibiyotik,
        features.derin_enf_ge_2,
        features.aile_oykusu_boy,
        features.cinsiyet,
        features.yas,
        features.hastane_yatis,
        features.bcg_lenfadenopati,
        features.kronik_cilt,
        features.gobek_kordon_gunu,
        features.konjenital_kalp,
        features.kronik_ishal,
        features.yogun_bakim,
        features.akrabalik,
        features.aile_erken_olum,
    ]

    try:
        prediction = MODEL.predict([vector])[0]
        prob = None
        if hasattr(MODEL, "predict_proba"):
            prob = MODEL.predict_proba([vector])[0].max().item()
        
        risk_level, message = get_risk_level(int(prediction), prob)
        
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Tahmin sırasında hata: {exc}"
        ) from exc

    return {
        "prediction": int(prediction),
        "probability": prob,
        "risk_level": risk_level,
        "message": message
    }


# Geliştirme için: uvicorn main:app --reload --host 0.0.0.0 --port 8000

