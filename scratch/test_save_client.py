import requests
import json

def main():
    base_url = "http://h2.morningislighting.ir:2095/app/apiv2"
    token = "shipien_bot_token_2026"
    
    headers = {
        "Token": token
    }
    
    # Let's try form-urlencoded first
    print("Trying Form-urlencoded...")
    client_data = {
        "id": 0,
        "enable": True,
        "name": "apitestclient1",
        "inbounds": [1],
        "volume": 0,
        "expiry": 0,
        "desc": "desc1",
        "group": "",
        "remark": "remark1"
    }
    
    post_data = {
        "object": "clients",
        "action": "new",
        "data": json.dumps(client_data)
    }
    
    r = requests.post(f"{base_url}/save", data=post_data, headers=headers)
    print("Form-urlencoded Status:", r.status_code)
    print("Form-urlencoded Response:", r.text)

    # Let's try JSON content-type with object, action, data as keys
    print("\nTrying JSON request body...")
    json_headers = {
        "Token": token,
        "Content-Type": "application/json"
    }
    json_data = {
        "object": "clients",
        "action": "new",
        "data": json.dumps(client_data)
    }
    r = requests.post(f"{base_url}/save", json=json_data, headers=json_headers)
    print("JSON Status:", r.status_code)
    print("JSON Response:", r.text)

if __name__ == '__main__':
    main()
