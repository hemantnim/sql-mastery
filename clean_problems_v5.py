import json
import re
import hashlib

file_path = r"C:\Users\hgmyc\host-manor\SQL mastery\src\app\problems.json"

with open(file_path, 'r', encoding='utf-8') as f:
    problems = json.load(f)

def final_polish(title, description):
    # Forced capitalization for acronyms
    title = re.sub(r'\bsql\b', 'SQL', title, flags=re.IGNORECASE)
    title = re.sub(r'\bid\b', 'ID', title, flags=re.IGNORECASE)
    title = re.sub(r'\bgdp\b', 'GDP', title, flags=re.IGNORECASE)
    
    # Remove trailing fragments
    title = re.sub(r'\s+(?:a|ii|i|or|and|b|with|from|to|for|the)$', '', title, flags=re.IGNORECASE)
    title = re.sub(r'[:\-]$', '', title).strip()
    
    # Professionalize generic placeholders
    if "analysis task" in title.lower() or len(title) < 10:
        # Try table lookup one last time
        table_match = re.search(r'(?:Table:\s*|from the\s+)(\w+)', description, re.IGNORECASE)
        if table_match:
            t = table_match.group(1).capitalize()
            if t != 'The': return f"Data Retrieval from {t} Table"
        return "Advanced SQL Query Task"
    
    return title

cleaned = []
seen_hashes = set()

for i, p in enumerate(problems):
    desc_norm = re.sub(r'\s+', '', p['description'].lower())
    h = hashlib.md5(desc_norm.encode('utf-8')).hexdigest()
    if h in seen_hashes: continue
    seen_hashes.add(h)

    # Current raw title (no number)
    raw = re.sub(r'^\d+\.\s*', '', p['title']).strip()
    
    polished = final_polish(raw, p['description'])
    polished = polished.strip().capitalize()
    
    # Capitalize acronyms again after capitalization of whole string
    polished = re.sub(r'\bSql\b', 'SQL', polished)
    polished = re.sub(r'\bId\b', 'ID', polished)
    
    p['title'] = polished
    cleaned.append(p)

# Final sequential numbering
for i, p in enumerate(cleaned):
    p['id'] = i + 1
    # Strip any number and re-apply
    text = re.sub(r'^\d+\.\s*', '', p['title'])
    p['title'] = f"{p['id']}. {text}"

with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(cleaned, f, indent=2)

print(f"Final professional polish complete. Total unique questions: {len(cleaned)}")
