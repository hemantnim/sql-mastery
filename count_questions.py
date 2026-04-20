import os
import glob
import re
import PyPDF2

folder = r"c:\Users\hgmyc\host-manor\SQL mastery\SQL Questions"
pdf_files = glob.glob(os.path.join(folder, "*.pdf"))

total_questions = 0

print("Analyzing PDFs...")

for pdf_path in pdf_files:
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
        
        filename = os.path.basename(pdf_path).lower()
        count = 0
        
        if "leetcode" in filename:
            # LeetCode questions usually start with a number, a dot, and a capitalized word
            # e.g., "175. Combine Two Tables"
            # But the Table of contents might double count.
            matches = set(re.findall(r'^\d+\.\s+[A-Z][a-zA-Z ]+', text, re.MULTILINE))
            count = len(matches)
        elif "lab manual" in filename:
            # Lab manuals often use Q1, Q.1, Question 1, etc.
            matches = re.findall(r'^(?:Q\s*\d+|Question\s*\d+|Q\.)', text, re.MULTILINE | re.IGNORECASE)
            count = len(matches)
            if count == 0:
                 # fallback to numbered lists
                 matches = re.findall(r'^\d+\.\s+[A-Z]', text, re.MULTILINE)
                 count = len(matches)
        else:
            # Generic interview questions or cheatsheets
            # Look for "Q1", "Question", etc.
            matches = re.findall(r'^(?:Q\s*\d+|Question\s*\d+|Q[1-9]\.|Q\.)', text, re.MULTILINE | re.IGNORECASE)
            count = len(matches)
            if count < 5:
                # Count the number of '?' as a fallback for interview questions
                count = text.count('?')
        
        print(f"- {os.path.basename(pdf_path)}: ~{count} questions")
        total_questions += count
    except Exception as e:
        print(f"- Failed to process {os.path.basename(pdf_path)}: {e}")

print(f"\nTotal estimated questions across all PDFs: {total_questions}")
