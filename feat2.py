import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

class FeatAnalyzer:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)

    def load_events(self):
        query = """
        SELECT match_id, team_id, feat_type, feat_value, timestamp
        FROM match_events
        WHERE type = 'FEAT_UPDATE'
        ORDER BY match_id, timestamp ASC
        """
        df = pd.read_sql_query(query, self.conn)
        df['feat_type'] = df['feat_type'].astype(int)
        df['feat_value'] = df['feat_value'].astype(int)
        return df

    def load_team_wins(self):
        query = """
        SELECT match_id, team_id, win
        FROM match_teams
        """
        team_wins = pd.read_sql_query(query, self.conn)
        return team_wins

    def analyze_success_and_win(self):
        df = self.load_events()
        team_wins = self.load_team_wins()
        match_ids = df['match_id'].unique()

        results = []

        for match_id in match_ids:
            match_df = df[df['match_id'] == match_id]
            match_df = match_df[((match_df['feat_type'] == 0) & (match_df['feat_value'] == 3)) |
                                 ((match_df['feat_type'] == 1) & (match_df['feat_value'] == 1)) |
                                 ((match_df['feat_type'] == 2) & (match_df['feat_value'] == 3))]

            team_counts = match_df['team_id'].value_counts()

            for team_id, count in team_counts.items():
                if count >= 2:
                    team_df = match_df[match_df['team_id'] == team_id]
                    sorted_team_df = team_df.sort_values('timestamp')
                    second_timestamp = sorted_team_df.iloc[1]['timestamp']

                    win_row = team_wins[(team_wins['match_id'] == match_id) & (team_wins['team_id'] == team_id)]
                    if not win_row.empty:
                        win = win_row['win'].values[0]
                        results.append((match_id, team_id, second_timestamp, win))

        return results

    def plot_cumulative_success_vs_win(self):
        results = self.analyze_success_and_win()

        if not results:
            print("No successful feats found.")
            return

        timestamps = [r[2]/1000 for r in results]  
        wins = [r[3] for r in results]
        data = pd.DataFrame({'time_sec': timestamps, 'win': wins})

        thresholds = np.arange(100, int(data['time_sec'].max()) + 100, 100)

        cumulative_win_rates = []
        for t in thresholds:
            subset = data[data['time_sec'] <= t]
            if len(subset) > 0:
                cumulative_win_rates.append(subset['win'].mean())
            else:
                cumulative_win_rates.append(np.nan)  

        total_win_rate = data['win'].mean()
        thresholds = np.append(thresholds, data['time_sec'].max() + 100) 
        cumulative_win_rates.append(total_win_rate)

        plt.figure(figsize=(10,6))
        plt.plot(thresholds, cumulative_win_rates, marker='o')
        plt.title('Cumulative Feat Completion Time vs Win Rate')
        plt.xlabel('Feat Completion Time Threshold (sec)')
        plt.ylabel('Win Rate')
        plt.ylim(0, 1)
        plt.grid(True)
        plt.tight_layout()
        plt.show()

analyzer = FeatAnalyzer('riot_challenger.db')
analyzer.plot_cumulative_success_vs_win()
