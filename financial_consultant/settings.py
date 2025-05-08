from google.genai import types


GenerateContentConfig = types.GenerateContentConfig(
    temperature=0.0,
    max_output_tokens=512,
    candidate_count=1,
)
DefaultModel = "gemini-2.0-flash-lite-001"
