import json
import re

file_path = r"C:\Users\hgmyc\host-manor\SQL mastery\src\app\problems.json"

with open(file_path, 'r', encoding='utf-8') as f:
    problems = json.load(f)

def infer_type(val):
    val = val.strip()
    if val.lower() == 'null': return 'INT'
    if re.match(r'^\d+$', val): return 'INT'
    if re.match(r'^\d+\.\d+$', val): return 'DECIMAL(10,2)'
    if re.match(r'^\d{4}-\d{2}-\d{2}$', val): return 'DATE'
    return 'STRING'

def parse_ascii_table(text):
    # Find blocks that look like | col1 | col2 |
    lines = text.split('\n')
    tables = []
    
    # Try to find table name before the block
    table_name_match = re.search(r'Table:\s*(\w+)', text, re.IGNORECASE)
    table_name = table_name_match.group(1) if table_name_match else "DataTable"

    rows = []
    for line in lines:
        if '|' in line:
            parts = [c.strip() for c in line.split('|') if c.strip() != '']
            if parts and not all(c.strip('-').strip('+') == '' for c in parts):
                rows.append(parts)
    
    if not rows: return None
    
    # Heuristic: First row might be header if it has letters and following rows have data
    header = rows[0]
    data = rows[1:] if len(rows) > 1 else []
    
    if not data:
        # Just columns defined?
        cols = [{"name": c, "type": "STRING"} for c in header]
        return {"name": table_name, "columns": cols, "data": []}
    
    # Infer types from first data row
    cols = []
    for i, col_name in enumerate(header):
        type_str = infer_type(data[0][i]) if i < len(data[0]) else "STRING"
        cols.append({"name": col_name, "type": type_str})
        
    return {"name": table_name, "columns": cols, "data": data}

def generate_setup_sql(table_info):
    if not table_info: return ""
    tname = table_info['name']
    cols_def = ", ".join([f"{c['name']} {c['type']}" for c in table_info['columns']])
    sql = f"CREATE TABLE IF NOT EXISTS {tname} ({cols_def}); DELETE FROM {tname}; "
    
    if table_info['data']:
        for row in table_info['data']:
            vals = []
            for v in row:
                if v.lower() == 'null': vals.append("NULL")
                elif re.match(r'^\d+(\.\d+)?$', v): vals.append(v)
                else: vals.append(f"'{v}'")
            sql += f"INSERT INTO {tname} VALUES ({', '.join(vals)}); "
            
    return sql

count = 0
for p in problems:
    if p['tables'] and p['setupSql']: continue
    
    # Clean HTML for parsing
    desc_text = re.sub(r'<[^>]+>', '\n', p['description'])
    
    # Try different parsers
    table_data = parse_ascii_table(desc_text)
    
    if table_data:
        p['tables'] = [{"name": table_data['name'], "columns": [{"name": c['name'], "type": c['type'].lower()} for c in table_data['columns']]}]
        p['setupSql'] = generate_setup_sql(table_data)
        count += 1
    else:
        # Special case for "following schema: a. studentid INT..."
        schema_match = re.findall(r'(\w+)\s+(INT|VARCHAR|DATE|NVARCHAR)', desc_text, re.IGNORECASE)
        if schema_match:
            tname = "Students" if "student" in desc_text.lower() else "DataTable"
            cols = [{"name": m[0], "type": m[1].lower()} for m in schema_match]
            p['tables'] = [{"name": tname, "columns": cols}]
            cols_sql = ", ".join([f"{c['name']} {c['type'].upper()}" for c in cols])
            p['setupSql'] = f"CREATE TABLE IF NOT EXISTS {tname} ({cols_sql});"
            count += 1

with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(problems, f, indent=2)

print(f"Generated schemas for {count} problems.")
