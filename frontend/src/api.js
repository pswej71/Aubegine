import axios from 'axios';

const API_URL = 'http://localhost:8000/api';

export const getLatestTelemetry = async (mac = 'DEMO-001') => {
  const response = await axios.get(`${API_URL}/predict?mac=${mac}`);
  return response.data;
};

export const getAlerts = async (mac = 'DEMO-001') => {
  const response = await axios.get(`${API_URL}/alerts?mac=${mac}`);
  return response.data;
};

export const getGenAIAnalysis = async (mac = 'DEMO-001') => {
  const response = await axios.get(`${API_URL}/genai-analysis?mac=${mac}`);
  return response.data;
};

export const getExternalWeather = async () => {
  const response = await axios.get(`${API_URL}/external-weather`);
  return response.data;
};

export const postTelemetry = async (payload) => {
  const response = await axios.post(`${API_URL}/inverter/telemetry`, payload);
  return response.data;
};
