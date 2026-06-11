import os
import json
import time
from google import genai
import groq

PRIMARY_PROVIDER = "google-genai"
SECONDARY_PROVIDER = "groq"

MODELS = {
    "google-genai": "gemini-3.5-flash",
    "groq": "llama3-70b-8192"
}

def _call_gemini(prompt: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set.")
    
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=MODELS["google-genai"],
        contents=prompt
    )
    if not response or not response.text:
        raise ValueError("Gemini returned empty response.")
    return response.text.strip()

def _call_groq(prompt: str) -> str:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable is not set.")
        
    client = groq.Groq(api_key=api_key)
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model=MODELS["groq"],
    )
    content = chat_completion.choices[0].message.content
    if not content:
        raise ValueError("Groq returned empty text")
    return content.strip()

def _call_provider(provider: str, prompt: str) -> str:
    if provider == "google-genai":
        return _call_gemini(prompt)
    elif provider == "groq":
        return _call_groq(prompt)
    else:
        raise ValueError(f"Unknown provider: {provider}")

def call_llm(prompt: str) -> str:
    """
    Calls the LLM using the configured primary provider. 
    If it fails, automatically falls back to the secondary provider.
    """
    providers_to_try = [PRIMARY_PROVIDER, SECONDARY_PROVIDER]
    
    last_exception = None
    for i, provider in enumerate(providers_to_try):
        try:
            print(f"[{'Primary' if i == 0 else 'Fallback'}] Attempting to generate using {provider}...")
            
            # Internal retry logic for transient errors (e.g., 503s or rate limits)
            max_retries = 2
            for attempt in range(max_retries + 1):
                try:
                    result = _call_provider(provider, prompt)
                    print(f"Success! {provider} served the request.")
                    return result
                except Exception as e:
                    if attempt < max_retries:
                        wait_time = 2 ** (attempt + 1)
                        print(f"[{provider} attempt {attempt + 1}/{max_retries}] Error: {e}. Retrying in {wait_time}s...")
                        time.sleep(wait_time)
                    else:
                        print(f"[{provider}] Max internal retries reached.")
                        raise e # bubble up to fallback logic
                        
        except Exception as e:
            print(f"Provider {provider} failed completely: {e}")
            last_exception = e
            
    raise Exception(f"All providers failed. Last error: {last_exception}")

def _extract_json(text: str) -> str:
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
        
    if text.endswith("```"):
        text = text[:-3]
        
    return text.strip()

def generate_solution(problem_text: str) -> dict:
    """
    Generates a structured solution for a DSA problem using the configured AI model.
    """
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
    try:
        text = call_llm(prompt)
        text = _extract_json(text)
        return json.loads(text)
    except json.JSONDecodeError as e:
        return {
            "error": "Failed to parse JSON response from the model.",
            "details": str(e),
            "raw_text": text if 'text' in locals() else None
        }
    except Exception as e:
        return {
            "error": "An error occurred during content generation.",
            "details": str(e)
        }

def classify_pattern(problem_text: str) -> str:
    """Classifies a problem into a specific DSA pattern."""
    prompt = f"""
Classify the following problem into exactly ONE of these patterns:
Arrays, Strings, Hashing, Two Pointers, Sliding Window, Stack, Queue, Linked List, Trees, Graphs, Heap, Binary Search, Recursion, Backtracking, Dynamic Programming, Greedy, Bit Manipulation, Math, Tries, Intervals.

Respond with ONLY the exact pattern string, no quotes, no extra text.

Problem:
{problem_text}
"""
    try:
        text = call_llm(prompt)
        return text
    except Exception:
        return "Unknown"

def suggest_questions(pattern: str, sub_pattern_name: str) -> list[dict]:
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
        text = call_llm(prompt)
        text = _extract_json(text)
        return json.loads(text)
    except Exception:
        return []
