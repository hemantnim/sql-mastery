import json
import re
import hashlib

file_path = r"C:\Users\hgmyc\host-manor\SQL mastery\src\app\problems.json"

with open(file_path, 'r', encoding='utf-8') as f:
    problems = json.load(f)

def add_spaces(text):
    # Fix "Writeaquery" -> "Write a query"
    # Basic heuristic: add space before capital letters if preceded by lowercase
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
    # Common SQL keywords squashed
    text = re.sub(r'(Write|Query|Retrieve|Find|Update|Delete|Create|From|Table|Where|Select|And|Or)([a-z])', r'\1 \2', text)
    return text

def is_weird(title):
    t = title.lower().strip()
    if len(t) < 8: return True
    if ' ' not in t and len(t) > 10: return True # Squashed
    if t.endswith(' or b') or t.endswith(' and') or t.endswith(' i'): return True # Fragments
    if any(x in t for x in ['data task', 'practice task', 'sql task', 'query on table', 'select *', 'select column']): return True
    if re.search(r'[^a-zA-Z0-9\s.\-\(\)]', t): return True # Too many symbols
    return False

def extract_professional_title(description):
    # Clean description
    clean = re.sub(r'<[^>]+>', ' ', description).replace('\n', ' ')
    clean = re.sub(r'\s+', ' ', clean).strip()
    
    # Try to find "Question X : LINK [Actual Title]"
    link_match = re.search(r'Question\s*\d+\s*:\s*LINK\s+([^.]+)', clean, re.IGNORECASE)
    if link_match:
        return link_match.group(1).strip()

    # Look for instructions
    patterns = [
        r'Write\s+a\s+(?:SQL\s+)?query\s+to\s+([^.]+)',
        r'Query\s+the\s+([^.]+)',
        r'Find\s+the\s+([^.]+)',
        r'Retrieve\s+([^.]+)',
        r'Report\s+([^.]+)',
        r'Calculate\s+([^.]+)'
    ]
    
    for p in patterns:
        match = re.search(p, clean, re.IGNORECASE)
        if match:
            extracted = match.group(1).strip()
            # Clean up extraction
            extracted = re.sub(r'\s+in\s+any\s+order.*$', '', extracted, flags=re.IGNORECASE)
            extracted = re.sub(r'\s+sorted\s+by.*$', '', extracted, flags=re.IGNORECASE)
            if 5 < len(extracted) < 60:
                return extracted.capitalize()
    
    # Fallback to first meaningful sentence
    sentences = [s.strip() for s in clean.split('.') if len(s.strip()) > 10]
    for s in sentences:
        if len(s) < 70 and not s.lower().startswith('write a query'):
            return s
            
    return "SQL Analysis Task"

cleaned = []
seen_hashes = set()

# Verification loop for 1-50 (they are mostly good, but check for weirdness)
for i, p in enumerate(problems):
    # Deduplicate first
    desc_norm = re.sub(r'\s+', '', p['description'].lower())
    h = hashlib.md5(desc_norm.encode('utf-8')).hexdigest()
    if h in seen_hashes:
        continue
    seen_hashes.add(h)

    # Strip existing ID from title
    raw_title = re.sub(r'^\d+\.\s*', '', p['title']).strip()
    raw_title = re.sub(r'^\d+\.\s*', '', raw_title).strip() # Twice if needed
    
    # Check if we should keep it or rename it
    if i >= 50 and is_weird(raw_title):
        new_title = extract_professional_title(p['description'])
    else:
        new_title = add_spaces(raw_title)
        
    # Final polish on title
    new_title = new_title.strip().capitalize()
    if new_title.endswith('.'): new_title = new_title[:-1]
    # Truncate and clean
    if len(new_title) > 80: new_title = new_title[:77] + "..."
    
    p['title'] = new_title
    
    # Fix description formatting a bit more
    p['description'] = p['description'].replace(' .', '.').replace(' ,', ',')
    
    cleaned.append(p)

# Table grouping for those that still ended up generic
final_list = []
table_counts = {}
for i, p in enumerate(cleaned):
    p['id'] = i + 1
    
    # Grouping logic
    title_text = p['title']
    if "Task" in title_text or len(title_text) < 10:
        table_match = re.search(r'Table:\s*(\w+)', p['description'], re.IGNORECASE)
        if table_match:
            tname = table_match.group(1).capitalize()
            table_counts[tname] = table_counts.get(tname, 0) + 1
            title_text = f"Data Analysis on {tname} (Part {table_counts[tname]})"
    
    p['title'] = f"{p['id']}. {title_text}"
    final_list.append(p)

with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(final_list, f, indent=2)

print(f"Professional Cleaning Complete. Final count: {len(final_list)}")
