import json

output_path = r"C:\Users\hgmyc\host-manor\SQL mastery\src\app\problems.json"

with open(output_path, 'r', encoding='utf-8') as f:
    problems = json.load(f)

for i, p in enumerate(problems):
    # Correct ID to be sequential 1-based
    new_id = i + 1
    p['id'] = new_id
    
    # Strip existing number from title if it exists like "175. Combine Two Tables"
    import re
    title_text = re.sub(r'^\d+\.\s*', '', p['title'])
    p['title'] = f"{new_id}. {title_text}"
    
    # Ensure category is set
    if 'category' not in p or not p['category']:
        p['category'] = "Database"

# Review and refine difficulty levels for 11-50 based on standard Leetcode difficulty
# We'll do a quick pass for the ones we fixed
diff_map = {
    11: "Easy", 12: "Easy", 13: "Medium", 14: "Medium", 15: "Easy",
    16: "Easy", 17: "Easy", 18: "Easy", 19: "Easy", 20: "Easy",
    21: "Easy", 22: "Easy", 23: "Medium", 24: "Easy", 25: "Medium",
    26: "Easy", 27: "Easy", 28: "Easy", 29: "Medium", 30: "Easy",
    31: "Medium", 32: "Easy", 33: "Easy", 34: "Medium", 35: "Easy",
    36: "Easy", 37: "Medium", 38: "Easy", 39: "Easy", 40: "Easy",
    41: "Medium", 42: "Easy", 43: "Medium", 44: "Easy", 45: "Easy",
    46: "Easy", 47: "Medium", 48: "Easy", 49: "Medium", 50: "Easy"
}

for p in problems:
    if p['id'] in diff_map:
        p['difficulty'] = diff_map[p['id']]

with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(problems, f, indent=2)

print(f"Corrected numbering and difficulty for {len(problems)} problems.")
