# lol-match-analysis

---

## 📚 Project Overview

**LoL Match Insights** is a data-driven project designed to collect, store, and analyze match data from Riot Games' official API.  
This project systematically **stores match data in a local SQLite database** for efficient querying and long-term analysis.  
Beyond simple win/loss outcomes, it aims to extract deep insights into player behaviors, objective control, and match dynamics.

Key analysis areas include:
- Match metadata analysis
- Time-based event tracking (objectives, pings, kills)
- Champion performance analysis
- Summoner playstyle analysis
- Data storage and management with SQLite

---

## Key Features

- **Match Data Collection**: Fetch metadata and timeline data using Riot's Match-V5 API.
- **Champion Analytics**: Analyze champion stats such as win rate, damage output, and KDA.
- **Event Timeline Parsing**: Process detailed event logs (dragons, barons, turrets, pings).
- **Feature Engineering**: Generate features to model match flow and player impact.
- **Database Management**: Efficiently manage large-scale match data for repeated analyses.
- **Visualization Ready**: Designed for integration with visualization tools for advanced analysis.

---

## Project Structure

| File          | Description |
|:--------------|:------------|
| `main.py`     | Main pipeline controller |
| `champion.py` | Champion-related statistics and processing |
| `elitemon.py` | Elite monster (dragon, baron) event handling |
| `feat.py`     | Basic feature engineering |
| `feat2.py`    | Extended feature engineering |
| `match.py`    | Match metadata collection |
| `matchtime.py`| Timeline event parsing |
| `ping.py`     | Ping usage pattern analysis |

---

## Installation & Setup

### Prerequisites
- Python 3.10 or higher
- A Riot Games Developer API Key
