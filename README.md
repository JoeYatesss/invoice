# 🤖 AI-Powered Invoicing Tool

A comprehensive invoicing solution built with Streamlit that provides three core functionalities:

1. **📝 Generate Professional Invoices** - Create clean, styled invoices with minimal input
2. **📂 Bulk Import from CSV/Excel** - Upload CSV/Excel files and generate invoices automatically
3. **🔍 Extract Invoice Data** - Read any invoice format and export to Excel/CSV

## ✨ Features

### Invoice Generation
- **Clean, Professional Design** - Modern invoice templates with consistent styling
- **Minimal Input Required** - Just fill in basic details and line items
- **Instant PDF Generation** - Download invoices immediately
- **Tax Calculations** - Automatic subtotal, tax, and total calculations
- **Multiple Currencies** - Support for USD, EUR, GBP, CAD, AUD

### Invoice Data Extraction
- **Multi-Format Support** - PDF, PNG, JPG, JPEG
- **Advanced OCR** - EasyOCR and Tesseract integration
- **AI-Powered Extraction** - OpenAI GPT integration for intelligent data parsing
- **Flexible Extraction Methods** - Auto, OCR+LLM, OCR Only, Layout Analysis
- **Structured Output** - Vendor info, invoice details, line items

### Bulk Import & Export
- **CSV/Excel Import** - Upload files with invoice data and generate PDFs
- **Smart Data Parsing** - Automatically detect business info, client details, line items
- **Excel Export** - Download structured data in Excel format with multiple sheets
- **CSV Export** - Download structured data in CSV format
- **PDF Summaries** - Generate summary reports
- **Batch Processing** - Handle multiple invoices at once

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd invoice

# Install dependencies
pip install -r requirements.txt

# Install additional system dependencies (macOS)
brew install tesseract
```

### 2. Basic Setup

```bash
# Run the application
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

### 3. Optional: Enhanced Features Setup

#### OpenAI Integration (for AI-powered extraction)
```bash
# Set your OpenAI API key
export OPENAI_API_KEY="your-api-key-here"
```

#### Google Sheets Integration
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google Sheets API
4. Create a Service Account and download the JSON credentials
5. Upload the credentials file in the Settings tab of the app

## 📖 Usage Guide

### Generating Invoices

1. **Navigate to "📝 Generate Invoice"**
2. **Fill in Business Information**
   - Your company details (name, address, email, phone)
3. **Add Client Information**
   - Client company details
4. **Configure Invoice Details**
   - Invoice number, dates, currency
5. **Add Line Items**
   - Description, quantity, rate for each service/product
   - Use ➕ to add more items, 🗑️ to delete
6. **Set Additional Info**
   - Notes, tax rate
7. **Generate & Download**
   - Click "🎨 Generate Invoice"
   - Download the PDF

### Reading & Extracting Invoice Data

1. **Navigate to "🔍 Read Invoice"**
2. **Upload Invoice File**
   - Drag & drop or browse for PDF/image files
3. **Choose Extraction Method**
   - **Auto (Recommended)**: Best available method
   - **OCR + LLM**: OCR + AI processing (requires OpenAI API)
   - **OCR Only**: Traditional OCR with rule-based extraction
   - **Layout Analysis**: Advanced PDF structure analysis
4. **Extract Data**
   - Click "🔍 Extract Data"
   - Review and edit extracted information
5. **Export Options**
   - **📊 Export to CSV**: Download CSV file
   - **📋 Export to Excel**: Download Excel file with multiple sheets
   - **📄 Export Summary**: Generate PDF summary

### Bulk Import from CSV/Excel

1. **Navigate to "📂 Bulk Import"**
2. **Upload CSV/Excel File**
   - Drag & drop or browse for CSV/Excel files
   - Supports multiple formats: line items only, structured data, multi-sheet Excel
3. **Preview Imported Data**
   - Review business info, client details, line items
   - See calculated totals
4. **Generate Invoice**
   - Click "📄 Generate Invoice" to create PDF
   - Download the professional invoice immediately
5. **Export Options**
   - **📊 Export to Excel**: Download structured data

### Settings Configuration

#### AI Models Setup
1. **Navigate to "⚙️ Settings" → "AI Models"**
2. **Configure OpenAI API Key** (optional, for enhanced extraction)
3. **Select Default Extraction Model**

#### General Settings
1. **Navigate to "⚙️ Settings" → "General"**
2. **Set Default Currency**
3. **Choose Export Format Preferences**
4. **Configure OCR Settings**

