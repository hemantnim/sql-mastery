import json
import re

file_path = r"C:\Users\hgmyc\host-manor\SQL mastery\src\app\problems.json"

with open(file_path, 'r', encoding='utf-8') as f:
    problems = json.load(f)

def polish(p):
    # Description polish
    desc = p['description']
    desc = re.sub(r'^<p>\s*LINK\s*', '<p>', desc, flags=re.IGNORECASE)
    desc = re.sub(r'^<p>\s*\.\s*', '<p>', desc)
    p['description'] = desc
    
    # Title polish
    title = p['title']
    title_text = re.sub(r'^\d+\.\s*', '', title)
    
    # If title is a fragment like ", the (lat...)"
    if title_text.startswith(',') or title_text.startswith('.') or len(title_text) < 5:
        # Try to extract from description
        clean_desc = re.sub(r'<[^>]+>', '', desc).strip()
        # Find first sentence or first 50 chars
        match = re.search(r'Write a (?:query|solution) to (.*?)\.', clean_desc, re.IGNORECASE)
        if match:
            title_text = match.group(1)
        else:
            title_text = clean_desc[:60] + "..."
            
    title_text = title_text.strip().capitalize()
    if title_text.endswith('.'): title_text = title_text[:-1]
    
    p['title'] = f"{p['id']}. {title_text}"

for p in problems:
    polish(p)

with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(problems, f, indent=2)

print("Final Polish Complete.")
