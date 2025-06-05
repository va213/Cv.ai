import requests
import json

def query_ollama_for_json(text):
    prompt = f"""
You are an expert resume parser.

Extract the following fields from the resume text exactly as JSON with keys:

- Name (string, required, set to empty string if not found)
- Email (string, required, set to empty string if not found)
- Phone (string, required, set to empty string if not found)
- Location (string, optional, set to null if not found)
- Education (string, required, set to the closest thing you find which is related,if not set null)
- Skills (string, required, set to empty string if not found)
- Experience Years (integer, required, set to empty string if not found)
- Current Company (string, required, set to null if not found)
- Expected Salary (string, optional, set to null if not found)
- Notice Period (string, optional, set to null if not found)
- Portfolio Link (string URL, optional, set to null if not found)

Do NOT add any explanations or extra text. ONLY output a valid JSON object with these keys and appropriate values.

If a field is missing or unknown:
- Analyze the skills and separate it by "," to insert in the skill field
- For required fields (Name, Email, Phone), set the value to an empty string ""
- For optional fields, set the value to null

Here is the resume text:
\"\"\"{text[:3000]}\"\"\"

Output ONLY the JSON now.
"""
    response = requests.post("http://localhost:11434/api/generate", json={
        "model": "llama3",
        "prompt": prompt,
        "stream": False
    })
    print("RAW OLLAMA RESPONSE:", response.text)
    try:
        response_json = response.json()
        raw_text = response_json.get("response", "").strip()
        return json.loads(raw_text)
    except Exception as e:
        raise ValueError(f"Ollama returned invalid JSON:\n{response.text}\n\nError: {e}")

def query_ollama_direct(prompt):
    try:
        response = requests.post("http://localhost:11434/api/generate", json={
            "model": "llama3",
            "prompt": prompt,
            "stream": False
        })

        response.raise_for_status()  # Raises HTTPError for bad responses (4xx or 5xx)
        response_json = response.json()

        return response_json.get("response", "").strip()

    except requests.exceptions.RequestException as e:
        print(f"Error during Ollama request: {e}")
        return ""

