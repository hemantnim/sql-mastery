import json
import re
import hashlib

file_path = r"C:\Users\hgmyc\host-manor\SQL mastery\src\app\problems.json"

with open(file_path, 'r', encoding='utf-8') as f:
    problems = json.load(f)

def get_content_hash(text):
    normalized = re.sub(r'\s+', '', text.lower())
    normalized = normalized.replace('<br/>', '').replace('<p>', '').replace('</p>', '')
    return hashlib.md5(normalized.encode('utf-8')).hexdigest()

def extract_better_title(title, description):
    # Clean description for extraction
    clean_desc = re.sub(r'<[^>]+>', '', description).replace('\n', ' ')
    clean_desc = re.sub(r'\s+', ' ', clean_desc).strip()
    
    # Generic keywords
    generic_words = ['write', 'link', 'return', 'create', 'find', 'query', 'sql', 'retrieve', 'select', 
                     'system-defined', 'user -defined', 'practice', 'task', 'question', 'arithmetic', 'comparison']
    
    clean_title = re.sub(r'^\d+\.\s*', '', title).strip()
    
    if len(clean_title) < 10 or any(clean_title.lower() == x for x in generic_words) or 'link' in clean_title.lower() or 'practice' in clean_title.lower():
        # Try to find "Table: X" or "from the X table"
        table_match = re.search(r'(?:Table:\s*|from the\s+)(\w+)(?:\s+table)?', clean_desc, re.IGNORECASE)
        if table_match:
             tname = table_match.group(1)
             if tname.lower() != 'the':
                return f"Query on {tname.capitalize()} Table"
            
        # Try to find first meaningful sentence but skip "Write a query..."
        sentences = clean_desc.split('.')
        for s in sentences:
            s = s.strip()
            if 10 < len(s) < 80:
                s_lower = s.lower()
                if not s_lower.startswith('write a query') and not s_lower.startswith('return the result'):
                    return s
                else:
                    # If it starts with "Write a query to...", take the rest
                    shortened = re.sub(r'^write a query to\s*', '', s, flags=re.IGNORECASE)
                    shortened = re.sub(r'^retrieve\s*', '', shortened, flags=re.IGNORECASE)
                    if len(shortened) > 5:
                        return shortened.capitalize()
                    
        return "SQL Data Task"
    
    return clean_title

cleaned = []
seen_hashes = set()

# Problems 1-50 are verified
for i in range(min(len(problems), 50)):
    p = problems[i]
    h = get_content_hash(p['description'])
    seen_hashes.add(h)
    # Ensure title is not double-numbered
    p['title'] = re.sub(r'^\d+\.\s*', '', p['title'])
    cleaned.append(p)

for i in range(50, len(problems)):
    p = problems[i]
    if any(x in p['description'].lower() for x in ['z-test', 't-test', 'annova', 'chi square', 'statistics']):
        continue
    h = get_content_hash(p['description'])
    if h in seen_hashes:
        continue
    seen_hashes.add(h)
    
    p['title'] = extract_better_title(p['title'], p['description'])
    # Remove HTML junk in description
    p['description'] = p['description'].replace('<br/>', ' ').replace('<br>', ' ')
    p['description'] = re.sub(r'\s+', ' ', p['description']).strip()
    
    cleaned.append(p)

# Final numbering and grouping
final_list = []
table_counts = {}

for i, p in enumerate(cleaned):
    p['id'] = i + 1
    # Strip any existing numbers
    clean_title_text = re.sub(r'^\d+\.\s*', '', p['title']).strip()
    
    # Check for table name for grouping
    table_match = re.search(r'(?:Table:\s*|from the\s+)(\w+)(?:\s+table)?', p['description'], re.IGNORECASE)
    if table_match:
        tname = table_match.group(1).capitalize()
        if tname != 'The':
            table_counts[tname] = table_counts.get(tname, 0) + 1
            if "Data Task" in clean_title_text or len(clean_title_text) < 10:
                clean_title_text = f"Analysis on {tname} (Part {table_counts[tname]})"

    p['title'] = f"{p['id']}. {clean_title_text}"
    final_list.append(p)

with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(final_list, f, indent=2)

print(f"Final cleanup complete. Total count: {len(final_list)}")
