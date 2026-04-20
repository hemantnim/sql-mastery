import json
import re

file_path = r"C:\Users\hgmyc\host-manor\SQL mastery\src\app\problems.json"

with open(file_path, 'r', encoding='utf-8') as f:
    problems = json.load(f)

mismatches = []
for p in problems:
    if p['id'] > 276: continue
    tables = [t['name'].lower() for t in p.get('tables', [])]
    sql = p.get('setupSql', '').lower()
    
    if tables and not sql:
        mismatches.append(f"ID {p['id']}: No setupSql for tables {tables}")
    elif tables:
        missing = [t for t in tables if t not in sql]
        if missing:
            mismatches.append(f"ID {p['id']}: Tables {missing} defined but not found in setupSql")

if mismatches:
    print(f"Found {len(mismatches)} potential issues:")
    for m in mismatches[:20]:
        print(m)
else:
    print("No obvious table/SQL mismatches found.")
