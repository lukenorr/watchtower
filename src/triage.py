import os
import json
import re
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.environ['GEMINI_API_KEY'])
MODEL_NAME = "gemini-2.5-flash"

def gemini_triage_event(event):
    """send parsed DNS event to gemini for triage"""

    prompt = f"""\
    You are a security triage assistant. Classify this DNS log event.

    Return ONLY a JSON object with exactly these fields:
    - "verdict": "benign" or "suspicious" or "malicious"
    - "severity": "low" or "medium" or "high"
    - "confidence": number between 0 and 1
    - "reasoning": "brief explanation in one sentence"

    DNS Event:
    Domain: {event.get("domain", "unknown")}
    Client IP: {event.get("client_ip", "unknown")}
    Query Type: {event.get("query_type", "unknown")}
    Raw log: {event.get("raw_log", "")}

    JSON response:
    """

    model = genai.GenerativeModel(MODEL_NAME)
    response = model.generate_content(prompt)

    # collect the response
    raw = response.text.strip()

    # look for code fence pattern
    match = re.search(
        r'`{2,3}(?:json)?\s*\n(.*?)\n\s*`{2,3}',
        raw,
        re.DOTALL
    )
    if match:
        # keep only the json
        raw = match.group(1).strip()
    else:
        # cut out the json
        start = raw.find('{')
        end = raw.rfind('}')
        if start != -1 and end != -1:
            raw = raw[start:end+1]

    # parse json and handle errors
    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        result = {
            "verdict" : "unknown", 
            "severity" : "low",
            "confidence" : 0.0,
            "reasoning" : f"JSON parse failed. Raw response: {raw[:200]} "
        }
    return result


if __name__ == "__main__":
    # smoke test
    sample = {
        "domain": "suspicious-xyz.xyz",
        "client_ip": "192.168.1.100",
        "query_type": "A",
        "raw_log": "query: A suspicious-xyz.xyz from 192.168.1.100"
    }

    result = gemini_triage_event(sample)
    print(json.dumps(result, indent=2))