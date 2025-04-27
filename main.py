import requests
import sqlite3
import time
import datetime

class RateLimitedRequester:
    def __init__(self, api_key):
        self.api_key = api_key
        self.request_count = 0

    def get(self, url):
        self.request_count += 1

        if self.request_count % 100 == 0:
            print(f"[INFO] 100개 요청 완료, 2분간 대기...")
            time.sleep(120)  # 2분(120초) 대기

        elif self.request_count % 20 == 0:
            print(f"[INFO] 20개 요청 완료, 1초간 대기...")
            time.sleep(1)  

        headers = {"X-Riot-Token": self.api_key}
        response = requests.get(url, headers=headers)
        return response

def create_connection_and_table(db_name='riot_challenger.db'):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS challenger_puuid (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            puuid TEXT UNIQUE
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS challenger_matchid (
            match_id TEXT PRIMARY KEY
        )
    ''')
    conn.commit()
    return conn

def fetch_and_store_challenger_puuids(api_key, conn):
    url = f"https://kr.api.riotgames.com/lol/league/v4/challengerleagues/by-queue/RANKED_SOLO_5x5?api_key={api_key}"
    response = requests.get(url)
    
    if response.status_code == 200:
        entries = response.json()['entries']
        cursor = conn.cursor()
        for idx, entry in enumerate(entries, 1):
            puuid = entry['puuid']
            cursor.execute("INSERT OR IGNORE INTO challenger_puuid (puuid) VALUES (?)", (puuid,))
            print(f"[{idx}/{len(entries)}] 챌린저 puuid 저장 중...")
        conn.commit()
        print(f"총 저장된 ID 수: {len(entries)}")
    else:
        print(f"[ERROR] Riot API 응답 실패: {response.status_code}")

def fetch_and_store_match_id(api_key, conn):
    cursor = conn.cursor()
    cursor.execute("SELECT puuid FROM challenger_puuid")
    puuids = [row[0] for row in cursor.fetchall()]

    yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
    weekago = datetime.datetime.now() - datetime.timedelta(days=7)
    start = int(weekago.replace(hour=0,minute=0,second=0,microsecond=0).timestamp())
    end = int(yesterday.replace(hour=23,minute=59,second=59,microsecond=999999).timestamp())

    total_matches = set()
    requester = RateLimitedRequester(api_key)
    
    for idx,puuid in enumerate(puuids,1):
        url = f"https://asia.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?startTime={start}&endTime={end}&api_key={api_key}"
        response = requester.get(url)
        
        if response.status_code == 200:
            match_ids = response.json()
            total_matches.update(match_ids)
            print(f"[{idx}/{len(puuids)}] {len(match_ids)}개 match ID 수집 완료 (누적 {len(total_matches)}개)")
        else:
            print(f"[ERROR] {idx}번째 puuid 요청 실패: {response.status_code}")
    
    for match_id in total_matches:
        cursor.execute("INSERT OR IGNORE INTO challenger_matchid (match_id) VALUES (?)", (match_id,))
    conn.commit()
    print(f"최종 저장된 match ID 수: {len(total_matches)}")

def main():
    api_key = ''
    conn = create_connection_and_table()
    fetch_and_store_challenger_puuids(api_key, conn)
    fetch_and_store_match_id(api_key,conn)
    conn.close()

if __name__ == "__main__":
    main()