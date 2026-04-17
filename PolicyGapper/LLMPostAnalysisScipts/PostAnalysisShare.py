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



packageName=sys.argv[1]

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
json_path = pathlib.Path("/app/PolicyGapper/AnalysisResults/AnalysisResultsShare/"+packageName+".json")

with open("/app/PolicyGapper/AnalysisResults/AnalysisResultsShare/"+packageName+".json", 'r') as file:
    data = json.load(file)

def batch_llm_validation():
    prompt = """
You are a Google Play Data Safety compliance expert. Analyze the following JSON of "omitted_declarations" from an Android app privacy policy analysis:

## STEP 1: Consistency Check
For each entry:
- Verify if "data_type" logically matches the "policy_reference" content.
- Delete any inconsistent entries (e.g., if policy mentions analytics but data_type is unrelated).

## STEP 2: Duplicates Removal
- Remove exact duplicate entries (same data_type + policy_reference).

## STEP 3: Exemption Check (Google Play User Data Policy)
Delete entries meeting ANY exemption—no disclosure as "sharing" required:
- **Service Providers**: Policy shows SDKs/partners processing ON BEHALF OF developer under their instructions (e.g., "we authorise partners to provide services", "share necessary info to implement functions").
- **Legal Purposes**: Explicit legal obligations/government requests.
- **User-Initiated/Consent**: User action or prominent disclosure+consent.
- **Anonymous Data**: Fully anonymized, non-identifiable.
- **First-Party Only**: No third-party beyond service providers.

CRITICAL: SDKs like Firebase, Google Analytics, AdMob, Facebook SDK, Appsflyer are typically service providers if used for app functions/crash reporting/push—not independent third-party profiling. Check policy language for "on our behalf" or "to implement our services".

## STEP 4: Output Rules
- Respond ONLY with cleaned JSON: 
{
"omitted_declarations": [
{ "data_type": "...", "policy_reference": "...",  "justification": "...", "how_to_fix": "...", "lang": "..." }
],
"excluded_declarations": [
{ "data_type": "...", "policy_reference": "...",  "reason_of_removal": "...", "justification": "...", "lang": "..." }
]
}
- NEVER add commentary, explanations, or extra text.
- Preserve original structure for remaining entries.

"""

    models_to_try = [
        "gemini-2.5-pro"
    ]


    for model_name in models_to_try:
        print(f"Attempt with model: {model_name}")
        while True:  
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=[
                        types.Part.from_text(text=prompt),
                        types.Part.from_text(text=json_path.read_text(encoding="utf-8"))
                    ],
                    config=types.GenerateContentConfig(temperature=0.0)

                )
                print(f"Success with model: {model_name}")
                print(response.text)
                output_dir = "/app/PolicyGapper/AnalysisResults/AnalysisResultsShare"
                os.makedirs(output_dir, exist_ok=True)  
                output_file = os.path.join(output_dir, f"{packageName}_SHARE_VALIDATED.json")
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(response.text)
                break  
            except ServerError as se:
                print(f"ServerError with model {model_name}: {se}")
                traceback.print_exc()
                time.sleep(5)  
            except Exception as e:
                print(f"Unexpected error with model {model_name}: {e}")
                traceback.print_exc()
                time.sleep(5)  
                
batch_llm_validation()