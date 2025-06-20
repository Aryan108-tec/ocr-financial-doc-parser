
import streamlit as st
import pytesseract
import spacy
from pdf2image import convert_from_path
from PyPDF2 import PdfReader
import tempfile
import re
from datetime import datetime
from collections import defaultdict

st.set_page_config(page_title="Quick Underwriter", layout="wide")
st.title("📄 AI-Powered Quick Underwriting Tool")

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except:
    st.error("Please run: python -m spacy download en_core_web_sm")
    st.stop()

# Patterns
date_pattern = re.compile(r"(\d{1,2}/\d{1,2}/\d{2,4})")
money_pattern = re.compile(r"(\$?[0-9]{1,3}(?:,[0-9]{3})*\.?[0-9]*)")

def extract_text_from_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def extract_with_ocr(file):
    with tempfile.TemporaryDirectory() as path:
        images = convert_from_path(file, output_folder=path)
        text = ""
        for image in images:
            text += pytesseract.image_to_string(image)
        return text

def clean_amount(val):
    try:
        return float(val.replace('$','').replace(',',''))
    except:
        return None

def parse_underwriting(text):
    lines = text.split('\n')
    deposits = defaultdict(float)
    balances = {}
    company_name = ""
    avg_balance = None
    negative_days = 0

    # Company name (first 10 lines NER)
    header = '\n'.join(lines[:10])
    doc = nlp(header)
    for ent in doc.ents:
        if ent.label_ in ['ORG', 'PERSON']:
            company_name = ent.text
            break

    for i, line in enumerate(lines):
        if 'average ledger balance' in line.lower() or 'average daily balance' in line.lower():
            amt = money_pattern.search(line)
            if amt:
                avg_balance = clean_amount(amt.group())

        if 'ending balance' in line.lower() and date_pattern.search(line):
            amt = money_pattern.search(line)
            if amt:
                dt = date_pattern.search(line).group()
                val = clean_amount(amt.group())
                try:
                    dt = datetime.strptime(dt, '%m/%d/%Y')
                    balances[dt] = val
                    if val < 0:
                        negative_days += 1
                except:
                    pass

        # Deposits block or inferred deposit
        if date_pattern.search(line) and money_pattern.search(line):
            lower = line.lower()
            if any(w in lower for w in ['deposit', 'credit', 'from']) and not any(w in lower for w in ['withdrawal', 'debit']):
                dt = date_pattern.search(line).group()
                val = clean_amount(money_pattern.search(line).group())
                try:
                    dt = datetime.strptime(dt, '%m/%d/%Y')
                    if val and val > 0:
                        deposits[dt] += val
                except:
                    pass

    return company_name, deposits, avg_balance, negative_days

uploaded_file = st.file_uploader("Upload a bank statement PDF", type=["pdf"])

if uploaded_file:
    st.success(f"📄 Processing: {uploaded_file.name}")

    try:
        text = extract_text_from_pdf(uploaded_file)
        if len(text.strip()) < 50:
            raise ValueError("Switching to OCR...")
    except:
        uploaded_file.seek(0)
        text = extract_with_ocr(uploaded_file)

    name, deposits, avg_bal, neg_days = parse_underwriting(text)

    st.subheader("📌 Underwriting Summary")

    st.write(f"**🧾 Company Name:** {name or 'Not detected'}")
    st.write(f"**💰 Monthly Revenue:** ${sum(deposits.values()):,.2f}")
    if deposits:
        with st.expander("🗓️ Deposit Breakdown"):
            for dt, amt in sorted(deposits.items()):
                st.write(f"- {dt.strftime('%b %d, %Y')}: ${amt:,.2f}")

    st.write(f"**📉 Avg Daily Balance:** ${avg_bal:,.2f}" if avg_bal else "**📉 Avg Daily Balance:** Not found")
    st.write(f"**🔻 Negative Balance Days:** {neg_days}")

    with st.expander("📄 Raw Extracted Text"):
        st.text(text)
