import os
import google.generativeai as genai
import json

def get_ai_reasoning(telemetry_row: dict, prediction_results: dict):
    """
    Generate Root Cause Analysis (RCA) and maintenance recommendations using Gemini.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        return {
            "warning": "System Alert",
            "possible_reasons": ["AI Service Disconnected"],
            "recommended_actions": ["Configure GEMINI_API_KEY in .env"]
        }
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Context for the AI
    context = {
        "current_state": telemetry_row,
        "prediction_results": prediction_results
    }
    
    prompt = f"""
    You are an Industrial Solar Inverter Diagnostic AI. 
    Analyze the current system state and ML prediction results to provide a Root Cause Analysis (RCA).
    
    Current Data: {json.dumps(telemetry_row)}
    ML Predictions: {json.dumps(prediction_results)}
    
    Generate a diagnostic report in STRICT JSON format with these exact keys:
    - "warning": A clear header (e.g., "Potential Thermal Stress", "Grid Instability Detected").
    - "possible_reasons": A list of technical reasons (e.g., ["Dust accumulation", "High ambient temp"]).
    - "recommended_actions": A list of specific maintenance steps.
    
    Logic Guidelines:
    1. If anomaly_score is high or risk_level is Medium/High, be more critical.
    2. Look for patterns:
       - High temp + Efficiency drop -> Thermal issues or cooling failure.
       - High humidity + Grid fluctuation -> Insulation or grid stability.
       - Power output = 0 during daylight -> Inverter fault or disconnection.
    
    Only return raw JSON. No markdown.
    """
    
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        # Clean up possible markdown wrapping
        if text.startswith("```json"): text = text[7:-3].strip()
        elif text.startswith("```"): text = text[3:-3].strip()
        
        return json.loads(text)
    except Exception as e:
        return {
            "warning": "Diagnostic Error",
            "possible_reasons": ["AI processing failed"],
            "recommended_actions": ["Check system logs", str(e)]
        }
