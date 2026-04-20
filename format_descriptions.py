import json
import re

file_path = r"C:\Users\hgmyc\host-manor\SQL mastery\src\app\problems.json"

with open(file_path, 'r', encoding='utf-8') as f:
    problems = json.load(f)

def ascii_to_html_table(text):
    lines = text.split('\n')
    table_html = '<table style="border-collapse: collapse; width: 100%; margin: 10px 0; font-family: monospace; font-size: 14px;">'
    has_table = False
    in_table = False
    
    formatted_lines = []
    current_table = []
    
    for line in lines:
        if '|' in line and not all(c in ' +-|' for c in line.strip()):
            in_table = True
            has_table = True
            cells = [c.strip() for c in line.split('|') if c.strip() != '' or line.count('|') > 1]
            # Remove empty strings at start/end if they exist
            if line.strip().startswith('|'): cells = cells # handled by split logic
            
            row_html = '<tr>'
            for cell in cells:
                row_html += f'<td style="border: 1px solid #ddd; padding: 8px;">{cell}</td>'
            row_html += '</tr>'
            current_table.append(row_html)
        else:
            if in_table:
                formatted_lines.append(table_html + "".join(current_table) + '</table>')
                current_table = []
                in_table = False
            
            # Skip separator lines
            if re.match(r'^[+\-| ]+$', line.strip()) and len(line.strip()) > 3:
                continue
            
            if line.strip():
                formatted_lines.append(line.strip())
                
    if in_table:
        formatted_lines.append(table_html + "".join(current_table) + '</table>')
        
    return "\n".join(formatted_lines) if has_table else text

def clean_desc(p):
    desc = p['description']
    title_text = re.sub(r'^\d+\.\s*', '', p['title'])
    
    # Remove leading title repeat
    desc = re.sub(f'^<p>{re.escape(title_text)}\s*Description', '<p>', desc, flags=re.IGNORECASE)
    desc = re.sub(f'^<p>{re.escape(title_text)}', '<p>', desc, flags=re.IGNORECASE)
    
    # Extract inner text from <p> to process
    inner = re.sub(r'^<p>(.*?)</p>$', r'\1', desc, flags=re.DOTALL)
    
    # Convert <br/> to newlines for processing
    inner = inner.replace('<br/>', '\n').replace('<br>', '\n')
    
    # Process ASCII tables
    inner = ascii_to_html_table(inner)
    
    # Convert back to HTML paragraphs
    # Split by double newlines or significant gaps
    parts = re.split(r'\n{2,}', inner)
    final_html = ""
    for part in parts:
        if part.strip():
            if part.startswith('<table'):
                final_html += part
            else:
                # Wrap text in p tags
                final_html += f"<p>{part.replace('\n', ' ')}</p>"
    
    return final_html

for p in problems:
    p['description'] = clean_desc(p)
    # Fix setupSql if it's empty but we have tables (from previous step)
    if not p['setupSql'] and p['tables']:
        # Simple placeholder if we have columns but no data
        t = p['tables'][0]
        cols = ", ".join([f"{c['name']} {c['type'].upper()}" for c in t['columns']])
        p['setupSql'] = f"CREATE TABLE IF NOT EXISTS {t['name']} ({cols});"

with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(problems, f, indent=2)

print("Formatting Complete.")
