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
            time.sleep(120)  
        elif self.request_count % 20 == 0:
            print(f"[INFO] 20개 요청 완료, 1초간 대기...")
            time.sleep(1)  

        headers = {"X-Riot-Token": self.api_key}
        response = requests.get(url, headers=headers)
        return response

def create_connection_and_table(db_name='riot_challenger.db'):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # match_summary 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS match_summary(
            match_id TEXT PRIMARY KEY,
            game_mode TEXT,
            game_version TEXT,
            game_type TEXT,
            map_id INTEGER,
            queue_id INTEGER,
            game_duration INTEGER
        )
    ''')

    # match_participants 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS match_participants(
            match_id TEXT,
            puuid TEXT,
            riot_id_game_name TEXT,
            champion_name TEXT,
            champion_id INTEGER,
            individual_position TEXT,
            lane TEXT,
            item0 INTEGER,
            item1 INTEGER,
            item2 INTEGER,
            item3 INTEGER,
            item4 INTEGER,
            item5 INTEGER,
            item6 INTEGER,
            kills INTEGER,
            deaths INTEGER,
            assists INTEGER,
            all_in_pings INTEGER,
            assist_me_pings INTEGER,
            basic_pings INTEGER,
            command_pings INTEGER,
            danger_pings INTEGER,
            enemy_vision_pings INTEGER,
            enemy_missing_pings INTEGER,
            get_back_pings INTEGER,
            hold_pings INTEGER,
            need_vision_pings INTEGER,
            retreat_pings INTEGER,
            on_my_way_pings INTEGER,
            push_pings INTEGER,
            vision_cleared_pings INTEGER,
            detector_wards_placed INTEGER,
            wards_killed INTEGER,
            ward_placed INTEGER,
            vision_score INTEGER,
            win INTEGER,
            PRIMARY KEY (match_id, puuid)
        )
    ''')

    # match_teams 테이블
    cursor.execute('DROP TABLE IF EXISTS match_teams')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS match_teams(
            match_id TEXT,
            team_id INTEGER,
            win INTEGER,
            feats_epic_monster_kill INTEGER,
            feats_first_blood INTEGER,
            feats_first_turret INTEGER,
            champion_first INTEGER,
            champion_kill INTEGER,
            dragon_first INTEGER,
            dragon_kill INTEGER,
            horde_first INTEGER,
            horde_kill INTEGER,
            rift_herald_first INTEGER,
            rift_herald_kill INTEGER,
            atakhan_first INTEGER,
            atakhan_kill INTEGER,
            baron_first INTEGER,
            baron_kill INTEGER,
            tower_first INTEGER,
            tower_kill INTEGER,
            inhibitor_first INTEGER,
            inhibitor_kill INTEGER,
            PRIMARY KEY (match_id, team_id)
        )
    ''')

    # match_bans 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS match_bans(
            match_id TEXT PRIMARY KEY,
            ban1 INTEGER,
            ban2 INTEGER,
            ban3 INTEGER,
            ban4 INTEGER,
            ban5 INTEGER,
            ban6 INTEGER,
            ban7 INTEGER,
            ban8 INTEGER,
            ban9 INTEGER,
            ban10 INTEGER
        )
    ''')

    conn.commit()
    return conn

def fetch_match_data(requester, match_id):
    url = f"https://asia.api.riotgames.com/lol/match/v5/matches/{match_id}"
    response = requester.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"[ERROR] match_id {match_id} 요청 실패: {response.status_code}")
        return None

