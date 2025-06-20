# Intelligent Financial Document OCR Parser

This project is an AI-powered OCR system designed to extract underwriting-relevant financial data—such as monthly deposits, average daily balances, and merchant names—from unstructured or image-based bank statements. Built for real-world use in a Wall Street brokerage.

## 🚀 What It Does

- Extracts:
  - Monthly revenue (deposits)
  - Average daily balances
  - Number of days with negative balances
  - Business name (merchant/borrower)
- Works with scanned PDFs or image files (JPG/PNG)
- Uses NLP + OCR + rule-based error correction

## 🛠 Tech Stack

- Python 3.x
- Tesseract OCR (`pytesseract`)
- `pdf2image`
- `spaCy` (for entity parsing)
- `Streamlit` (optional UI)
- `pandas`, `re`, `numpy`

## 📈 Real-World Impact

> Deployed in an active Wall Street brokerage firm  
> Boosted underwriting throughput by 53%  
> Reduced manual review time across over 1,000 statements/month

## 📂 Project Structure

.
├── src/
│ ├── main.py
│ └── parser/
├── notebooks/
│ └── demo.ipynb
├── sample_data/
│ └── bank_statement_example.png
├── README.md
└── requirements.txt

## 🧠 Next Improvements

- Integrate Donut/LayoutLM for layout-aware parsing
- Add training data interface
- Publish a benchmarking notebook

## 📜 License

MIT License
