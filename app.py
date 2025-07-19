from flask import Flask, render_template
import requests
import json
from tabulate import tabulate
import os


app = Flask(__name__)

def fetch_cricket_scores():
    url = "https://cricbuzz-cricket.p.rapidapi.com/matches/v1/recent"

    headers = {
        "X-RapidAPI-Host": "cricbuzz-cricket.p.rapidapi.com",
        "X-RapidAPI-Key": "a8a33e4f6bmsh126213ef1a968e4p156942jsn3b286f0438f2"  
    }
    response = requests.get(url, headers=headers)
    data = response.json()

    matches_data = []

    for match_type in data.get('typeMatches', []):
     for series in match_type.get('seriesMatches', []):
        matches = series.get('seriesAdWrapper', {}).get('matches', [])

        for match in matches:
            try:
                info = match['matchInfo']
                team1 = info['team1']['teamName']
                team2 = info['team2']['teamName']
                desc = info.get('matchDesc', 'N/A')
                series_name = info.get('seriesName', 'N/A')
                format = info.get('matchFormat', 'N/A')
                status = info.get('status', 'N/A')

                # Scores
                score = match.get('matchScore', {})
                team1_score = score.get('team1Score', {}).get('inngs1', {})
                team2_score = score.get('team2Score', {}).get('inngs1', {})

                # Table
                table = [
                    ["Match", f"{desc}: {team1} vs {team2}"],
                    ["Series", series_name],
                    ["Format", format],
                    ["Result", status],
                    [team1, f"{team1_score.get('runs', '-')}/{team1_score.get('wickets', '-')} in {team1_score.get('overs', '-')} overs"],
                    [team2, f"{team2_score.get('runs', '-')}/{team2_score.get('wickets', '-')} in {team2_score.get('overs', '-')} overs"]
                ]
            except Exception as e:
                print("Error reading match data:", e)
        matches_data.append(tabulate(table, tablefmt="html"))

    return matches_data

def fetch_upcoming_matches():
    url = "https://cricbuzz-cricket.p.rapidapi.com/schedule/v1/international"

    headers = {
        "X-RapidAPI-Host": "cricbuzz-cricket.p.rapidapi.com",
        "X-RapidAPI-Key": "a8a33e4f6bmsh126213ef1a968e4p156942jsn3b286f0438f2"  # Replace with your RapidAPI key
    }
    #
    response = requests.get(url, headers=headers)
    upcoming_matches = []

    if response.status_code == 200:
        try:
            data = response.json()
            match_schedules = data.get('matchScheduleMap', [])

            for schedule in match_schedules:
                if 'scheduleAdWrapper' in schedule:
                    date = schedule['scheduleAdWrapper']['date']
                    matches = schedule['scheduleAdWrapper']['matchScheduleList']

                    for match_info in matches:
                        for match in match_info['matchInfo']:
                            description = match['matchDesc']
                            team1 = match['team1']['teamName']
                            team2 = match['team2']['teamName']
                            match_data = {
                                'Date': date,
                                'Description': description,
                                'Teams': f"{team1} vs {team2}"
                            }
                            upcoming_matches.append(match_data)
                else:
                    print("No match schedule found for this entry.")

        except json.JSONDecodeError as e:
            print("Error parsing JSON:", e)
        except KeyError as e:
            print("Key error:", e)
    else:
        print("Failed to fetch cricket scores. Status code:", response.status_code)

    return upcoming_matches


@app.route('/')
def index():
    cricket_scores = fetch_cricket_scores()
    upcoming_matches = fetch_upcoming_matches()
    return render_template('index.html', cricket_scores=cricket_scores, upcoming_matches=upcoming_matches)

if __name__ == '__main__':
    app.run(port=int(os.environ.get("PORT", 8080)),host='0.0.0.0',debug=True)