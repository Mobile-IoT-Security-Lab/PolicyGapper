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
pdf_path = pathlib.Path("../PPP/"+packageName+".pdf")

try:
    print("Uploading PPP file...")
    sample_1 = client.files.upload(file=pdf_path)
    print("File uploaded successfully")
except Exception as e:
    print(f"Error uploading file: {e}")
    exit(1)
    
def batch_llm_validation_collection():
    prompt = """
You are a Privacy Policy Text Extraction Specialist focused on data-collection disclosures.
Extract and return ALL references to data collection from the uploaded Privacy Policy Page PDF.

STEP 1: Encoding and Character Preservation

Maintain strict UTF-8 compliance: preserve all special characters (ș, ț, é), punctuation (–, …), and whitespace exactly as in source.

No character substitution, approximation, or normalization.

Ligatures and accented characters must remain exactly as encoded in the PDF.

STEP 2: Data Collection Definition
Extract ANY text Block mentioning:

Gathering of personal data (sensors, input, storage, logs, analytics, cookies).

Keywords: "collect", "gather", "obtain", "receive", "access", "read".

GDPR definition: Any operation (recording, structuring, storing) performed on data.

INCLUSIONS: Conditional ("we may collect"), Optional, and Consent-based collection.

EXCLUSIONS: Pure sharing, retention, or deletion clauses without collection references.

STEP 3: Extraction Boundaries

Extract the ENTIRE logical block containing the reference (full paragraph, complete list item, or full table row + headers).

Include essential context: Section headers, purpose statements ("for security"), and legal basis.

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

(empty output indicates no collection references found)

NEVER add introductory text, explanations, analysis, or extra content. Preserve original order and formatting exactly."""

    models_to_try = ["gemini-2.5-pro"]
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
                os.makedirs("/app/PolicyGapper/AnalysisResults/PreAnalysisResultsCollection", exist_ok=True)
                output_file = f"/app/PolicyGapper/AnalysisResults/PreAnalysisResultsCollection/{packageName}.txt"
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
    # post_validation_collection(data)
    batch_llm_validation_collection()
