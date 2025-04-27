import sqlite3
import requests
import time
import json

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

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS match_events (
            match_id TEXT,
            timestamp INTEGER,
            type TEXT,
            actor_id INTEGER,
            assisting_participant_ids TEXT,
            victim_id INTEGER,
            ward_type TEXT,
            skill_slot INTEGER,
            item_id INTEGER,
            team_id INTEGER,
            feat_type TEXT,
            feat_value INTEGER,
            lane_type TEXT,
            monster_type TEXT,
            monster_sub_type TEXT,
            building_type TEXT,
            tower_type TEXT,
            winning_team INTEGER
        )
    ''')

    conn.commit()
    return conn

def fetch_timeline_data(requester, match_id):
    url = f"https://asia.api.riotgames.com/lol/match/v5/matches/{match_id}/timeline"
    response = requester.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"[ERROR] match_id {match_id} timeline 요청 실패: {response.status_code}")
        return None

def save_timeline_to_db(conn, timeline_data):
    cursor = conn.cursor()
    match_id = timeline_data['metadata']['matchId']

    cursor.execute("DELETE FROM match_events WHERE match_id = ?", (match_id,))
    conn.commit()

    frames = timeline_data['info']['frames']

    for frame in frames:
        events = frame.get('events', [])
        for event in events:
            event_type = event.get('type')
            actor_id = event.get('participantId') or event.get('killerId') or event.get('creatorId')
            assisting_ids = event.get('assistingParticipantIds')
            assisting_ids_str = ",".join(map(str, assisting_ids)) if assisting_ids else None
            victim_id = event.get('victimId')
            ward_type = event.get('wardType')
            skill_slot = event.get('skillSlot')
            item_id = event.get('itemId')
            team_id = event.get('teamId') or event.get('killerTeamId')
            feat_type = event.get('featType')
            feat_value = event.get('featValue')
            lane_type = event.get('laneType')
            monster_type = event.get('monsterType')
            monster_sub_type = event.get('monsterSubType')
            building_type = event.get('buildingType')
            tower_type = event.get('towerType')
            winning_team = event.get('winningTeam')

            cursor.execute('''
                INSERT INTO match_events (
                    match_id, timestamp, type, actor_id, assisting_participant_ids, victim_id,
                    ward_type, skill_slot, item_id, team_id, feat_type, feat_value,
                    lane_type, monster_type, monster_sub_type, building_type, tower_type, winning_team
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                match_id,
                event.get('timestamp'),
                event_type,
                actor_id,
                assisting_ids_str,
                victim_id,
                ward_type,
                skill_slot,
                item_id,
                team_id,
                feat_type,
                feat_value,
                lane_type,
                monster_type,
                monster_sub_type,
                building_type,
                tower_type,
                winning_team
            ))

    conn.commit()

def process_all_timelines(api_key, conn):
    requester = RateLimitedRequester(api_key)
    cursor = conn.cursor()
    cursor.execute("SELECT match_id FROM match_summary")
    match_ids = [row[0] for row in cursor.fetchall()]

    for idx, match_id in enumerate(match_ids, 1):
        timeline_data = fetch_timeline_data(requester, match_id)
        if timeline_data:
            save_timeline_to_db(conn, timeline_data)
            print(f"[{idx}/{len(match_ids)}] match_id {match_id} timeline 저장 완료")
        else:
            print(f"[{idx}/{len(match_ids)}] match_id {match_id} timeline 저장 실패")

def main():
    api_key = ''
    conn = create_connection_and_table()
    process_all_timelines(api_key, conn)
    conn.close()

if __name__ == "__main__":
    main()
