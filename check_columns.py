import json
import re

file_path = r"C:\Users\hgmyc\host-manor\SQL mastery\src\app\problems.json"

with open(file_path, 'r', encoding='utf-8') as f:
    problems = json.load(f)

def get_cols_from_query(query):
    # Very rough extraction: words that look like columns
    # We look for words after SELECT, JOIN, WHERE, etc.
    # This is hard to do perfectly with regex but let's try to find obvious ones.
    words = re.findall(r'\b([a-zA-Z_]\w*)\b', query)
    # Ignore SQL keywords
    blacklist = {'select', 'from', 'where', 'and', 'or', 'group', 'by', 'having', 'order', 'limit', 'offset', 'as', 'in', 'is', 'null', 'not', 'distinct', 'count', 'max', 'min', 'avg', 'sum', 'join', 'left', 'right', 'on', 'into', 'values', 'create', 'table', 'if', 'exists', 'delete', 'update', 'set', 'case', 'when', 'then', 'else', 'end', 'over', 'partition', 'rank', 'dense_rank', 'row_number'}
    return {w.lower() for w in words if w.lower() not in blacklist}

mismatches = []
for p in problems:
    query_cols = get_cols_from_query(p.get('defaultQuery', ''))
    
    # Get defined columns from tables metadata
    defined_cols = set()
    for t in p.get('tables', []):
        for c in t.get('columns', []):
            defined_cols.add(c['name'].lower())
            
    # Also check setupSql as source of truth
    sql_cols = set()
    # Find words in CREATE TABLE (...)
    match = re.search(r'CREATE TABLE.*?\((.*?)\)', p.get('setupSql', ''), re.IGNORECASE | re.DOTALL)
    if match:
        parts = match.group(1).split(',')
        for part in parts:
            col_name_match = re.search(r'\b([a-zA-Z_]\w*)\b', part.strip())
            if col_name_match:
                sql_cols.add(col_name_match.group(1).lower())

    # Source of truth is defined_cols OR sql_cols
    all_known = defined_cols | sql_cols
    
    # Filter out table names from query_cols
    table_names = {t['name'].lower() for t in p.get('tables', [])}
    actual_query_cols = query_cols - table_names
    
    missing = [c for c in actual_query_cols if c not in all_known]
    # Filter out common aliases and false positives
    missing = [c for c in missing if len(c) > 1 and c not in {'t', 'e', 'p', 'a', 'w', 's', 'l', 'd'}]
    
    if missing:
        mismatches.append((p['id'], missing, list(all_known)))

if mismatches:
    print(f"Found {len(mismatches)} potential column mismatches:")
    for mid, miss, known in mismatches[:20]:
        print(f"ID {mid}: Query uses {miss}, but only {known} are defined.")
else:
    print("No obvious column mismatches found.")
