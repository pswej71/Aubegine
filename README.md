# AI-Powered Solar Inverter Monitoring & Failure Prediction System

An industrial-grade monitoring platform that predicts inverter health, power output, and efficiency using dual-mode Machine Learning (Internal & Combined) and Generative AI for diagnostics.

## Features
- **Dual ML Models**: Switches between Internal-only and Combined (Internal + External) models based on data availability.
- **Regression Analysis**: predicts future power output and efficiency trends.
- **Anomaly Detection**: Real-time identification of abnormal behavior using Isolation Forest.
- **7-Day Risk Prediction**: Probability of failure within the next week.
- **GenAI Root Cause Analysis**: Automated diagnostics and maintenance recommendations using Google Gemini.
- **Interactive Dashboard**: Modern glassmorphism UI with real-time charts and model selection toggles.

## Tech Stack
- **Backend**: FastAPI, SQLAlchemy, PostgreSQL, Scikit-Learn
- **Frontend**: React (Vite), Recharts, Lucide Icons
- **AI**: Google Gemini API
- **Deployment**: Docker, Docker Compose

## Getting Started

### Prerequisites
- Docker & Docker Compose
- Google Gemini API Key

### Setup
1. Clone the repository.
2. Copy `.env.example` to `.env` and add your `GEMINI_API_KEY`.
3. Run the following command:
   ```bash
   docker-compose up --build
   ```
4. Access the dashboard at `http://localhost`.

## API Documentation
- `POST /api/inverter/telemetry`: Send real-time data for analysis.
- `GET /api/predict`: Get latest predictions for a MAC address.
- `GET /api/alerts`: List active system anomalies and warnings.
- `POST /api/ml/train`: Trigger model retraining using local CSV data.

## Project Structure
- `backend/`: FastAPI server and ML services.
- `frontend/`: React dashboard.
- `notebooks/`: Colab-ready training scripts.
- `csv_files/`: Training data and history.