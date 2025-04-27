import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

class EpicMonsterAnalyzer:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)

    def load_elite_monster_kills(self):
        query = """
        SELECT match_id, team_id, monster_type, monster_sub_type, timestamp
        FROM match_events
        WHERE type = 'ELITE_MONSTER_KILL'
        ORDER BY match_id, timestamp ASC
        """
        df = pd.read_sql_query(query, self.conn)
        return df

    def load_team_wins(self):
        query = """
        SELECT match_id, team_id, win
        FROM match_teams
        """
        df = pd.read_sql_query(query, self.conn)
        return df

    def add_labels_ratio(self, ax, wins, total_counts):
        """ bar plot 위에 승리/전체 n/m 형태 표시 """
        for p, win, total in zip(ax.patches, wins, total_counts):
            height = p.get_height()
            label = f"{win}/{total}"
            ax.text(p.get_x() + p.get_width() / 2., height + 0.02, label, ha="center", fontsize=9)

    def analyze_horde_kills_vs_winrate(self):
        kills_df = self.load_elite_monster_kills()
        wins_df = self.load_team_wins()

        horde_df = kills_df[kills_df['monster_type'] == 'HORDE']
        horde_counts = horde_df.groupby(['match_id', 'team_id']).size().reset_index(name='horde_kills')

        merged = pd.merge(horde_counts, wins_df, on=['match_id', 'team_id'])

        total_counts = merged.groupby('horde_kills')['win'].count()
        win_counts = merged.groupby('horde_kills')['win'].sum()
        winrates = (win_counts / total_counts) * 100

        total_counts = total_counts.sort_index()
        win_counts = win_counts.sort_index()
        winrates = winrates.sort_index()

        plt.figure(figsize=(10,6))
        ax = winrates.plot(kind='bar', color='purple')
        self.add_labels_ratio(ax, win_counts, total_counts)
        plt.title('Number of Horde (Void Grub) Kills vs Win Rate')
        plt.xlabel('Number of Horde Kills')
        plt.ylabel('Win Rate (%)')
        plt.ylim(0, 100)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.show()

    def analyze_dragon_kills_vs_winrate(self):
        kills_df = self.load_elite_monster_kills()
        wins_df = self.load_team_wins()

        dragon_df = kills_df[kills_df['monster_type'] == 'DRAGON']
        dragon_counts = dragon_df.groupby(['match_id', 'team_id']).size().reset_index(name='dragon_kills')

        merged = pd.merge(dragon_counts, wins_df, on=['match_id', 'team_id'])

        total_counts = merged.groupby('dragon_kills')['win'].count()
        win_counts = merged.groupby('dragon_kills')['win'].sum()
        winrates = (win_counts / total_counts) * 100

        total_counts = total_counts.sort_index()
        win_counts = win_counts.sort_index()
        winrates = winrates.sort_index()

        plt.figure(figsize=(10,6))
        ax = winrates.plot(kind='bar', color='skyblue')
        self.add_labels_ratio(ax, win_counts, total_counts)
        plt.title('Number of Dragon Kills vs Win Rate')
        plt.xlabel('Number of Dragon Kills')
        plt.ylabel('Win Rate (%)')
        plt.ylim(0, 100)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.show()

    def analyze_dragon_type_vs_winrate(self):
        kills_df = self.load_elite_monster_kills()
        wins_df = self.load_team_wins()

        dragon_df = kills_df[kills_df['monster_type'] == 'DRAGON']
        dragon_types = dragon_df[['match_id', 'team_id', 'monster_sub_type']]

        merged = pd.merge(dragon_types, wins_df, on=['match_id', 'team_id'])

        total_counts = merged.groupby('monster_sub_type')['win'].count()
        win_counts = merged.groupby('monster_sub_type')['win'].sum()
        winrates = (win_counts / total_counts) * 100

        winrates = winrates.sort_values()
        total_counts = total_counts.reindex(winrates.index)
        win_counts = win_counts.reindex(winrates.index)

        plt.figure(figsize=(10,6))
        ax = winrates.plot(kind='bar', color='orange')
        self.add_labels_ratio(ax, win_counts, total_counts)
        plt.title('Dragon Type vs Win Rate')
        plt.xlabel('Dragon Type')
        plt.ylabel('Win Rate (%)')
        plt.ylim(0, 100)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.show()

    def analyze_objective_kills_vs_winrate(self):
        kills_df = self.load_elite_monster_kills()
        wins_df = self.load_team_wins()

        target_monsters = ['BARON_NASHOR', 'RIFTHERALD', 'ATAKHAN']
        objective_df = kills_df[kills_df['monster_type'].isin(target_monsters)]

        objective_flags = objective_df.drop_duplicates(subset=['match_id', 'team_id', 'monster_type'])
        objective_flags['kill_flag'] = 1

        pivot = objective_flags.pivot_table(index=['match_id', 'team_id'],
                                            columns='monster_type',
                                            values='kill_flag',
                                            fill_value=0).reset_index()

        merged = pd.merge(pivot, wins_df, on=['match_id', 'team_id'])

        results = []

        for monster in target_monsters:
            if monster in merged.columns:
                temp = merged[merged[monster] == 1]
                total = temp.shape[0]
                win = temp['win'].sum()
                winrate = (win / total) * 100 if total > 0 else 0
                results.append((monster, winrate, win, total))

        result_df = pd.DataFrame(results, columns=['Monster', 'Win Rate', 'Win Count', 'Total Count'])
        result_df = result_df.set_index('Monster')

        plt.figure(figsize=(10,6))
        ax = plt.bar(result_df.index, result_df['Win Rate'], color='lightgreen')

        for rect, (win, total) in zip(ax, zip(result_df['Win Count'], result_df['Total Count'])):
            height = rect.get_height()
            plt.text(rect.get_x() + rect.get_width()/2.0, height + 1, f'{int(win)}/{int(total)}', ha='center', va='bottom', fontsize=9)

        plt.title('Objective Kills vs Win Rate')
        plt.xlabel('Objective (Baron, Rift Herald, Atakan)')
        plt.ylabel('Win Rate (%)')
        plt.ylim(0, 100)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    analyzer = EpicMonsterAnalyzer('riot_challenger.db')

    analyzer.analyze_horde_kills_vs_winrate()
    analyzer.analyze_dragon_kills_vs_winrate()
    analyzer.analyze_dragon_type_vs_winrate()
    analyzer.analyze_objective_kills_vs_winrate()
