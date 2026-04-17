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
pdf_path = pathlib.Path("../PPP/"+packageName+".pdf")

try:
    print("Uploading PPP file...")
    sample_1 = client.files.upload(file=pdf_path)
    print("File uploaded successfully")
except Exception as e:
    print(f"Error upload: {e}")
    exit(1)

def batch_llm_validation():
    prompt = """
You are a Privacy Policy Text Extraction Specialist focused on data-sharing disclosures.
Extract and return ALL references to data sharing from the uploaded Privacy Policy Page PDF.

STEP 1: Encoding and Character Preservation

Maintain strict UTF-8 compliance: preserve all special characters (ș, ț, é), punctuation (–, …), and whitespace exactly as in source.

No character substitution, approximation, or normalization.

Ligatures and accented characters must remain exactly as encoded in the PDF.

STEP 2: Data Sharing Definition
Extract ANY text Block mentioning:

Transfer of data to external recipients (third parties, partners, advertisers, service providers).

Keywords: "shared", "transferred", "transmitted", "sent", "disclosed".

Third-party interactions: External entities having "access to", "receiving", or "collecting" user data.

Integration contexts: Analytics, advertising networks, tracking services, or external SDKs.

EXCLUSIONS: Internal processing, local storage, or collection-only statements without mention of external transfer.

STEP 3: Extraction Boundaries

Extract the ENTIRE logical block containing the reference (full paragraph, complete list item, or full table row + headers).

Include essential context: Section headers, purpose statements, and footnotes directly related to sharing.

Preserve document structure: Keep original line breaks, bullet points, and indentation levels exactly.

STEP 4: Verbatim Extraction

Copy text EXACTLY character-for-character (No typo/spelling corrections).

No expansion of abbreviations or modernization of terms.

No paraphrasing, summarizing, or content loss.

STEP 5: Output Rules Respond ONLY with extracted blocks in PDF sequence, verbatim:
[BLOCK 1 - exact text]

[BLOCK 2 - exact text]

[BLOCK 3 - exact text]

If non found:

(empty output indicates no sharing references found)

NEVER add introductory text, explanations, analysis, or extra content. Preserve original order and formatting exactly."""
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
                        sample_1
                    ],
                    config=types.GenerateContentConfig(temperature=0.0)

                )
                print(f"Success with model: {model_name}")
                print(response.text)
                output_dir = "/app/PolicyGapper/AnalysisResults/PreAnalysisResultsShare"
                os.makedirs(output_dir, exist_ok=True)  
                output_file = f"/app/PolicyGapper/AnalysisResults/PreAnalysisResultsShare/{packageName}.txt"
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