def save_match_to_db(conn, match_data):
    cursor = conn.cursor()
    info = match_data['info']
    metadata = match_data['metadata']
    match_id = metadata['matchId']

    queue_id = info.get('queueId')
    if queue_id != 420:
        print(f"[SKIP] match_id {match_id}는 queue_id {queue_id}입니다 (건너뜀)")
        return
  
    cursor.execute('''
        INSERT OR IGNORE INTO match_summary (
            match_id, game_mode, game_version, game_type,
            map_id, queue_id, game_duration
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        match_id,
        info.get('gameMode'),
        info.get('gameVersion'),
        info.get('gameType'),
        info.get('mapId'),
        info.get('queueId'),
        info.get('gameDuration')
    ))

    for p in info['participants']:
        cursor.execute('''
            INSERT OR IGNORE INTO match_participants (
                match_id, puuid, riot_id_game_name, champion_name, champion_id,
                individual_position, lane, item0, item1, item2, item3, item4, item5, item6,
                kills, deaths, assists,
                all_in_pings, assist_me_pings, basic_pings, command_pings, danger_pings,
                enemy_vision_pings, enemy_missing_pings, get_back_pings, hold_pings,
                need_vision_pings, retreat_pings, on_my_way_pings, push_pings,
                vision_cleared_pings, detector_wards_placed, wards_killed, ward_placed,
                vision_score, win
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            match_id,
            p.get('puuid'),
            p.get('riotIdGameName'),
            p.get('championName'),
            p.get('championId'),
            p.get('individualPosition'),
            p.get('lane'),
            p.get('item0'),
            p.get('item1'),
            p.get('item2'),
            p.get('item3'),
            p.get('item4'),
            p.get('item5'),
            p.get('item6'),
            p.get('kills'),
            p.get('deaths'),
            p.get('assists'),
            p.get('allInPings'),
            p.get('assistMePings'),
            p.get('basicPings'),
            p.get('commandPings'),
            p.get('dangerPings'),
            p.get('enemyVisionPings'),
            p.get('enemyMissingPings'),
            p.get('getBackPings'),
            p.get('holdPings'),
            p.get('needVisionPings'),
            p.get('retreatPings'),
            p.get('onMyWayPings'),
            p.get('pushPings'),
            p.get('visionClearedPings'),
            p.get('detectorWardsPlaced'),
            p.get('wardsKilled'),
            p.get('wardsPlaced'),
            p.get('visionScore'),
            int(p.get('win'))
        ))
   
    for team in info['teams']:
        cursor.execute('''
            INSERT OR IGNORE INTO match_teams (
                match_id, team_id, win,
                feats_epic_monster_kill,feats_first_blood,feats_first_turret,
                champion_first, champion_kill,
                dragon_first, dragon_kill,
                horde_first, horde_kill,
                rift_herald_first, rift_herald_kill,
                atakhan_first, atakhan_kill,
                baron_first, baron_kill,
                tower_first, tower_kill,
                inhibitor_first, inhibitor_kill
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?,?,?)
        ''', (
            match_id,
            team.get('teamId'),
            int(team.get('win')),
            int(team['feats']['EPIC_MONSTER_KILL']['featState']),
            int(team['feats']['FIRST_BLOOD']['featState']),
            int(team['feats']['FIRST_TURRET']['featState']),
            int(team['objectives']['champion']['first']),
            team['objectives']['champion']['kills'],
            int(team['objectives']['dragon']['first']),
            team['objectives']['dragon']['kills'],
            int(team['objectives']['horde']['first']),
            team['objectives']['horde']['kills'],
            int(team['objectives']['riftHerald']['first']),
            team['objectives']['riftHerald']['kills'],
            int(team['objectives']['atakhan']['first']),
            team['objectives']['atakhan']['kills'],
            int(team['objectives']['baron']['first']),
            team['objectives']['baron']['kills'],
            int(team['objectives']['tower']['first']),
            team['objectives']['tower']['kills'],
            int(team['objectives']['inhibitor']['first']),
            team['objectives']['inhibitor']['kills']
        ))
    
    bans = []
    for team in info['teams']:
        for ban in team.get('bans', []):
            bans.append(ban.get('championId', 0))

    cursor.execute('''
        INSERT OR IGNORE INTO match_bans (
            match_id, ban1, ban2, ban3, ban4, ban5, ban6, ban7, ban8, ban9, ban10
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (match_id, *bans))
    
    
    conn.commit()

def process_all_matches(api_key, conn):
    requester = RateLimitedRequester(api_key)
    cursor = conn.cursor()
    cursor.execute("SELECT match_id FROM challenger_matchid")
    match_ids = [row[0] for row in cursor.fetchall()]

    for idx, match_id in enumerate(match_ids, 1):
        match_data = fetch_match_data(requester, match_id)
        if match_data:
            save_match_to_db(conn, match_data)
            print(f"[{idx}/{len(match_ids)}] match_id {match_id} 저장 완료")
        else:
            print(f"[{idx}/{len(match_ids)}] match_id {match_id} 저장 실패")

def main():
    api_key = ''
    conn = create_connection_and_table()
    process_all_matches(api_key, conn)
    conn.close()

if __name__ == "__main__":
    main()
