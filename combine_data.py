import os
import json
import glob
from typing import Dict, Any

def add_to_jsonl(item: Dict[str, Any], file_path: str) -> None:
    """
    Appends a single dictionary to a JSONL file.
    """
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write(json.dumps(item, ensure_ascii=False) + '\n')

def combine_json_to_jsonl(input_dir, output_file):
    """
    Combines all JSON files from a directory into a single JSONL file.
    """
    json_files = glob.glob(os.path.join(input_dir, '*.json'))
    
    # Clear the output file
    with open(output_file, 'w') as f:
        pass

    for json_file in json_files:
        with open(json_file, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                add_to_jsonl(data, output_file)
                print(f"Processed and added {json_file} to {output_file}")
            except json.JSONDecodeError:
                print(f"Skipping invalid JSON file: {json_file}")

if __name__ == '__main__':
    data_directory = '/home/pietkap/projects/hackathons/HackYeah_2025/data'
    output_jsonl_file = '/home/pietkap/projects/hackathons/HackYeah_2025/syntetic_data.jsonl'
    combine_json_to_jsonl(data_directory, output_jsonl_file)
    print(f"All JSON files from '{data_directory}' have been combined into '{output_jsonl_file}'.")
