import PyPDF2
pdf_path = r"C:\Users\hgmyc\host-manor\SQL mastery\SQL Questions\SQL leetcode questions .pdf"
with open(pdf_path, 'rb') as file:
    reader = PyPDF2.PdfReader(file)
    with open("full_pdf_text.txt", "w", encoding="utf-8") as out:
        for i, page in enumerate(reader.pages):
            out.write(f"--- PAGE {i} ---\n")
            out.write(page.extract_text() or "")
            out.write("\n")
