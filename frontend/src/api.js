import axios from 'axios';

const API_URL = 'http://localhost:8000/api';

export const getLatestTelemetry = async () => {
  const response = await axios.get(`${API_URL}/inverter/latest`);
  return response.data;
};

export const getHistory = async (limit = 100) => {
  const response = await axios.get(`${API_URL}/inverter/history?limit=${limit}`);
  return response.data;
};

export const getAlerts = async () => {
  const response = await axios.get(`${API_URL}/alerts`);
  return response.data;
};

export const getAISuggestions = async () => {
  const response = await axios.get(`${API_URL}/ai/suggestions`);
  return response.data;
};

export const simulateData = async () => {
  const response = await axios.post(`${API_URL}/simulator/generate`);
  return response.data;
};
