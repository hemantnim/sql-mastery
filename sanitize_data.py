import json
import re

file_path = r"C:\Users\hgmyc\host-manor\SQL mastery\src\app\problems.json"

with open(file_path, 'r', encoding='utf-8') as f:
    problems = json.load(f)

def is_junk_identifier(name):
    if not name: return True
    # No spaces allowed in clean identifiers
    if ' ' in name: return True
    # No dividers or symbols
    if any(c in name for c in '+-|=<>():.[]{}'): return True
    # Blacklist common junk words
    low = name.lower()
    blacklist = ['description', 'solution', 'table', 'write', 'query', 'mysql', 'column', 'type', 'datatype', 'null', 'string', 'int', 'varchar']
    if low in blacklist: return True
    return False

def sanitize_problem(p):
    clean_tables = []
    for t in p.get('tables', []):
        if is_junk_identifier(t['name']):
            continue
        
        clean_cols = []
        for c in t.get('columns', []):
            if not is_junk_identifier(c['name']):
                clean_cols.append(c)
        
        if clean_cols:
            t['columns'] = clean_cols
            clean_tables.append(t)
    
    p['tables'] = clean_tables
    
    # Always rebuild setupSql if we sanitized
    if clean_tables:
        new_sql = ""
        for t in clean_tables:
            # Use backticks for safety in AlaSQL/MySQL style
            cols_str = ", ".join([f"`{c['name']}` {c['type'].upper()}" for c in t['columns']])
            new_sql += f"CREATE TABLE IF NOT EXISTS `{t['name']}` ({cols_str}); "
        p['setupSql'] = new_sql.strip()
    else:
        p['setupSql'] = ""
        p['tables'] = []

for p in problems:
    # IDs 1 and 2 are our "gold standard" hardcoded ones, don't touch them
    if p['id'] <= 2: continue
    
    # For others, if they have junk, sanitize
    # We define junk as anything with + - | or known junk words in identifiers
    has_junk = False
    for t in p.get('tables', []):
        if is_junk_identifier(t['name']): has_junk = True
        for c in t.get('columns', []):
            if is_junk_identifier(c['name']): has_junk = True
    
    if has_junk or any(c in p.get('setupSql', '') for c in '+-|'):
        sanitize_problem(p)

with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(problems, f, indent=2)

print("Strict Sanitization complete.")
