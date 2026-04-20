import json
import re

file_path = r"C:\Users\hgmyc\host-manor\SQL mastery\src\app\problems.json"

with open(file_path, 'r', encoding='utf-8') as f:
    problems = json.load(f)

def clean_sql(sql):
    if not sql: return ""
    # Remove lines that are purely table dividers like +-------+
    sql = re.sub(r'[\+\-]{3,}', '', sql)
    
    # If it's the mangled DataTable version, let's try to prune it
    if 'DataTable' in sql and '(' in sql:
        header_part = sql[sql.find('(')+1 : sql.find(')')]
        cols = header_part.split(',')
        clean_cols = []
        for c in cols:
            c = c.strip().split(' ')[0].strip()
            # Must be a valid identifier
            if re.match(r'^[a-zA-Z_]\w*$', c):
                clean_cols.append(f"{c} STRING")
        
        if not clean_cols:
            return "" # Too mangled to fix here
            
        tname = "DataTable"
        new_sql = f"CREATE TABLE IF NOT EXISTS {tname} ({', '.join(clean_cols)});"
        return new_sql
    
    return sql

for p in problems:
    # 1. Standardize SQL (ensure semicolons, remove comments that might break things)
    sql = p.get('setupSql', '')
    if sql:
        # Replace non-standard STRING with VARCHAR if needed, but AlaSQL likes STRING
        # Ensure each statement ends with semicolon
        statements = [s.strip() for s in sql.split(';') if s.strip()]
        p['setupSql'] = "; ".join(statements) + ";"

    # 2. Fix the specific DataTable mangling for 51-276
    if p['id'] > 50 and 'DataTable' in p.get('setupSql', ''):
        p['setupSql'] = clean_sql(p['setupSql'])
        # If we cleaned the SQL, we should also clean the tables metadata
        if not p['setupSql']:
            p['tables'] = []

with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(problems, f, indent=2)

print("Setup SQL cleaned.")
