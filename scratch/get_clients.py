import requests
import json

def main():
    base_url = "http://h2.morningislighting.ir:2095/app/apiv2"
    token = "shipien_bot_token_2026"
    headers = {
        "Token": token
    }
    r = requests.get(f"{base_url}/clients", headers=headers)
    print("Status:", r.status_code)
    try:
        data = r.json()
        print(json.dumps(data, indent=2))
    except Exception as e:
        print("Error parsing json:", e)
        print("Raw text:", r.text)

if __name__ == '__main__':
    main()
