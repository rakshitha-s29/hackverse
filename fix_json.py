import json
import os

def fix_json():
    filepath = 'data.json'
    if not os.path.exists(filepath):
        print("File not found")
        return

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            # Note: json.load might fail if there are duplicates effectively but 
            # standard library json.load handles them by picking the last one.
            # However, if there are structural errors (extra/missing brackets), it fails.
            data = json.load(f)
        
        # Rewrite cleaned and beautified
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        print("Successfully fixed and beautified data.json")
    except Exception as e:
        print(f"Error fixing JSON: {e}")

if __name__ == '__main__':
    fix_json()
