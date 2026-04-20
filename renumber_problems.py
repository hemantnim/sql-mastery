import json
import re

file_path = r'C:\Users\hgmyc\SQL mastery\src\app\problems.json'

with open(file_path, 'r', encoding='utf-8') as f:
    problems = json.load(f)

for i, problem in enumerate(problems):
    new_id = i + 1
    # Update internal ID
    problem['id'] = new_id
    
    # Clean up the title: remove any leading "Number. " and re-apply correctly
    title = problem['title']
    # Remove leading numbers like "1. ", "177. ", "11. "
    clean_title = re.sub(r'^\d+\.\s*', '', title)
    problem['title'] = f"{new_id}. {clean_title}"

with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(problems, f, indent=2)

print(f"Renumbered {len(problems)} problems sequentially.")
