import json
import re
import hashlib

file_path = r"C:\Users\hgmyc\host-manor\SQL mastery\src\app\problems.json"

with open(file_path, 'r', encoding='utf-8') as f:
    problems = json.load(f)

def get_content_hash(text):
    # Normalize text for hashing
    normalized = re.sub(r'\s+', '', text.lower())
    normalized = normalized.replace('<br/>', '').replace('<p>', '').replace('</p>', '')
    return hashlib.md5(normalized.encode('utf-8')).hexdigest()

def clean_description(desc):
    # Remove excessive <br/> and whitespace
    d = desc.replace('<br/>', ' ')
    d = re.sub(r'\s+', ' ', d)
    return d.strip()

def extract_better_title(title, description):
    # Clean description for extraction
    clean_desc = re.sub(r'<[^>]+>', '', description).replace('\n', ' ')
    clean_desc = re.sub(r'\s+', ' ', clean_desc).strip()
    
    # Generic keywords that trigger a rename
    generic = ['write', 'link', 'return', 'create', 'find', 'query', 'sql', 'retrieve', 'select', 'system-defined', 'user -defined']
    
    if len(title) < 10 or any(x == title.lower().strip() for x in generic) or 'link' in title.lower():
        # Try to find "Table: X"
        table_match = re.search(r'Table:\s*(\w+)', clean_desc, re.IGNORECASE)
        if table_match:
            return f"Query on {table_match.group(1)} Table"
            
        # Try to find first meaningful sentence
        sentences = clean_desc.split('.')
        for s in sentences:
            s = s.strip()
            if 5 < len(s) < 80:
                # Avoid just "Write a query"
                if len(s.split()) > 3:
                    return s
                    
        return "SQL Practice Task"
    
    return title

cleaned = []
seen_hashes = set()

# Problems 1-50 are verified
for i in range(min(len(problems), 50)):
    p = problems[i]
    h = get_content_hash(p['description'])
    seen_hashes.add(h)
    cleaned.append(p)

# Process the rest with better deduplication and title cleaning
for i in range(50, len(problems)):
    p = problems[i]
    
    # Skip non-SQL
    if any(x in p['description'].lower() for x in ['z-test', 't-test', 'annova', 'chi square', 'statistics']):
        continue
        
    h = get_content_hash(p['description'])
    if h in seen_hashes:
        continue
    seen_hashes.add(h)
    
    # Clean Title
    raw_title = re.sub(r'^\d+\.\s*', '', p['title'])
    p['title'] = extract_better_title(raw_title, p['description'])
    
    # Clean Description HTML (remove excessive <br/>)
    p['description'] = p['description'].replace('<br/><br/>', '<br/>').replace('<br/>', ' ')
    
    cleaned.append(p)

# Final numbering and table-based grouping
final_list = []
table_counts = {}

for i, p in enumerate(cleaned):
    p['id'] = i + 1
    
    # Re-apply table grouping if title is still generic
    table_match = re.search(r'Table:\s*(\w+)', p['description'], re.IGNORECASE)
    if table_match:
        tname = table_match.group(1)
        table_counts[tname] = table_counts.get(tname, 0) + 1
        if "Table" in p['title'] or "Practice Task" in p['title']:
            p['title'] = f"Data Analysis on {tname} (Part {table_counts[tname]})"

    # Ensure sequential numbering in title field
    title_text = re.sub(r'^\d+\.\s*', '', p['title'])
    p['title'] = f"{p['id']}. {title_text}"
    final_list.append(p)

with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(final_list, f, indent=2)

print(f"Deep Cleaned. Final count: {len(final_list)}")
