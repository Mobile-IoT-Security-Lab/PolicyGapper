from google import genai
from google.genai import types
import pathlib
import sys
import traceback
from google.genai.errors import ServerError
import time
import os

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
packageName=sys.argv[1]


txt_path = pathlib.Path("/app/PolicyGapper/AnalysisResults/PreAnalysisResultsShare/"+packageName+".txt")
json_path = pathlib.Path("../DSS/"+packageName+".json")

prompt = """
Act as a privacy auditor for Android apps, expert in Google Play Data Safety.

INPUT:

SUMMARY_PRIVACY_POLICY_TXT: .txt file uploaded

DATA_SAFETY_STATEMENT (DSS) OF THE APP: .json file uploaded

Review scope: Name, Email address, User IDs, Address, Phone number, Race and ethnicity, Political or religious beliefs, Sexual orientation, Other info(Any other personal information such as date of birth, gender identity, veteran status, etc.), User payment info, Purchase history, Credit score, Other financial info(Any other financial information such as user salary or debts),Health info, Fitness info, Approximate location, Precise location.

EXEMPTIONS FROM SHARING DISCLOSURE:

Service providers processing on developer’s behalf.

Legal obligations or government requests.

User-initiated action or prominent disclosure & consent.

Fully anonymized location data sharing.

Sharing within first party or service providers only.

TASK:

Analyze the SUMMARY_PRIVACY_POLICY_TXT to identify implicit or explicit share of scope of review data.

For each such data type identified, check if it is explicitly declared as “shared” in the DSS.

Flag as undeclared sharing any unmatched shares in DSS.


Important:
- Focus only on the data types listed in SCOPE_OF_REVIEW.
- The "policy_reference" field in the output must contain the full, unmodified paragraph from the Privacy Policy where the data collection is explicitly declared, including all context about recipients and purposes; partial or paraphrased excerpts are not acceptable.
- If a specific data type or evidence of share is **not** found in the SUMMARY_PRIVACY_POLICY_TXT, the model must **not hallucinate, infer, guess, or fabricate** any information. 
- Only cite what is explicitly or implicitly **supported by the actual text**. 
- If no relevant content is found, return the empty JSON structure below without adding or inventing anything.

RETURN ONLY valid JSON. NO extra comments. Format:

json
{
  "omitted_declarations": [
    {
      "data_type": "Precise location",
      "policy_reference": "Full unmodified paragraph from Privacy Policy describing sharing of location data...",
      "lang": "English"
    }
  ]
}
If none found, return exactly:

json
{
  "omitted_declarations": []
}

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
                    types.Part.from_text(text=txt_path.read_text(encoding="utf-8")),
                    types.Part.from_text(text=json_path.read_text(encoding="utf-8")),
                ],
                config=types.GenerateContentConfig(temperature=0.0)

            )
            print(f"Success with model: {model_name}")
            print(response.text)
            output_dir = "/app/PolicyGapper/AnalysisResults/AnalysisResultsShare"
            os.makedirs(output_dir, exist_ok=True)  
            output_file = os.path.join(output_dir, f"{packageName}_SharePersonalInfo.json")
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