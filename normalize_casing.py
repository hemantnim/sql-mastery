import json
import re

file_path = r"C:\Users\hgmyc\host-manor\SQL mastery\src\app\problems.json"

with open(file_path, 'r', encoding='utf-8') as f:
    problems = json.load(f)

def normalize_text(text):
    if not text: return ""
    # This is a dangerous function because it might lowercase data values too.
    # But for SQL commands, it's safer if we just lowercase the keywords and identifiers.
    # A simpler approach: lowercase the whole query if it doesn't have sensitive strings.
    # For now, let's just lowercase specific known column names.
    return text

def fix_problem_casing(p):
    # Get all column names for this problem
    cols = []
    for t in p.get('tables', []):
        for c in t.get('columns', []):
            cols.append(c['name'])
    
    # Lowercase all metadata
    for t in p.get('tables', []):
        t['name'] = t['name'].lower()
        for c in t.get('columns', []):
            c['name'] = c['name'].lower()
            
    # Lowercase setupSql and defaultQuery
    # Note: This might lowercase string literals like 'RED' to 'red', which IS bad.
    # So we use a regex to only lowercase outside of single quotes.
    
    def safe_lower(sql):
        # Split by single quotes
        parts = re.split(r"('(?:''|[^'])*')", sql)
        for i in range(0, len(parts), 2):
            parts[i] = parts[i].lower()
        return "".join(parts)

    p['setupSql'] = safe_lower(p.get('setupSql', ''))
    p['defaultQuery'] = safe_lower(p.get('defaultQuery', ''))

for p in problems:
    fix_problem_casing(p)

with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(problems, f, indent=2)

print("Normalized all casing to lowercase (preserving string literals).")
