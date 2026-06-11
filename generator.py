import os
import json
from google import genai

# Configuration to allow easily swapping model providers later
CONFIG = {
    "provider": "google-genai",
    "model": "gemini-3.5-flash"
}

def generate_solution(problem_text: str) -> dict:
    """
    Generates a structured solution for a DSA problem using the configured AI model.
    """
    if CONFIG["provider"] != "google-genai":
        return {"error": f"Provider '{CONFIG['provider']}' is not supported yet."}
        
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {"error": "GEMINI_API_KEY environment variable is not set."}

    client = genai.Client(api_key=api_key)
    
    prompt = f"""
You are an expert algorithms instructor.
For the following problem, provide exactly a JSON output. 
Do NOT include markdown code fences (like ```json), do NOT include any extra text. ONLY raw JSON.

CRITICAL FORMATTING INSTRUCTIONS:
Do NOT use LaTeX or math markup in any text fields. 
- Do NOT use dollar signs ($) for math.
- Do NOT use LaTeX commands like \\ge, \\le, \\log, \\sum, etc.
- Do NOT use caret notation like n^2.
Instead, write everything in plain readable text: use ≥, ≤, >, < directly. Write exponents in words or with actual unicode characters (e.g. "O(n²)" or "O(n squared)"). Write complexities in plain form like "O(n log n)". This applies to the explanation, idea, time_complexity, and space_complexity fields.

Structure exactly like this:
{{
  "title": "Problem Title",
  "explanation": "Clear explanation of the problem.",
  "approaches": [
    {{
      "name": "Approach Name",
      "idea": "Idea behind this approach",
      "code": {{
        "python": "Python code here",
        "java": "Java code here",
        "cpp": "C++ code here",
        "c": "C code here"
      }},
      "time_complexity": "O(...)",
      "space_complexity": "O(...)"
    }}
  ],
  "follow_ups": ["Follow up 1", "Follow up 2"]
}}

Ensure the approaches array covers a brute force approach, a better approach, and the optimal approach.

Problem:
{problem_text}
"""
    import time
    
    response = None
    max_retries = 5
    
    try:
        for attempt in range(max_retries + 1):
            try:
                response = client.models.generate_content(
                    model=CONFIG["model"],
                    contents=prompt
                )
                break
            except Exception as e:
                if attempt < max_retries:
                    wait_time = 2 ** (attempt + 1)  # 2, 4, 8, 16, 32 seconds
                    print(f"[Attempt {attempt + 1}/{max_retries}] Gemini API error: {type(e).__name__} - {str(e)}")
                    print(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    print(f"[Attempt {attempt + 1}/{max_retries + 1}] Max retries reached. Failing.")
                    raise e
                    
        text = response.text.strip()
        
        # Defensive cleanup in case the model still includes markdown formatting
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
            
        if text.endswith("```"):
            text = text[:-3]
            
        text = text.strip()
        
        return json.loads(text)
        
    except json.JSONDecodeError as e:
        return {
            "error": "Failed to parse JSON response from the model.",
            "details": str(e),
            "raw_text": response.text if 'response' in locals() else None
        }
    except Exception as e:
        return {
            "error": "An error occurred during content generation.",
            "details": str(e)
        }
