import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

class PingAnalyzer:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)

    def load_match_participants(self):
        query = """
        SELECT match_id, puuid, win,
               all_in_pings, assist_me_pings, basic_pings, command_pings, danger_pings,
               enemy_missing_pings, enemy_vision_pings, get_back_pings, hold_pings,
               need_vision_pings, on_my_way_pings, push_pings, vision_cleared_pings
        FROM match_participants
        """
        df = pd.read_sql_query(query, self.conn)
        return df

    def analyze_ping_usage(self):
        df = self.load_match_participants()

        ping_columns = [
            'all_in_pings', 'assist_me_pings', 'basic_pings', 'command_pings', 'danger_pings',
            'enemy_missing_pings', 'enemy_vision_pings', 'get_back_pings', 'hold_pings',
            'need_vision_pings', 'on_my_way_pings', 'push_pings', 'vision_cleared_pings'
        ]

        ping_usage = df[ping_columns].sum().sort_values(ascending=False)

        plt.figure(figsize=(12,6))
        ping_usage.plot(kind='bar', color='skyblue')
        plt.title('Total Ping Usage by Type')
        plt.xlabel('Ping Type')
        plt.ylabel('Total Usage')
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.show()

        return df, ping_columns

    def analyze_ping_usage_vs_winrate(self, df, ping_columns):
        df['total_pings'] = df[ping_columns].sum(axis=1)

        bins = [0, 10, 20, 30, 40, 50, 100, 9999]  # 핑 사용량 구간
        labels = ['0-10', '10-20', '20-30', '30-40', '40-50', '50-100', '100+']
        df['ping_bin'] = pd.cut(df['total_pings'], bins=bins, labels=labels, right=False)

        winrates = df.groupby('ping_bin')['win'].mean() * 100

        plt.figure(figsize=(10,6))
        winrates.plot(kind='bar', color='lightgreen')
        plt.title('Ping Usage vs Win Rate')
        plt.xlabel('Total Pings (per player)')
        plt.ylabel('Win Rate (%)')
        plt.ylim(0, 100)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    analyzer = PingAnalyzer('riot_challenger.db')

    df, ping_columns = analyzer.analyze_ping_usage()  
    analyzer.analyze_ping_usage_vs_winrate(df, ping_columns)  
