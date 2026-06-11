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
  "pattern": "Primary Pattern Here",
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
For the "pattern" field, pick the SINGLE best-fit primary pattern from this exact list ONLY:
Arrays, Strings, Hashing, Two Pointers, Sliding Window, Stack, Queue, Linked List, Trees, Graphs, Heap, Binary Search, Recursion, Backtracking, Dynamic Programming, Greedy, Bit Manipulation, Math, Tries, Intervals.

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

def classify_pattern(problem_text: str) -> str:
    """Classifies a problem into a specific DSA pattern."""
    if CONFIG["provider"] != "google-genai":
        return "Unknown"
        
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "Unknown"

    client = genai.Client(api_key=api_key)
    
    prompt = f"""
Classify the following problem into exactly ONE of these patterns:
Arrays, Strings, Hashing, Two Pointers, Sliding Window, Stack, Queue, Linked List, Trees, Graphs, Heap, Binary Search, Recursion, Backtracking, Dynamic Programming, Greedy, Bit Manipulation, Math, Tries, Intervals.

Respond with ONLY the exact pattern string, no quotes, no extra text.

Problem:
{problem_text}
"""
    try:
        response = client.models.generate_content(
            model=CONFIG["model"],
            contents=prompt
        )
        return response.text.strip()
    except Exception:
        return "Unknown"

def suggest_questions(pattern: str, sub_pattern_name: str) -> list[dict]:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return []
        
    client = genai.Client(api_key=api_key)
    
    prompt = f"""
You are an expert algorithms instructor.
For the DSA pattern '{pattern}' and specific sub-pattern '{sub_pattern_name}', suggest exactly 4 to 5 canonical, well-known interview questions (e.g. from LeetCode or similar).
Return ONLY a raw JSON list of objects, with NO markdown code fences (like ```json), NO extra text.
Each object must have exactly these keys: "question_title" (string), "difficulty" (string: "Easy", "Medium", or "Hard").

Example format:
[
  {{"question_title": "Two Sum", "difficulty": "Easy"}},
  {{"question_title": "3Sum", "difficulty": "Medium"}}
]
"""
    try:
        response = client.models.generate_content(
            model=CONFIG["model"],
            contents=prompt
        )
        text = response.text.strip()
        if text.startswith("```json"): text = text[7:]
        elif text.startswith("```"): text = text[3:]
        if text.endswith("```"): text = text[:-3]
        text = text.strip()
        
        return json.loads(text)
    except Exception:
        return []
