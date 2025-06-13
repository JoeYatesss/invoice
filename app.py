import streamlit as st
import fitz  # PyMuPDF
import os
import json
from dotenv import load_dotenv
from xero import Xero
from xero.auth import OAuth2Credentials
from xero.constants import XeroScopes
import openai

# Load environment variables
load_dotenv()

# Initialize OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

# Initialize Xero credentials
def get_xero_client():
    credentials = OAuth2Credentials(
        client_id=os.getenv('XERO_CLIENT_ID'),
        client_secret=os.getenv('XERO_CLIENT_SECRET'),
        callback_uri=os.getenv('XERO_CALLBACK_URI'),
        scope=[XeroScopes.ACCOUNTING_TRANSACTIONS]
    )
    return Xero(credentials)

def extract_text_from_pdf(pdf_file):
    """Extract text from uploaded PDF file."""
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def extract_invoice_data_with_openai(text):
    """Use OpenAI to extract structured invoice data from text."""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # or "gpt-3.5-turbo" if you prefer
            messages=[
                {"role": "system", "content": """You are an expert at extracting invoice data. 
                Extract the following information from the invoice text:
                - Invoice number
                - Invoice date
                - Due date
                - Total amount
                - Customer name and details
                - Line items (description, quantity, unit price, amount)
                - Tax information
                Return the data in a structured JSON format."""},
                {"role": "user", "content": text}
            ],
            temperature=0.1  # Low temperature for more consistent results
        )
        
        # Parse the response to get structured data
        extracted_data = json.loads(response.choices[0].message.content)
        return extracted_data
    except Exception as e:
        st.error(f"Error extracting data with OpenAI: {str(e)}")
        return None

def create_xero_invoice(extracted_data):
    """Create an invoice in Xero based on extracted data."""
    invoice_data = {
        "Type": "ACCREC",
        "Contact": {
            "Name": extracted_data.get("customer_name", "Unknown Customer"),
            "EmailAddress": extracted_data.get("customer_email", ""),
            "Addresses": [{
                "AddressType": "POBOX",
                "AddressLine1": extracted_data.get("customer_address", "")
            }]
        },
        "LineItems": [],
        "Date": extracted_data.get("invoice_date", ""),
        "DueDate": extracted_data.get("due_date", ""),
        "Status": "DRAFT",
        "CurrencyCode": "USD"  # You might want to make this configurable
    }
    
    # Add line items
    for item in extracted_data.get("line_items", []):
        invoice_data["LineItems"].append({
            "Description": item.get("description", ""),
            "Quantity": item.get("quantity", 1),
            "UnitAmount": item.get("unit_price", 0),
            "AccountCode": "200"  # This should be your sales account code
        })
    
    return invoice_data

def main():
    st.title("PDF to Xero Invoice Uploader")
    
    # File upload
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    
    if uploaded_file is not None:
        # Extract text from PDF
        with st.spinner("Extracting text from PDF..."):
            text_data = extract_text_from_pdf(uploaded_file)
        
        # Extract structured data using OpenAI
        with st.spinner("Analyzing invoice with AI..."):
            extracted_data = extract_invoice_data_with_openai(text_data)
        
        if extracted_data:
            # Display extracted data
            st.subheader("Extracted Invoice Data")
            st.json(extracted_data)
            
            # Create invoice in Xero
            if st.button("Create Xero Invoice"):
                try:
                    xero = get_xero_client()
                    invoice_data = create_xero_invoice(extracted_data)
                    
                    # Preview the invoice data
                    st.subheader("Preview Invoice Data")
                    st.json(invoice_data)
                    
                    # Confirm before sending to Xero
                    if st.button("Confirm and Send to Xero"):
                        invoice = xero.invoices.put(invoice_data)
                        st.success("Invoice created successfully in Xero!")
                        st.json(invoice)
                except Exception as e:
                    st.error(f"Error creating invoice: {str(e)}")
        else:
            st.error("Failed to extract invoice data. Please check the PDF format and try again.")

if __name__ == "__main__":
    main() 