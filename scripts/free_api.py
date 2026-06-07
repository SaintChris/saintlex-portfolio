import json, random, os, sys

def main():
    data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'free-apis.json'))
    out_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'public', 'daily-api.json'))
    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            apis = json.load(f)
    except Exception as e:
        print(f'Error loading APIs: {e}', file=sys.stderr)
        sys.exit(1)
    if not isinstance(apis, list) or not apis:
        print('API list empty or invalid', file=sys.stderr)
        sys.exit(1)
    entry = random.choice(apis)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(entry, f, ensure_ascii=False, indent=2)
    print('Wrote daily API entry to', out_path)

if __name__ == '__main__':
    main()