## 🛠️ Technical Architecture

### Core Components

- **`app.py`** - Main Streamlit application with UI
- **`invoice_generator.py`** - PDF invoice generation using ReportLab
- **`invoice_reader.py`** - Multi-engine OCR and AI-powered data extraction
- **`csv_excel_processor.py`** - CSV/Excel import and export functionality

### Dependencies

- **Streamlit** - Web application framework
- **ReportLab** - PDF generation
- **PyMuPDF** - PDF text extraction
- **EasyOCR & Tesseract** - Optical Character Recognition
- **OpenAI** - AI-powered data extraction (optional)
- **Pandas & OpenPyXL** - Data manipulation and Excel processing
- **XlsxWriter** - Excel file generation

## 🔧 Advanced Configuration

### Environment Variables

```bash
# Optional: OpenAI API for enhanced extraction
OPENAI_API_KEY=your_openai_api_key

# Optional: Default extraction model
DEFAULT_EXTRACTION_MODEL=gpt-3.5-turbo
```

### CSV/Excel File Formats

The app supports multiple CSV/Excel formats:

#### Format 1: Line Items Only
```csv
Description,Quantity,Rate
Consulting Services,10,150
Web Development,1,2500
Design Work,5,200
```

#### Format 2: Structured Data
```csv
Business Name,Your Company Name
Business Email,contact@company.com
Client Name,Client Corp
Invoice Number,INV-001

Description,Quantity,Rate
Service 1,2,100
Service 2,1,200
```

#### Format 3: Multi-Sheet Excel
- **Sheet 1 "Info"**: Business and client details (key-value pairs)
- **Sheet 2 "Items"**: Line items with Description, Quantity, Rate columns

### OCR Dependencies

#### macOS
```bash
brew install tesseract
```

#### Ubuntu/Debian
```bash
sudo apt-get install tesseract-ocr
```

#### Windows
- Download Tesseract from [GitHub releases](https://github.com/UB-Mannheim/tesseract/wiki)
- Add to PATH

## 🚀 Deployment Options

### Local Development
```bash
streamlit run app.py
```

### Docker Deployment
```dockerfile
FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libgl1-mesa-glx \
    libglib2.0-0

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Streamlit Cloud
1. Push code to GitHub
2. Connect repository to [Streamlit Cloud](https://streamlit.io/cloud)
3. Deploy with one click

## 🎯 Use Cases

### For Freelancers
- Quick invoice generation for clients
- Track incoming invoice payments
- Organize client billing information

### For Small Businesses
- Standardize invoice format across team
- Bulk import invoice data from CSV/Excel
- Convert existing spreadsheets to professional invoices

### For Accounting Teams
- Batch process supplier invoices
- Extract invoice data to Excel for analysis
- Generate structured reports from invoice data

## 🔒 Security & Privacy

- **Local Processing**: OCR runs locally when possible
- **API Security**: OpenAI API calls use encrypted connections
- **No Data Storage**: App doesn't store uploaded files permanently
- **File Processing**: All file processing happens locally

## 🐛 Troubleshooting

### Common Issues

#### OCR Not Working
```bash
# Install Tesseract
brew install tesseract  # macOS
sudo apt-get install tesseract-ocr  # Ubuntu
```

#### File Upload Issues
- Ensure file is in supported format (CSV, .xlsx, .xls)
- Check file isn't corrupted or password-protected
- Verify file has readable data structure

#### OpenAI API Errors
- Verify API key is correctly set
- Check API quota and billing
- Ensure model (gpt-3.5-turbo) is available

#### PDF Generation Issues
- Check ReportLab installation: `pip install reportlab`
- Verify system fonts are available

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit pull request

## 📄 License

MIT License - see LICENSE file for details

## 🔮 Roadmap

- [ ] **Enhanced Templates** - Multiple invoice design options
- [ ] **Multi-language OCR** - Support for non-English invoices
- [ ] **Database Integration** - PostgreSQL/SQLite support
- [ ] **Email Integration** - Send invoices directly via email
- [ ] **Recurring Invoices** - Schedule automatic invoice generation
- [ ] **Mobile Optimization** - Better mobile experience
- [ ] **API Endpoints** - REST API for programmatic access

## 💬 Support

For questions, issues, or feature requests:
- Open an issue on GitHub
- Check the troubleshooting section above
- Review the documentation

---

**Built with ❤️ using Streamlit, OpenAI, and modern Python tools**