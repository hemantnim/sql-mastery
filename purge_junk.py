import json
import re

file_path = r"C:\Users\hgmyc\host-manor\SQL mastery\src\app\problems.json"

with open(file_path, 'r', encoding='utf-8') as f:
    problems = json.load(f)

# 1. Remove 277+
new_problems = [p for p in problems if p['id'] < 277]

# 2. Check remaining for "Whole-Description Tables"
def fix_mangled_description(p):
    desc = p['description']
    # If the whole thing is just a table and contains "Write" or "MySQL" or "Description" inside
    if desc.strip().startswith('<table') and desc.strip().endswith('</table>'):
        # Extract text from cells
        cells = re.findall(r'<td[^>]*>(.*?)</td>', desc, re.DOTALL)
        text = " ".join(cells)
        if any(x in text for x in ['Write', 'MySQL', 'Description', 'Table:']):
             # It was probably mangled. Clean it up.
             text = text.replace('Description', '').replace('# Write your MySQL query statement below', '').strip()
             return f"<p>{text}</p>"
    return desc

for p in new_problems:
    p['description'] = fix_mangled_description(p)

# 3. Final re-indexing and Title cleanup
for i, p in enumerate(new_problems):
    p['id'] = i + 1
    title = p['title']
    # Remove double numbering
    title = re.sub(r'^\d+\.\s*', '', title)
    title = re.sub(r'^\d+\.\s*', '', title)
    # Remove "Link"
    title = re.sub(r'^link\s*', '', title, flags=re.IGNORECASE)
    # capitalize
    title = title.strip().capitalize()
    p['title'] = f"{p['id']}. {title}"

with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(new_problems, f, indent=2)

print(f"Purged junk questions. Total count: {len(new_problems)}")
