import requests
import json
import uuid
import random
import string

def main():
    base_url = "http://h2.morningislighting.ir:2095/app/apiv2"
    token = "shipien_bot_token_2026"
    headers = {
        "Token": token
    }

    name = "apitest4"
    password = "".join(random.choices(string.ascii_letters + string.digits, k=10))
    client_uuid = str(uuid.uuid4())

    config_dict = {
        "anytls": {"name": name, "password": password},
        "http": {"password": password, "username": name},
        "hysteria": {"auth_str": password, "name": name},
        "hysteria2": {"name": name, "password": password},
        "mixed": {"password": password, "username": name},
        "naive": {"password": password, "username": name},
        "shadowsocks": {"name": name, "password": "1IIJASI1IVtdx7bPMGyMOzIyS+VBVBFCi60mRtapX/Q="},
        "shadowsocks16": {"name": name, "password": "z09seDSz4la2sJV/hskfjw=="},
        "shadowtls": {"name": name, "password": "1IIJASI1IVtdx7bPMGyMOzIyS+VBVBFCi60mRtapX/Q="},
        "socks": {"password": password, "username": name},
        "trojan": {"name": name, "password": password},
        "tuic": {"name": name, "password": password, "uuid": client_uuid},
        "vless": {"flow": "xtls-rprx-vision", "name": name, "uuid": client_uuid},
        "vmess": {"alterId": 0, "name": name, "uuid": client_uuid}
    }

    client_data = {
        "id": 0,
        "enable": True,
        "name": name,
        "inbounds": [1],
        "config": config_dict,
        "links": [],
        "volume": 0,
        "expiry": 0,
        "desc": "desc4",
        "group": "",
        "remark": "remark4"
    }
    
    params = {
        "object": "clients",
        "action": "new",
        "data": json.dumps(client_data)
    }
    r = requests.post(f"{base_url}/save", params=params, headers=headers)
    print("Status:", r.status_code)
    print("Response:", r.text)

if __name__ == '__main__':
    main()
