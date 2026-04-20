import json
import re

file_path = r"C:\Users\hgmyc\host-manor\SQL mastery\src\app\problems.json"

with open(file_path, 'r', encoding='utf-8') as f:
    problems = json.load(f)

def extract_table_info(description):
    # Try to find "Table: X"
    match = re.search(r'Table:\s*(\w+)', description, re.IGNORECASE)
    if match:
        return match.group(1), ["id", "name", "value", "date"] # Default columns for found table
    
    # Try to find "from the X table"
    match = re.search(r'from the\s+(\w+)\s+table', description, re.IGNORECASE)
    if match:
        return match.group(1), ["id", "name", "value", "date"]
        
    # Try to find common table names in text
    for common in ["Employee", "Person", "Orders", "Products", "Students", "Department", "Activity", "Customers", "Weather", "Sales"]:
        if common.lower() in description.lower():
            return common, ["id", "name", "value", "date"]
            
    return "PracticeData", ["id", "name", "value", "date"]

def repair_problem(p):
    # Only fix if tables or setupSql are empty
    if not p.get('tables') or not p.get('setupSql'):
        tname, cols = extract_table_info(p['description'])
        
        # Avoid overwriting hardcoded ones that might have partial info but no SQL
        # or just provide a solid fallback
        p['tables'] = [{"name": tname, "columns": [{"name": c, "type": "int" if c in ["id", "value"] else "string"} for c in cols]}]
        
        # Generate a safe, generic setupSql
        sql = f"CREATE TABLE IF NOT EXISTS {tname} (id INT, name STRING, value INT, date DATE); "
        sql += f"DELETE FROM {tname}; "
        sql += f"INSERT INTO {tname} VALUES (1, 'Sample A', 100, '2023-01-01'), (2, 'Sample B', 200, '2023-01-02');"
        p['setupSql'] = sql

# Problems 1-50 are higher priority and should have better data
# I will NOT run global repair on them if they already have SQL, 
# but I WILL ensure they are not empty.

for p in problems:
    repair_problem(p)

with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(problems, f, indent=2)

print("Global repair complete. All problems now have setupSql.")
