import re
from google import genai
from google.genai import types
import pathlib
import sys
import traceback
from google.genai.errors import ServerError
import time
import os
import json

packageName = sys.argv[1]

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
json_path = pathlib.Path("/app/PolicyGapper/AnalysisResults/AnalysisResultsCollection/"+packageName+".json") 

with open("/app/PolicyGapper/AnalysisResults/AnalysisResultsCollection/"+packageName+".json", 'r') as file:
    data = json.load(file)


def batch_llm_validation_collection():
  prompt = """
You are a Google Play Data Safety compliance expert. Analyze the following JSON of "omitted_declarations" (data types claimed as collected but potentially exempt) from an Android app privacy policy analysis:

## STEP 1: Consistency Check
For each entry:
- Verify if "data_type" logically matches the "policy_reference" content.
- Delete inconsistent entries (e.g., policy mentions cloud sync but data_type is device-only).

## STEP 2: Duplicates Removal
- Remove exact duplicate entries (same data_type + policy_reference).

## STEP 3: Exemption Check (Google Play Data Safety - Collected Data)
Delete entries meeting ANY exemption—no disclosure as "collected" required:

- **Websites collection**: Data collected by websites or any sources that is not the mobile applications.

- **On-device Access/Processing**: Data accessed by app but ONLY processed locally on user's device—NOT sent off-device. Look for: "local storage", "device-only", "not transmitted", "cached locally".
  
- **End-to-End Encryption**: Data sent off-device but unreadable by developer/intermediaries due to E2EE. Keys held ONLY by sender/recipient. Evidence: "end-to-end encrypted", "E2EE", "unreadable by us", "only sender/recipient can decrypt".

CRITICAL: Exempt ONLY if policy EXPLICITLY indicates on-device-only OR proper E2EE. Generic "encrypted" or "secure transmission" does NOT qualify—must confirm developer cannot access plaintext.

## STEP 4: Output Rules
- Respond ONLY with cleaned JSON:
{
"omitted_declarations": [
{ "data_type": "...", "policy_reference": "...",  "justification": "...", "how_to_fix": "...", "lang": "..." }
],
"excluded_declarations": [
{ "data_type": "...", "policy_reference": "...",  "reason_of_removal": "...", "justification": "...","lang": "..." }
]
}
- NEVER add commentary, explanations, or extra text.
- Preserve original structure for remaining entries.
"""

  models_to_try = ["gemini-2.5-pro"]
  source_text = json_path.read_text(encoding="utf-8")
  for model_name in models_to_try:
      print(f"Attempt with model: {model_name}")
      while True:
          try:
              response = client.models.generate_content(
                  model=model_name,
                  contents=[
                      types.Part.from_text(text=prompt),
                      types.Part.from_text(text=source_text)
                  ],
                  config=types.GenerateContentConfig(temperature=0.0)

              )
              print(f"Success with model: {model_name}")
              print(response.text)
              os.makedirs("./AnalysisResultsCollection", exist_ok=True)
              output_file = f"/app/PolicyGapper/AnalysisResults/AnalysisResultsCollection/{packageName}_COLLECTION_VALIDATED.json"
              with open(output_file, "w", encoding="utf-8") as f:
                  f.write(response.text)
              return
          except ServerError as se:
              print(f"ServerError with model {model_name}: {se}")
              traceback.print_exc()
              time.sleep(5)
          except Exception as e:
              print(f"Unexpected error with model {model_name}: {e}")
              traceback.print_exc()
              time.sleep(5)
if __name__ == "__main__":
    batch_llm_validation_collection()
