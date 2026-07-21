import sqlite3

def main():
    conn = sqlite3.connect('/usr/local/s-ui/db/s-ui.db')
    c = conn.cursor()
    c.execute("SELECT config, links FROM clients WHERE name = 'apitest4'")
    row = c.fetchone()
    print("Config:", row[0][:200] if row else "None")
    print("Links:", row[1] if row else "None")

if __name__ == '__main__':
    main()
