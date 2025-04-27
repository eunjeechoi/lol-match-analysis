import sqlite3
import pandas as pd

class ChampionAnalyzer:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)

    def load_match_participants(self):
        query = """
        SELECT match_id, champion_id, champion_name, win
        FROM match_participants
        """
        df = pd.read_sql_query(query, self.conn)
        return df

    def load_match_bans(self):
        query = """
        SELECT match_id, ban1, ban2, ban3, ban4, ban5
        FROM match_bans
        """
        df = pd.read_sql_query(query, self.conn)
        return df

    def analyze_champion_pick_and_ban(self):
        participants = self.load_match_participants()
        bans = self.load_match_bans()

        total_players = participants.shape[0]
        pick_counts = participants.groupby(['champion_id', 'champion_name']).size()
        win_counts = participants[participants['win'] == 1].groupby(['champion_id', 'champion_name']).size()

        pick_rate = (pick_counts / total_players) * 100
        win_rate = (win_counts / pick_counts) * 100

        ban_data = pd.melt(bans, id_vars=['match_id'], value_vars=['ban1', 'ban2', 'ban3', 'ban4', 'ban5'],
                           var_name='ban_slot', value_name='champion_id')

        total_teams = bans['match_id'].nunique()
        ban_counts = ban_data['champion_id'].value_counts()
        ban_rate = (ban_counts / total_teams) * 100

        result = pd.DataFrame({
            'Pick Count': pick_counts,
            'Win Count': win_counts,
            'Pick Rate (%)': pick_rate,
            'Win Rate (%)': win_rate
        }).fillna(0)

        result = result.reset_index().set_index('champion_id')
        result['Ban Count'] = ban_counts
        result['Ban Rate (%)'] = ban_rate
        result = result.fillna(0)
        result = result.reset_index()

        table_name = "champion_pick_ban_stats"
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(f"DROP TABLE IF EXISTS {table_name}")
            result.to_sql(table_name, conn, index=False, if_exists='replace')

        print(f"\n[INFO] 분석 결과가 '{table_name}' 테이블로 저장되었습니다.")
        print(result[['champion_id', 'champion_name', 'Pick Rate (%)', 'Win Rate (%)', 'Pick Count', 'Ban Rate (%)', 'Ban Count']])

if __name__ == "__main__":
    analyzer = ChampionAnalyzer('riot_challenger.db')
    analyzer.analyze_champion_pick_and_ban()
