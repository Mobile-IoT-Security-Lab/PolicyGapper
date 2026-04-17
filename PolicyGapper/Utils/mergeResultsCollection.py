import json
import sys
from collections import defaultdict

def merge_omitted_declarations(results):
    """Merge multiple LLM results containing 'omitted_declarations' into a single comprehensive list."""
    all_declarations = []
    
    for result in results:
        if 'omitted_declarations' in result:
            all_declarations.extend(result['omitted_declarations'])
    
    seen = set()
    declarations = []
    
    for decl in all_declarations:
        key = (decl['data_type'], decl['policy_reference'], decl['lang'])
        seen.add(key)
        declarations.append(decl)
    
    return {
        "omitted_declarations": declarations
    }

def main():
    if len(sys.argv) < 3:
        print("Usage: python merge_results.py res1.json res3.json")
        sys.exit(1)
    
    results = []
    output_name=sys.argv[1].split("_")
    output_name=output_name[0]
    for filepath in sys.argv[1:]:
        try:
            with open("/app/PolicyGapper/AnalysisResults/AnalysisResultsCollection/"+filepath, 'r', encoding='utf-8') as f:
                result = json.load(f)
                results.append(result)
                print(f"Loaded {filepath}: {len(result.get('omitted_declarations', []))} declarations")
        except FileNotFoundError:
            print(f"Error: File {filepath} not found")
            sys.exit(1)
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in {filepath}")
            sys.exit(1)
    
    merged_result = merge_omitted_declarations(results)
    
    print(json.dumps(merged_result, indent=2, ensure_ascii=False))
    
    output_file = "/app/PolicyGapper/AnalysisResults/AnalysisResultsCollection/"+output_name+'.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(merged_result, f, indent=2, ensure_ascii=False)
    print(f"\nSaved to {output_file}")

if __name__ == "__main__":
    main()
