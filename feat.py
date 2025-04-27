import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

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

    def analyze_mode(self, df, match_id, mode='current'):
        match_df = df[df['match_id'] == match_id]

        if mode == 'current':
            match_df = match_df[((match_df['feat_type'] == 0) & (match_df['feat_value'] == 3)) |
                                 ((match_df['feat_type'] == 1) & (match_df['feat_value'] == 1)) |
                                 ((match_df['feat_type'] == 2) & (match_df['feat_value'] == 3))]
        elif mode == 'previous':
            match_df = match_df[((match_df['feat_type'] == 0) & (match_df['feat_value'] == 1)) |
                                 ((match_df['feat_type'] == 1) & (match_df['feat_value'] == 1)) |
                                 ((match_df['feat_type'] == 2) & (match_df['feat_value'] == 3))]

        team_counts = match_df['team_id'].value_counts()

        for team_id, count in team_counts.items():
            if count >= 2:
                team_df = match_df[match_df['team_id'] == team_id]
                sorted_team_df = team_df.sort_values('timestamp')
                second_timestamp = sorted_team_df.iloc[1]['timestamp']
                return second_timestamp

        return None

    def compare_modes_all(self):
        df = self.load_events()
        match_ids = df['match_id'].unique()

        results = []

        for match_id in match_ids:
            current_time = self.analyze_mode(df, match_id, mode='current')
            previous_time = self.analyze_mode(df, match_id, mode='previous')

            print(f"\nMatch ID: {match_id}")
            print(f"Current System Completion Time: {current_time}")
            print(f"Previous System Completion Time: {previous_time}")

            if current_time is not None and previous_time is not None:
                diff = current_time - previous_time
                print(f"Difference (Current - Previous): {diff} ms")
                results.append((match_id, current_time, previous_time, diff))

        if results:
            current_times = [item[1]/1000 for item in results]  
            previous_times = [item[2]/1000 for item in results]  
            avg_current = sum(current_times) / len(current_times)
            avg_previous = sum(previous_times) / len(previous_times)
            print(f"\nAverage Current System Completion Time: {avg_current:.2f} sec")
            print(f"Average Previous System Completion Time: {avg_previous:.2f} sec")

            plt.figure(figsize=(14,7))
            plt.scatter(range(len(current_times)), current_times, label='Current System (3 kills)', color='blue', alpha=0.6)
            plt.scatter(range(len(previous_times)), previous_times, label='Previous System (1 kill)', color='green', alpha=0.6)

            plt.axhline(y=avg_current, color='blue', linestyle='--', label=f'Current Avg: {avg_current:.1f} sec')
            plt.axhline(y=avg_previous, color='green', linestyle='--', label=f'Previous Avg: {avg_previous:.1f} sec')

            plt.title('Comparison of 2-Feat Completion Times (Current vs Previous System)')
            plt.xlabel('Game Number')
            plt.ylabel('Completion Timestamp (sec)')
            plt.legend()
            plt.grid(True)
            plt.tight_layout()
            plt.show()

# Usage
analyzer = FeatAnalyzer('riot_challenger.db')
analyzer.compare_modes_all()
