# -*- coding: utf-8 -*-
"""
Created on Sun Jul  7 17:40:04 2024

@author: proed
"""

import fitz  # PyMuPDF

# Open the PDF file
pdf_path = "Analyse/sollerfüllung_2324.pdf"
document = fitz.open(pdf_path)

# Loop through each page
for page_num in range(document.page_count):
    page = document.load_page(page_num)
    text = page.get_text()