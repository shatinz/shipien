import sys
sys.path.append("/root/shipien")
from shipienbot import add_sui_client

def main():
    try:
        print("Creating client via bot add_sui_client...")
        link = add_sui_client("test_import_bot", 1, 5)
        print("Success! Link:", link)
    except Exception as e:
        print("Failed:", e)

if __name__ == '__main__':
    main()
