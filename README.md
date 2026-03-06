# AI Solar Monitoring & Failure Prediction System (Industrial Edition)

A 100% compliant implementation of the industrial-grade monitoring specification.

## 18-Point Architecture
1. **Dual Intelligence**: Internal & Combined ML models.
2. **Modular Backend**: Separated into predictable modules (`predictor`, `anomaly`, `genai`).
3. **Utility Layer**: Robust `data_cleaning` (Z-score) and `feature_engineering`.
4. **XGBoost/LightGBM**: High-accuracy gradient boosting algorithms.
5. **Multi-Horizon**: Failure risk predicted for 10m, 1h, 24h, and 7d.
6. **Isolation Forest**: Mathematical anomaly scoring.
7. **GenAI Reasoning**: Expert templates using Google Gemini.
8. **Real-Time Buffer**: Sliding window telemetry ingestion.
9. **Dual Model Switching**: Auto-detection vs Manual override.
10. **Glassmorphism UI**: Dashboard for live trends and alerts.

## Launch Guide

### 1. Training (Google Colab)
- Paste `notebooks/train_models_colab.py` into Colab.
- Upload CSV telemetry to `/content/data`.
- Run and download the `.joblib` models.

### 2. Deployment (Local/Server)
- Place models in the `models/` directory.
- Update `.env` with `GEMINI_API_KEY`.
- Run:
  ```bash
  docker-compose up --build
  ```

### 3. Monitoring
- Access `http://localhost`.
- Toggle between Model Modes to see how "Auto" switches intelligence based on environmental data availability.