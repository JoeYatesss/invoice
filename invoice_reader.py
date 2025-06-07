import os
import json
import re
from typing import Dict, Any
from io import BytesIO

# OCR and Image Processing
try:
    import pytesseract
    import easyocr
    from PIL import Image
    from pdf2image import convert_from_bytes
    import fitz  # PyMuPDF
    TESSERACT_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Some OCR dependencies not available: {e}")
    TESSERACT_AVAILABLE = False

# AI/LLM Integration
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    print("Warning: OpenAI not available")
    OPENAI_AVAILABLE = False

class InvoiceReader:
    def __init__(self):
        self.supported_formats = ['pdf', 'png', 'jpg', 'jpeg']
        self.easyocr_reader = None
        self.openai_client = None
        self._init_ocr_engines()
        self._init_llm()
    
    def _init_ocr_engines(self):
        """Initialize OCR engines"""
        try:
            if TESSERACT_AVAILABLE:
                self.easyocr_reader = easyocr.Reader(['en'])
                print("✅ EasyOCR initialized successfully")
        except Exception as e:
            print(f"Warning: Could not initialize EasyOCR: {e}")
    
    def _init_llm(self):
        """Initialize LLM client"""
        try:
            if OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY"):
                self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                print("✅ OpenAI client initialized successfully")
        except Exception as e:
            print(f"Warning: Could not initialize OpenAI: {e}")
    
    def extract_invoice_data(self, uploaded_file, method: str = "auto") -> Dict[str, Any]:
        """Extract data from uploaded invoice file"""
        file_content = uploaded_file.read()
        file_extension = uploaded_file.name.lower().split('.')[-1]
        
        if file_extension not in self.supported_formats:
            raise ValueError(f"Unsupported file format: {file_extension}")
        
        if method.lower() in ["auto", "auto (recommended)"]:
            extracted_data = self._auto_extract(file_content, file_extension)
        elif method.lower() == "ocr + llm":
            extracted_data = self._ocr_plus_llm_extract(file_content, file_extension)
        elif method.lower() == "ocr only":
            extracted_data = self._ocr_only_extract(file_content, file_extension)
        else:
            extracted_data = self._auto_extract(file_content, file_extension)
        
        return extracted_data
    
    def _auto_extract(self, file_content: bytes, file_extension: str) -> Dict[str, Any]:
        """Automatically choose the best extraction method"""
        try:
            if self.openai_client:
                return self._ocr_plus_llm_extract(file_content, file_extension)
            else:
                return self._ocr_only_extract(file_content, file_extension)
        except Exception as e:
            print(f"Auto extraction failed: {e}")
            return self._basic_ocr_extract(file_content, file_extension)
    
    def _ocr_plus_llm_extract(self, file_content: bytes, file_extension: str) -> Dict[str, Any]:
        """Use OCR to extract text, then LLM to structure the data"""
        raw_text = self._extract_text_from_file(file_content, file_extension)
        
        if not raw_text.strip():
            raise ValueError("No text could be extracted from the document")
        
        if self.openai_client:
            structured_data = self._llm_structure_data(raw_text)
        else:
            structured_data = self._rule_based_extraction(raw_text)
        
        return structured_data
    
    def _ocr_only_extract(self, file_content: bytes, file_extension: str) -> Dict[str, Any]:
        """Use only OCR with rule-based post-processing"""
        raw_text = self._extract_text_from_file(file_content, file_extension)
        return self._rule_based_extraction(raw_text)
    
    def _extract_text_from_file(self, file_content: bytes, file_extension: str) -> str:
        """Extract raw text from file using multiple OCR engines"""
        if file_extension == 'pdf':
            return self._extract_text_from_pdf(file_content)
        else:
            return self._extract_text_from_image(file_content)
    
    def _extract_text_from_pdf(self, pdf_content: bytes) -> str:
        """Extract text from PDF using multiple methods"""
        try:
            doc = fitz.open(stream=pdf_content, filetype="pdf")
            mupdf_text = ""
            for page in doc:
                mupdf_text += page.get_text()
            doc.close()
            
            if mupdf_text.strip():
                return mupdf_text
                
        except Exception as e:
            print(f"PyMuPDF extraction failed: {e}")
        
        return ""
    
    def _extract_text_from_image(self, image_content: bytes) -> str:
        """Extract text from image using OCR"""
        try:
            image = Image.open(BytesIO(image_content))
            
            if self.easyocr_reader:
                try:
                    results = self.easyocr_reader.readtext(image)
                    return " ".join([result[1] for result in results])
                except Exception as e:
                    print(f"EasyOCR failed: {e}")
            
            if TESSERACT_AVAILABLE:
                try:
                    return pytesseract.image_to_string(image)
                except Exception as e:
                    print(f"Tesseract failed: {e}")
            
            return ""
        except Exception as e:
            print(f"Image text extraction failed: {e}")
            return ""
    
    def _rule_based_extraction(self, text: str) -> Dict[str, Any]:
        """Extract invoice data using rule-based pattern matching"""
        extracted_data = {
            "vendor_name": "",
            "vendor_address": "",
            "vendor_email": "",
            "vendor_phone": "",
            "invoice_number": "",
            "invoice_date": "",
            "due_date": "",
            "total_amount": "",
            "line_items": []
        }
        
        try:
            # Extract email
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            emails = re.findall(email_pattern, text)
            if emails:
                extracted_data["vendor_email"] = emails[0]
            
            # Extract invoice number
            invoice_patterns = [
                r'(?i)invoice\s*#?\s*:?\s*([A-Z0-9-]+)',
                r'(?i)inv\s*#?\s*:?\s*([A-Z0-9-]+)',
                r'(?i)invoice\s*number\s*:?\s*([A-Z0-9-]+)'
            ]
            for pattern in invoice_patterns:
                match = re.search(pattern, text)
                if match:
                    extracted_data["invoice_number"] = match.group(1)
                    break
            
            # Extract total amount
            total_patterns = [
                r'(?i)total\s*:?\s*\$?([0-9,]+\.?\d*)',
                r'(?i)amount\s*due\s*:?\s*\$?([0-9,]+\.?\d*)'
            ]
            for pattern in total_patterns:
                match = re.search(pattern, text)
                if match:
                    amount = match.group(1).replace(',', '')
                    extracted_data["total_amount"] = amount
                    break
            
            # Extract vendor name
            lines = text.split('\n')
            for line in lines[:5]:
                line = line.strip()
                if line and len(line) > 2 and '@' not in line:
                    extracted_data["vendor_name"] = line
                    break
            
        except Exception as e:
            print(f"Rule-based extraction failed: {e}")
        
        return extracted_data
    
    def _llm_structure_data(self, raw_text: str) -> Dict[str, Any]:
        """Use LLM to structure raw OCR text into invoice data"""
        if not self.openai_client:
            return self._rule_based_extraction(raw_text)
        
        try:
            prompt = f"""Extract invoice information from this text and return only valid JSON:
            
            Invoice text: {raw_text[:2000]}
            
            Return format:
            {{
                "vendor_name": "...",
                "vendor_address": "...", 
                "vendor_email": "...",
                "vendor_phone": "...",
                "invoice_number": "...",
                "invoice_date": "...",
                "due_date": "...",
                "total_amount": "...",
                "line_items": []
            }}"""
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=1000
            )
            
            response_text = response.choices[0].message.content.strip()
            
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            structured_data = json.loads(response_text)
            return structured_data
            
        except Exception as e:
            print(f"LLM structuring failed: {e}")
            return self._rule_based_extraction(raw_text)
    
    def _basic_ocr_extract(self, file_content: bytes, file_extension: str) -> Dict[str, Any]:
        """Basic OCR extraction as final fallback"""
        try:
            if file_extension == 'pdf':
                doc = fitz.open(stream=file_content, filetype="pdf")
                text = ""
                for page in doc:
                    text += page.get_text()
                doc.close()
            else:
                image = Image.open(BytesIO(file_content))
                text = pytesseract.image_to_string(image) if TESSERACT_AVAILABLE else ""
            
            return self._rule_based_extraction(text)
            
        except Exception as e:
            return {
                "vendor_name": "",
                "vendor_address": "",
                "vendor_email": "",
                "vendor_phone": "",
                "invoice_number": "",
                "invoice_date": "",
                "due_date": "",
                "total_amount": "",
                "line_items": [],
                "error": f"Extraction failed: {str(e)}"
            }

if __name__ == "__main__":
    reader = InvoiceReader()
    print("Invoice Reader initialized successfully!")
