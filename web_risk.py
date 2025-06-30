import os
from dotenv import load_dotenv
import google.generativeai as genai
import json
import re

# Load API key from .env file
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=API_KEY)

# Define the company for assessment
company_name = "quarkfin.ai"

# Define your prompt with explicit JSON formatting instructions
prompt = f"""


You are performing a detailed KYB (Know Your Business) risk assessment for the given company: {company_name} based on these 5 risk categories:

1. Reputation Risk
2. Financial Risk
3. Technology Risk
4. Business Risk
5. Legal & Compliance Risk

Under each risk category, provide exactly 5 practical checks, assign each check a score between 0 (high risk) to 10 (low risk), and clearly state reasons and current insights backing the scores, explicitly citing real-world data sources.

Calculate the average score for each risk category, and then compute a weighted total score using these specific weights:
- Reputation Risk: 25%
- Financial Risk: 25%
- Technology Risk: 20%
- Business Risk: 15%
- Legal & Compliance Risk: 15%

IMPORTANT: Return ONLY valid JSON without any additional text, markdown formatting, or explanations. The JSON should follow this exact structure:

{{
  "company_name": "{company_name}",
  "risk_categories": {{
    "reputation_risk": {{
      "checks": [
        {{"check_name": "...", "score": <score>, "reason": "...", "Insight": "<reason with source>", source: "<source link to vet the insight>"}}
        ...
      ],
      "average_score": 0.0,
      "weight": 0.25
    }},
    "financial_risk": {{
      "checks": [...],
      "average_score": 0.0,
      "weight": 0.25
    }},
    "technology_risk": {{
      "checks": [...],
      "average_score": 0.0,
      "weight": 0.20
    }},
    "business_risk": {{
      "checks": [...],
      "average_score": 0.0,
      "weight": 0.15
    }},
    "legal_compliance_risk": {{
      "checks": [...],
      "average_score": 0.0,
      "weight": 0.15
    }}
  }},
  "weighted_total_score": 0.0,
  "risk_level": "Low/Medium/High"

Ensure every insight clearly references credible real-world sources.
}}
"""

def extract_json_from_response(text):
    """Extract JSON from response text that might contain extra formatting"""
    # Remove markdown code blocks if present
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*$', '', text)
    
    # Try to find JSON object boundaries
    start_idx = text.find('{')
    if start_idx == -1:
        raise ValueError("No JSON object found in response")
    
    # Find the matching closing brace
    brace_count = 0
    end_idx = start_idx
    for i, char in enumerate(text[start_idx:], start_idx):
        if char == '{':
            brace_count += 1
        elif char == '}':
            brace_count -= 1
            if brace_count == 0:
                end_idx = i + 1
                break
    
    json_str = text[start_idx:end_idx]
    return json_str

try:
    # Generate response from Gemini model
    model = genai.GenerativeModel('gemini-2.0-flash')
    response = model.generate_content(prompt)
    
    print("Raw response received:")
    print("-" * 50)
    print(response.text)
    print("-" * 50)
    
    # Extract and parse JSON
    json_str = extract_json_from_response(response.text)
    risk_assessment = json.loads(json_str)
    
    # Output the risk assessment
    print("\nParsed Risk Assessment:")
    print("=" * 50)
    print(json.dumps(risk_assessment, indent=4))
    
    # Optional: Save to file
    with open(f'{company_name}_risk_assessment.json', 'w') as f:
        json.dump(risk_assessment, f, indent=4)
    print(f"\nRisk assessment saved to {company_name}_risk_assessment.json")

except json.JSONDecodeError as e:
    print(f"JSON parsing error: {e}")
    print("Raw response text:")
    print(response.text)
    print("\nTrying alternative parsing...")
    
    # Alternative: Try to manually clean the response
    try:
        cleaned_text = response.text.strip()
        # Remove common prefixes/suffixes that might interfere
        if cleaned_text.startswith('```json'):
            cleaned_text = cleaned_text[7:]
        if cleaned_text.endswith('```'):
            cleaned_text = cleaned_text[:-3]
        cleaned_text = cleaned_text.strip()
        
        risk_assessment = json.loads(cleaned_text)
        print("Successfully parsed with alternative method:")
        print(json.dumps(risk_assessment, indent=4))
        
    except Exception as e2:
        print(f"Alternative parsing also failed: {e2}")
        print("Consider modifying the prompt or handling the response differently")

except Exception as e:
    print(f"General error: {e}")
    print("Raw response (if available):")
    if 'response' in locals():
        print(response.text)