import os
import google.generativeai as genai
from dotenv import load_dotenv
import json
import re

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# make a simple call
model = genai.GenerativeModel("gemini-2.5-flash")
prompt = """
You are a security triage assistant. Classify this DNS log event.

Return ONLY a JSON object with exactly these fields:
  "verdict": "benign" or "suspicious" or "malicious",
  "severity": "low" or "medium" or "high",
  "confidence": number between 0 and 1,
  "reasoning": "brief explanation in one sentence"

Log event:
Jun 27 20:15:00 dnsmasq[123]: query[A] github.com from 192.168.1.42

JSON response:
"""
response = model.generate_content(prompt)
print(response.text)

# try to parse as JSON    

raw = response.text.strip()
    
# remove any markdown code fences, with or without "json"
# handles: ```json ... ```  and  ``json ... ``  and  ``` ... ```
match = re.search(
    r'`{2,3}(?:json)?\s*\n(.*?)\n\s*`{2,3}',
    raw,
    re.DOTALL
)
    
if match:
    # extract content
    raw = match.group(1).strip()
else:
    # fallback: grab the first { to the last }
    start = raw.find('{')
    end = raw.rfind('}')
    if start != -1 and end != -1:
        raw = raw[start:end+1]
    
try:
    data = json.loads(raw)
    print("Parsed JSON:")
    print(json.dumps(data, indent=2))
except json.JSONDecodeError:
    print("Could not parse JSON. Raw output was:")
    print(raw)    