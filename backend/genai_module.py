import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class GenAIAnalyzer:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-pro')

    async def analyze(self, data: dict):
        """
        Industrial GenAI Reasoning (Layer LLM 14).
        Uses specific expert prompt template.
        """
        prompt = f"""
You are a solar inverter expert AI.
Analyze the following inverter monitoring data.

Prediction results:
failure_probability = {data.get('failure_probability_7d')}
power_trend = {data.get('predicted_power_output')} kW
temperature = {data.get('inverter_temperature')} °C
risk_level = {data.get('risk_level_7d')}

Explain the situation.
Provide exactly:
1. Detected Issue
2. Three Possible Causes
3. Recommended Maintenance Actions
4. Risk Level

Format your response as a JSON object with these keys.
"""
        try:
            response = self.model.generate_content(prompt)
            # Basic parsing of Gemini response (assuming JSON for now, or raw text if needed)
            return response.text
        except Exception as e:
            return {
                "detected_issue": "Analysis Error",
                "recommended_actions": [f"Connection error: {e}"]
            }
