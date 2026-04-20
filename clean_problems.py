import json
import re

file_path = r"C:\Users\hgmyc\host-manor\SQL mastery\src\app\problems.json"

with open(file_path, 'r', encoding='utf-8') as f:
    problems = json.load(f)

def clean_title(title, description):
    # If title is just a number or very generic, try to extract from description
    if re.match(r'^\d+\.\s*$', title) or any(x in title.lower() for x in ['link', 'write', 'create', 'find', 'productsbewkoof', 'system defined', 'user defined', 'like', 'mexico', 'credit']):
        # Try to find "Table: X" or "Write a SQL query"
        table_match = re.search(r'Table:\s*(\w+)', description)
        if table_match:
            return f"Query on {table_match.group(1)} Table"
        
        # Try to find first sentence
        desc_clean = re.sub(r'<[^>]+>', '', description).strip()
        first_sentence = desc_clean.split('.')[0]
        if 10 < len(first_sentence) < 60:
            return first_sentence
            
    # Remove leading numbers and Description tags
    new_title = re.sub(r'^\d+\.\s*', '', title)
    new_title = new_title.replace('Description', '').strip()
    # Truncate if too long
    if len(new_title) > 70:
        new_title = new_title[:67] + "..."
    return new_title

cleaned = []
seen = set()

# Problems 1-50 are high quality, keep them as is (but re-index)
for i in range(min(len(problems), 50)):
    p = problems[i]
    # Use a key to avoid duplicates
    key = (p['title'].lower(), p['description'][:100].lower())
    if key not in seen:
        seen.add(key)
        cleaned.append(p)

# Process the rest
for i in range(50, len(problems)):
    p = problems[i]
    
    # Skip if it looks like non-SQL content (Statistics, etc)
    if any(x in p['description'].lower() for x in ['z-test', 't-test', 'annova', 'chi square']):
        continue
        
    # Skip duplicates
    key = (p['title'].lower(), p['description'][:100].lower())
    if key not in seen:
        p['title'] = clean_title(p['title'], p['description'])
        
        # If title is still too generic after clean_title, try more aggressive extraction
        if len(p['title']) < 5:
             p['title'] = "SQL Practice Question"
             
        seen.add(key)
        cleaned.append(p)

# Grouping and Numbering
final_problems = []
table_groups = {}

for i, p in enumerate(cleaned):
    # Re-id
    p['id'] = i + 1
    
    # Extract table name for grouping
    table_match = re.search(r'Table:\s*(\w+)', p['description'])
    if table_match:
        t_name = table_match.group(1)
        if t_name not in table_groups:
            table_groups[t_name] = 0
        table_groups[t_name] += 1
        
        # If we have multiple for same table, add group numbering
        # But only for those we just "cleaned" or renamed
        if "Table" in p['title'] or p['title'] == "SQL Practice Question":
            p['title'] = f"Analysis on {t_name} (Part {table_groups[t_name]})"

    # Re-apply sequential numbering to title
    p['title'] = re.sub(r'^\d+\.\s*', '', p['title'])
    p['title'] = f"{p['id']}. {p['title']}"
    final_problems.append(p)

with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(final_problems, f, indent=2)

print(f"Cleaned problems. Total count: {len(final_problems)}")
