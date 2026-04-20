import os
import re
import json
import PyPDF2

pdf_dir = r"C:\Users\hgmyc\host-manor\SQL mastery\SQL Questions"
output_path = r"C:\Users\hgmyc\host-manor\SQL mastery\src\app\problems.json"

with open(output_path, 'r', encoding='utf-8') as f:
    problems = json.load(f)

max_id = max((p['id'] for p in problems), default=0)
current_id = max_id + 1

# Patterns to identify questions in raw text
patterns = [
    r'\n\s*(?:Q|Question)\s*\d*[:.)]\s*(.+?)(?=\n\s*(?:Q|Question)\s*\d*[:.)]|\Z)',
    r'\n\s*\d+\.\s+([A-Z].+?)(?=\n\s*\d+\.\s+[A-Z]|\Z)' # Numbered lists starting with capital letter
]

def analyze_difficulty(text):
    text_lower = text.lower()
    hard_keywords = ['window function', 'cte', 'recursive', 'rank()', 'dense_rank', 'partition by']
    medium_keywords = ['join', 'group by', 'having', 'subquery', 'union', 'intersect', 'exists']
    
    if any(kw in text_lower for kw in hard_keywords):
        return 'Hard'
    if any(kw in text_lower for kw in medium_keywords):
        return 'Medium'
    return 'Easy'

new_problems = []

for filename in os.listdir(pdf_dir):
    if not filename.lower().endswith('.pdf'):
        continue
        
    pdf_path = os.path.join(pdf_dir, filename)
    print(f"Processing {filename}...")
    try:
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            full_text = ""
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    full_text += text + "\n"
                    
        # Basic cleanup
        full_text = re.sub(r' +', ' ', full_text)
        
        # Try to extract questions
        questions = []
        for pattern in patterns:
            matches = re.finditer(pattern, full_text, re.IGNORECASE | re.DOTALL)
            for m in matches:
                q_text = m.group(1).strip()
                # Filter out junk
                if 20 < len(q_text) < 3000 and not q_text.lower().startswith('table:'):
                    questions.append(q_text)
            
            if questions:
                break # Stop if we found questions with a specific pattern
                
        for q in questions:
            lines = q.split('\n', 1)
            title_candidate = lines[0].strip()
            # If title is too long, truncate it
            if len(title_candidate) > 80:
                title_candidate = title_candidate[:77] + "..."
                
            desc = q.replace('\n', '<br/>')
            
            title = f"{current_id}. {title_candidate}"
            difficulty = analyze_difficulty(q)
            
            new_problems.append({
                "id": current_id,
                "title": title,
                "difficulty": difficulty,
                "category": "Database",
                "description": f"<p>{desc}</p>",
                "tables": [],
                "defaultQuery": "-- Write your query here\n",
                "setupSql": ""
            })
            current_id += 1
            
    except Exception as e:
        print(f"Failed to process {filename}: {e}")

print(f"Extracted {len(new_problems)} new problems.")

problems.extend(new_problems)

with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(problems, f, indent=2)

print(f"Total problems now: {len(problems)}")
