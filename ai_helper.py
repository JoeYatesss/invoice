import openai
import os
import json
from typing import List, Dict, Any, Optional
import streamlit as st

class AIHelper:
    def __init__(self):
        self.client = None
        self._setup_openai()
    
    def _setup_openai(self):
        """Setup OpenAI client with API key from session state or environment"""
        api_key = None
        
        # Try to get from session state first
        if 'settings' in st.session_state and st.session_state.settings.get('openai_api_key'):
            api_key = st.session_state.settings['openai_api_key']
        
        # Fall back to environment variable
        if not api_key:
            api_key = os.getenv('OPENAI_API_KEY')
        
        if api_key:
            try:
                self.client = openai.OpenAI(api_key=api_key)
                return True
            except Exception as e:
                st.warning(f"OpenAI setup failed: {str(e)}")
                return False
        
        return False
    
    def is_available(self) -> bool:
        """Check if OpenAI is available and configured"""
        return self.client is not None
    
    def generate_invoice_items(self, company_info: Dict[str, Any], client_info: Dict[str, Any], 
                              project_description: str = "", num_items: int = 3) -> List[Dict[str, Any]]:
        """Generate invoice items based on company and client information"""
        if not self.is_available():
            return self._get_default_items()
        
        try:
            prompt = f"""
            Generate {num_items} professional invoice line items for the following scenario:
            
            Company: {company_info.get('name', 'Service Provider')}
            Industry/Description: {company_info.get('industry', '')} {company_info.get('description', '')}
            
            Client: {client_info.get('name', 'Client')}
            
            Project Description: {project_description if project_description else 'General services'}
            
            Generate realistic line items with:
            - Professional service descriptions
            - Appropriate quantities (hours, units, etc.)
            - Market-rate pricing in USD
            
            Return only a JSON array with this exact format:
            [
                {{"description": "Service description", "quantity": number, "rate": number}},
                {{"description": "Service description", "quantity": number, "rate": number}}
            ]
            
            Make the services relevant to the company's industry and the project description.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional invoicing assistant. Generate realistic, industry-appropriate invoice line items."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            content = response.choices[0].message.content.strip()
            
            # Extract JSON from response
            if content.startswith('```json'):
                content = content[7:-3]
            elif content.startswith('```'):
                content = content[3:-3]
            
            items = json.loads(content)
            
            # Validate and clean up items
            validated_items = []
            for item in items:
                if all(key in item for key in ['description', 'quantity', 'rate']):
                    validated_items.append({
                        'description': str(item['description']),
                        'quantity': float(item['quantity']),
                        'rate': float(item['rate'])
                    })
            
            return validated_items if validated_items else self._get_default_items()
            
        except Exception as e:
            st.warning(f"AI generation failed: {str(e)}. Using default items.")
            return self._get_default_items()
    
    def enhance_extraction(self, ocr_text: str, document_type: str = "invoice") -> Dict[str, Any]:
        """Use AI to enhance OCR extraction results"""
        if not self.is_available():
            return {"error": "OpenAI not available"}
        
        try:
            prompt = f"""
            Extract structured data from this {document_type} text. The text was obtained via OCR so may have some errors.
            
            OCR Text:
            {ocr_text}
            
            Extract and return ONLY a JSON object with this exact structure:
            {{
                "vendor_name": "extracted vendor/company name",
                "vendor_address": "extracted vendor address",
                "vendor_email": "extracted email if found",
                "vendor_phone": "extracted phone if found",
                "invoice_number": "extracted invoice number",
                "invoice_date": "extracted date in YYYY-MM-DD format",
                "due_date": "extracted due date in YYYY-MM-DD format if found",
                "total_amount": "extracted total amount as number",
                "currency": "detected currency (USD, EUR, etc.)",
                "line_items": [
                    {{"description": "item description", "quantity": number, "rate": number, "amount": number}}
                ]
            }}
            
            If a field cannot be found, use empty string for text fields or 0 for numbers.
            Be as accurate as possible in extracting the information.
            """
            
            response = self.client.chat.completions.create(
                model=st.session_state.settings.get('extraction_model', 'gpt-3.5-turbo'),
                messages=[
                    {"role": "system", "content": "You are an expert at extracting structured data from invoices and receipts. Always return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content.strip()
            
            # Extract JSON from response
            if content.startswith('```json'):
                content = content[7:-3]
            elif content.startswith('```'):
                content = content[3:-3]
            
            result = json.loads(content)
            return result
            
        except Exception as e:
            return {"error": f"AI extraction failed: {str(e)}"}
    
    def suggest_client_info(self, company_name: str, industry: str = "") -> Dict[str, str]:
        """Generate realistic client information for demo purposes"""
        if not self.is_available():
            return {
                "name": "Sample Client Corp",
                "address": "123 Client Street\nCity, State 12345",
                "email": "billing@client.com"
            }
        
        try:
            prompt = f"""
            Generate realistic client information for a {industry} company that would hire {company_name}.
            
            Return ONLY a JSON object:
            {{
                "name": "realistic company name",
                "address": "realistic business address with street, city, state, zip",
                "email": "realistic business email"
            }}
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Generate realistic business information for invoicing demos."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=200
            )
            
            content = response.choices[0].message.content.strip()
            
            if content.startswith('```json'):
                content = content[7:-3]
            elif content.startswith('```'):
                content = content[3:-3]
            
            result = json.loads(content)
            return result
            
        except Exception as e:
            return {
                "name": "Sample Client Corp",
                "address": "123 Client Street\nCity, State 12345", 
                "email": "billing@client.com"
            }
    
    def extract_contract_invoice_data(self, contract_text: str) -> Dict[str, Any]:
        """Extract invoice-relevant data from a contract PDF"""
        if not self.is_available():
            return {"error": "OpenAI not available"}
        
        try:
            prompt = f"""
            Extract invoice-relevant information from this contract text. The goal is to create invoice data from a signed contract.
            
            Contract Text:
            {contract_text}
            
            Extract and return ONLY a JSON object with this exact structure:
            {{
                "client": {{
                    "name": "extracted client/company name",
                    "address": "extracted client address",
                    "email": "extracted client email if found"
                }},
                "business": {{
                    "name": "extracted service provider/contractor name",
                    "address": "extracted provider address",
                    "email": "extracted provider email"
                }},
                "invoice": {{
                    "number": "generate invoice number like INV-YYYYMMDD-001",
                    "date": "{datetime.now().strftime('%Y-%m-%d')}",
                    "due_date": "calculate due date (30 days from today)",
                    "currency": "USD"
                }},
                "items": [
                    {{
                        "description": "service/deliverable description from contract",
                        "quantity": 1,
                        "rate": "extracted price/amount as number"
                    }}
                ],
                "notes": "Professional thank you message",
                "tax_rate": 0.0
            }}
            
            Focus on:
            - Service descriptions and deliverables
            - Payment amounts and pricing
            - Client and service provider details
            - Project scope items
            
            If multiple services are mentioned, create separate line items.
            If total contract value is mentioned, break it down into logical services.
            """
            
            response = self.client.chat.completions.create(
                model=st.session_state.settings.get('extraction_model', 'gpt-3.5-turbo'),
                messages=[
                    {"role": "system", "content": "You are an expert at extracting invoice data from contracts. Always return valid JSON with realistic business information."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=1500
            )
            
            content = response.choices[0].message.content.strip()
            
            # Extract JSON from response
            if content.startswith('```json'):
                content = content[7:-3]
            elif content.startswith('```'):
                content = content[3:-3]
            
            result = json.loads(content)
            return result
            
        except Exception as e:
            return {"error": f"Contract extraction failed: {str(e)}"}

    def _get_default_items(self) -> List[Dict[str, Any]]:
        """Return default invoice items when AI is not available"""
        return [
            {"description": "Consulting Services", "quantity": 10, "rate": 150.0},
            {"description": "Project Development", "quantity": 1, "rate": 2500.0},
            {"description": "Documentation", "quantity": 5, "rate": 100.0}
        ]

# Global instance
ai_helper = AIHelper() 