#!/usr/bin/env python3
"""
Test script to verify AI Invoice Tool setup
"""

import sys
import importlib

def test_import(module_name, description=""):
    """Test if a module can be imported"""
    try:
        importlib.import_module(module_name)
        print(f"✅ {module_name} - {description}")
        return True
    except ImportError as e:
        print(f"❌ {module_name} - {description} - Error: {e}")
        return False

def test_core_modules():
    """Test core application modules"""
    print("🧪 Testing Core Modules")
    print("-" * 30)
    
    modules = [
        ("app", "Main Streamlit application"),
        ("invoice_generator", "PDF invoice generation"),
        ("invoice_reader", "Invoice data extraction"),
        ("google_sheets_integration", "Google Sheets integration")
    ]
    
    all_passed = True
    for module, desc in modules:
        if not test_import(module, desc):
            all_passed = False
    
    return all_passed

def test_dependencies():
    """Test required dependencies"""
    print("\n📦 Testing Dependencies")
    print("-" * 30)
    
    required_deps = [
        ("streamlit", "Web application framework"),
        ("reportlab", "PDF generation"),
        ("pandas", "Data manipulation"),
        ("PIL", "Image processing"),
    ]
    
    optional_deps = [
        ("pytesseract", "OCR engine (optional)"),
        ("easyocr", "Advanced OCR (optional)"),
        ("fitz", "PDF processing (optional)"),
        ("openai", "AI integration (optional)"),
        ("google.oauth2.service_account", "Google Sheets (optional)"),
    ]
    
    all_required_passed = True
    
    print("Required Dependencies:")
    for module, desc in required_deps:
        if not test_import(module, desc):
            all_required_passed = False
    
    print("\nOptional Dependencies:")
    for module, desc in optional_deps:
        test_import(module, desc)
    
    return all_required_passed

def test_invoice_generation():
    """Test basic invoice generation functionality"""
    print("\n📄 Testing Invoice Generation")
    print("-" * 30)
    
    try:
        from invoice_generator import InvoiceGenerator
        
        # Test data
        test_data = {
            "business": {
                "name": "Test Business",
                "address": "123 Test St",
                "email": "test@business.com",
                "phone": "555-0123"
            },
            "client": {
                "name": "Test Client",
                "address": "456 Client Ave",
                "email": "client@test.com"
            },
            "invoice": {
                "number": "TEST-001",
                "date": "2024-12-01",
                "due_date": "2024-12-31",
                "currency": "USD"
            },
            "items": [
                {"description": "Test Service", "quantity": 1, "rate": 100.00}
            ],
            "notes": "Test invoice",
            "tax_rate": 0
        }
        
        generator = InvoiceGenerator()
        pdf_buffer = generator.create_invoice(test_data)
        
        if pdf_buffer and len(pdf_buffer.getvalue()) > 0:
            print("✅ Invoice generation working")
            return True
        else:
            print("❌ Invoice generation failed - empty output")
            return False
            
    except Exception as e:
        print(f"❌ Invoice generation failed - {e}")
        return False

def test_invoice_reading():
    """Test basic invoice reading functionality"""
    print("\n🔍 Testing Invoice Reading")
    print("-" * 30)
    
    try:
        from invoice_reader import InvoiceReader
        
        reader = InvoiceReader()
        print("✅ Invoice reader initialized")
        
        # Test rule-based extraction with sample text
        sample_text = """
        ACME Corporation
        123 Business Street
        contact@acme.com
        
        INVOICE
        Invoice Number: INV-2024-001
        Date: 2024-12-01
        
        Description: Consulting Services
        Amount: $1,500.00
        
        Total: $1,500.00
        """
        
        extracted_data = reader._rule_based_extraction(sample_text)
        
        if extracted_data and extracted_data.get('vendor_name'):
            print("✅ Rule-based extraction working")
            return True
        else:
            print("❌ Rule-based extraction failed")
            return False
            
    except Exception as e:
        print(f"❌ Invoice reading failed - {e}")
        return False

def main():
    """Main test function"""
    print("🧪 AI Invoice Tool - Setup Test")
    print("=" * 40)
    
    # Test Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    
    print(f"✅ Python {sys.version.split()[0]} detected")
    
    # Run tests
    tests = [
        test_core_modules,
        test_dependencies,
        test_invoice_generation,
        test_invoice_reading
    ]
    
    all_passed = True
    for test in tests:
        if not test():
            all_passed = False
    
    print("\n" + "=" * 40)
    if all_passed:
        print("🎉 All tests passed! Your setup is ready.")
        print("\n📋 Next Steps:")
        print("1. Run: streamlit run app.py")
        print("2. Open http://localhost:8501")
        print("3. Start generating and reading invoices!")
    else:
        print("⚠️  Some tests failed. Check the output above.")
        print("Install missing dependencies and try again.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 