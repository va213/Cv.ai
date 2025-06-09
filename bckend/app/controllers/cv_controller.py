from flask import request, jsonify
from app.services.pdf_service import extract_text_from_pdf
from app.services.ollama_service import query_ollama_for_json
from app.services.db_service import insert_to_db, get_all_cv_data
import json
from io import BytesIO
from flask_cors import cross_origin
from ..log_config import setup_logger

@cross_origin()
def upload_cv():
    logger=setup_logger()
    if 'files' not in request.files:
        return jsonify({"error": "No files part"}), 400

    files = request.files.getlist('files')
    results = []

    for file in files:

        if file.filename == '':
            continue
        try:
            file_stream = BytesIO(file.read())
            text = extract_text_from_pdf(file_stream)
            structured_data = query_ollama_for_json(text)
            insert_to_db(structured_data)
            results.append({"filename": file.filename, "status": "success", "data": structured_data})
            logger.info(f"Processed file: {file.filename}, Extracted data: {structured_data}")
        except Exception as e:
            results.append({"filename": file.filename, "status": "error", "error": str(e)})

    return jsonify({"message": "CV processing complete", "results": results})

@cross_origin()
def query_cv():
    logger=setup_logger()

    try:
        user_query = request.json.get("query", "")
        logger.info(f"user_query :{user_query}")
        if not user_query:
            return jsonify({"error": "Query is required"}), 400

        # Fetch all applicant rows
        rows = get_all_cv_data()
        headers = [
            "Name", "Email", "Phone", "Location", "Education", "Skills",
            "Experience Years", "Current Company", "Expected Salary",
            "Notice Period", "Portfolio Link"
        ]

        # Combine all applicant data as text
        all_applicants_text = ""
        for row in rows:
            applicant_data = {headers[i]: row[i] for i in range(len(headers))}
            applicant_str = "\n".join(f"{key}: {value}" for key, value in applicant_data.items())
            all_applicants_text += f"---\n{applicant_str}\n"
        logger.info(f"applicants:{all_applicants_text}")
        
#"give me applicants who satisfy the the conditons knows[React,python],softskills[leadership], "location": ["Bangalore"],yearsExp:3, score: "600"
        # Define prompt safely with .format()
        prompt_template = """
You are a top-tier recruitment assistant.

You are provided with structured CV data from multiple applicants. Your task is to evaluate how closely each applicant matches the ideal profile based on the job-related question provided.

-----------------------
Question:
"{user_query}"
-----------------------

Here is the structured list of applicants:

{all_applicants_text}


Output Requirements:
- Return **only** a valid JSON array of objects, without any explanation or commentary.
- Do **not** include any extra text before or after the JSON.
- DO not return anything other than the given JSON format.
- If a field is not available, return an empty string "".
- The output must be in this exact JSON format:

[
  {{
    "name": "Alice Johnson",
    "email": "alice@example.com",
    "experience": "5 years",
    "contact": "+91-9876543210",
    "score": 92
  }},
  {{
    "name": "Bob Singh",
    "email": "bob@example.com",
    "experience": "",
    "contact": "",
    "score": 74
  }}
]


1.. For each applicant, evaluate and assign a score between 0 and 100 based on relevance:
   - 100 = perfect match
   - 0 = no match
   - Use intermediate scores for partial relevance.
2. Return ONLY a valid JSON array, where each applicant object contains the following fields:
   - "name" (string): Full name
   - "email" (string): Email address
   - "experience" (string): Total experience (e.g., "3 years" or "" if not available)
   - "contact" (string): Phone number or "" if not available
   - "score" (integer): Matching score between 0–100




"""

        prompt = prompt_template.format(
            user_query=user_query,
            all_applicants_text=all_applicants_text
        )

        # Send to model
        from app.services.ollama_service import query_ollama_direct

        model_answer = query_ollama_direct(prompt)
        logger.info(f"Model answer: {model_answer},user given query:{user_query}")

        # Try parsing the result
        try:
            parsed_json = json.loads(model_answer)
            return jsonify({
                "question": user_query,
                "results": parsed_json
            })
        except json.JSONDecodeError as e:
            return jsonify({
                "error": "Model returned invalid JSON",
                "raw_response": model_answer,
                "details": str(e)
            }), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500