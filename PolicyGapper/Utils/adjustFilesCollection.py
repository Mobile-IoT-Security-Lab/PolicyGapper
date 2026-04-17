import sys

def remove_first_last_lines(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    if len(lines) <= 2:
        new_lines = []
    else:
        new_lines = lines[1:-1]

    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <file_path>")
        sys.exit(1)
    target_directory1 = "/app/PolicyGapper/AnalysisResults/AnalysisResultsCollection/"
    file_path = sys.argv[1]
    remove_first_last_lines(target_directory1+file_path+".json")

    print(f"First and last lines removed from: {file_path}")
