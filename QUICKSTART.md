# 🚀 Quick Start Guide

Get your AI Invoice Tool running in under 5 minutes!

## 🎯 One-Command Setup

```bash
# Option 1: Automated setup
python3 setup.py

# Option 2: Quick start script
./run.sh

# Option 3: Manual setup
pip install -r requirements.txt
streamlit run app.py
```

## 📱 Access Your App

Once running, open your browser to:
**http://localhost:8501**

## ✨ First Steps

### 1. Generate Your First Invoice (2 minutes)

1. Click **"📝 Generate Invoice"**
2. Fill in your business details
3. Add a client
4. Add line items (services/products)
5. Click **"🎨 Generate Invoice"**
6. Download your professional PDF!

### 2. Bulk Import from CSV/Excel (1 minute)

1. Click **"📂 Bulk Import"**
2. Upload a CSV or Excel file with invoice data
3. Preview the imported data
4. Click **"📄 Generate Invoice"**
5. Download your professional PDF!

### 3. Extract Data from an Invoice (1 minute)

1. Click **"🔍 Read Invoice"**
2. Upload any PDF or image invoice
3. Click **"🔍 Extract Data"**
4. Review extracted information
5. Export to Excel or CSV!

## 🔧 Optional Enhancements

### Add AI-Powered Extraction
```bash
export OPENAI_API_KEY="your-api-key"
```
Get your key from: https://platform.openai.com/api-keys

### Configure Settings
1. Go to **Settings → AI Models** to add OpenAI API key
2. Go to **Settings → General** to set preferences
3. Configure OCR settings and export formats

## 🐳 Docker Quick Start

```bash
# Build and run with Docker
docker-compose up --build

# Access at http://localhost:8501
```

## 🧪 Test Your Setup

```bash
python3 test_setup.py
```

## 🆘 Need Help?

- **Dependencies missing?** Run `python3 setup.py`
- **OCR not working?** Install Tesseract: `brew install tesseract` (macOS)
- **Can't access app?** Check http://localhost:8501
- **Still stuck?** Check the full README.md

## 🎉 You're Ready!

Your AI Invoice Tool is now ready to:
- ✅ Generate professional invoices instantly
- ✅ Bulk import from CSV/Excel files
- ✅ Extract data from any invoice format
- ✅ Export to Excel and CSV
- ✅ Handle multiple currencies and tax rates

**Happy invoicing! 🧾✨** 