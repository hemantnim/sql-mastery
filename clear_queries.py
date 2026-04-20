import json

file_path = r'C:\Users\hgmyc\SQL mastery\src\app\problems.json'

with open(file_path, 'r', encoding='utf-8') as f:
    problems = json.load(f)

for problem in problems:
    problem['defaultQuery'] = '-- write your query here\n'

with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(problems, f, indent=2)

print(f"Successfully cleared defaultQuery in {len(problems)} problems.")
