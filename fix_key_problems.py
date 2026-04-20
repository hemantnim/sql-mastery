import json

file_path = r"C:\Users\hgmyc\host-manor\SQL mastery\src\app\problems.json"

with open(file_path, 'r', encoding='utf-8') as f:
    problems = json.load(f)

# Hardcoded fixes for some common ones that were lost
fixes = {
    44: {
        "tables": [
            { "name": "Activity", "columns": [ {"name": "user_id", "type": "int"}, {"name": "session_id", "type": "int"}, {"name": "activity_date", "type": "date"}, {"name": "activity_type", "type": "string"} ] }
        ],
        "setupSql": "CREATE TABLE IF NOT EXISTS Activity (user_id INT, session_id INT, activity_date DATE, activity_type STRING); DELETE FROM Activity; INSERT INTO Activity VALUES (1, 1, '2019-07-20', 'open_session'), (2, 4, '2019-07-20', 'open_session'), (2, 4, '2019-07-21', 'send_message'), (3, 2, '2019-07-21', 'open_session');"
    },
    11: {
        "tables": [ { "name": "Activity", "columns": [ {"name": "player_id", "type": "int"}, {"name": "device_id", "type": "int"}, {"name": "event_date", "type": "date"}, {"name": "games_played", "type": "int"} ] } ],
        "setupSql": "CREATE TABLE IF NOT EXISTS Activity (player_id INT, device_id INT, event_date DATE, games_played INT); DELETE FROM Activity; INSERT INTO Activity VALUES (1, 2, '2016-03-01', 5), (1, 2, '2016-05-02', 6), (2, 3, '2017-06-25', 1);"
    }
}

for p in problems:
    if p['id'] in fixes:
        p.update(fixes[p['id']])

with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(problems, f, indent=2)

print("Restored key problems.")
