# jsonl.py

import json
from typing import List, Dict, Any, Union, Generator

def dump(data: List[Dict[str, Any]], file_path: str, mode: str = 'w') -> None:
    """
    Writes a list of dictionaries to a JSONL file.

    Each dictionary in the list is serialized to a JSON string and written
    as a new line in the specified file.

    Args:
        data (List[Dict[str, Any]]): A list of dictionaries to write.
        file_path (str): The path to the output JSONL file.
        mode (str): The file writing mode. 'w' to overwrite the file (default),
                    'a' to append to the file.
    """
    if mode not in ['w', 'a']:
        raise ValueError("Mode must be 'w' (write) or 'a' (append).")
    
    with open(file_path, mode, encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

def add(item: Dict[str, Any], file_path: str) -> None:
    """
    Appends a single dictionary to a JSONL file.

    The dictionary is serialized to a JSON string and appended as a new line.

    Args:
        item (Dict[str, Any]): The dictionary to append.
        file_path (str): The path to the JSONL file.
    """
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write(json.dumps(item, ensure_ascii=False) + '\n')

def load(file_path: str) -> List[Dict[str, Any]]:
    """
    Reads a JSONL file and returns a list of dictionaries.

    Each line in the file is parsed as a separate JSON object.

    Args:
        file_path (str): The path to the JSONL file.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries loaded from the file.
    """
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            data.append(json.loads(line))
    return data

def stream_load(file_path: str) -> Generator[Dict[str, Any], None, None]:
    """
    Reads a JSONL file line by line without loading the whole file into memory.

    This is useful for very large files.

    Args:
        file_path (str): The path to the JSONL file.

    Yields:
        Generator[Dict[str, Any], None, None]: A generator that yields one
                                               dictionary at a time.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            yield json.loads(line)

# --- Example Usage ---
if __name__ == '__main__':
    # Define some sample data
    users_batch_1 = [
        {"id": 1, "name": "Alice", "email": "alice@example.com"},
        {"id": 2, "name": "Bob", "email": "bob@example.com", "tags": ["dev", "python"]},
    ]
    users_batch_2 = [
        {"id": 3, "name": "Charlie", "email": "charlie@example.com", "active": True},
        {"id": 4, "name": "Dana", "email": "dana@example.com"},
    ]
    
    file = 'users.jsonl'
    
    print(f"--- Writing initial data to '{file}' using dump() ---")
    dump(users_batch_1, file, mode='w') # Use 'w' to create/overwrite the file

    print(f"--- Appending more data to '{file}' using dump() ---")
    dump(users_batch_2, file, mode='a') # Use 'a' to append

    print(f"--- Appending a single record to '{file}' using add() ---")
    new_user = {"id": 5, "name": "Eve", "email": "eve@example.com"}
    add(new_user, file)

    print(f"\n--- Reading all data from '{file}' using load() ---")
    all_data = load(file)
    print(all_data)
    # Expected output:
    # [{'id': 1, ...}, {'id': 2, ...}, {'id': 3, ...}, {'id': 4, ...}, {'id': 5, ...}]

    print(f"\n--- Reading data from '{file}' as a stream using stream_load() ---")
    for record in stream_load(file):
        print(f"  - Loaded record ID: {record.get('id')}")

    # You can check the contents of 'users.jsonl'. It will look like this:
    # {"id": 1, "name": "Alice", "email": "alice@example.com"}
    # {"id": 2, "name": "Bob", "email": "bob@example.com", "tags": ["dev", "python"]}
    # {"id": 3, "name": "Charlie", "email": "charlie@example.com", "active": true}
    # {"id": 4, "name": "Dana", "email": "dana@example.com"}
    # {"id": 5, "name": "Eve", "email": "eve@example.com"}