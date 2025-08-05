import pdfplumber
import nltk

nltk.set_proxy("http://proxy_emea.safran:8080")
nltk.download("punkt_tab")

with pdfplumber.open(R"files\filtered\S104800-02-0132à0151-VALISEDS2362.pdf") as pdf:
    first_page = pdf.pages[0]
    text = first_page.extract_text()
    print(text, nltk.word_tokenize(text))
