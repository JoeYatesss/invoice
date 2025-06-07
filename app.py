import streamlit as st
import os
from datetime import datetime
import pandas as pd
from io import BytesIO
import base64

# Import our custom modules
from invoice_generator import InvoiceGenerator
from invoice_reader import InvoiceReader
from csv_excel_processor import CSVExcelProcessor
from ai_helper import ai_helper

# Page config
st.set_page_config(
    page_title="AI Invoice Tool",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    st.title("🤖 AI-Powered Invoicing Tool")
    st.markdown("### Generate invoices effortlessly & extract data from any invoice format")
    
    # Initialize session state for settings persistence
    if 'settings' not in st.session_state:
        st.session_state.settings = {
            "openai_api_key": "",
            "default_currency": "USD",
            "export_format": "Excel (.xlsx)",
            "ocr_language": "English",
            "confidence_threshold": 0.7,
            "extraction_model": "gpt-3.5-turbo"
        }
    
    # Initialize session state for company profile
    if 'company_profile' not in st.session_state:
        st.session_state.company_profile = {
            "name": "",
            "address": "",
            "email": "",
            "phone": "",
            "industry": "",
            "description": ""
        }
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose Action",
        ["📝 Generate Invoice", "🔍 Read Invoice", "📂 Bulk Import", "⚙️ Settings"]
    )
    
    if page == "📝 Generate Invoice":
        generate_invoice_page()
    elif page == "🔍 Read Invoice":
        read_invoice_page()
    elif page == "📂 Bulk Import":
        bulk_import_page()
    elif page == "⚙️ Settings":
        settings_page()

def generate_invoice_page():
    st.header("📝 Generate Invoice from Spreadsheet")
    st.markdown("Upload Excel/CSV file to automatically populate invoice data")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # File Upload Section
        st.subheader("📂 Upload Invoice Data")
        
        uploaded_file = st.file_uploader(
            "Upload Excel or CSV file with invoice data",
            type=['csv', 'xlsx', 'xls'],
            help="Upload a file containing client details, invoice items, and billing information"
        )
        
        if uploaded_file is not None:
            try:
                with st.spinner("📊 Processing file..."):
                    processor = CSVExcelProcessor()
                    invoice_data = processor.read_invoice_data_from_file(uploaded_file)
                
                st.success(f"✅ File processed: {uploaded_file.name}")
                st.session_state.uploaded_invoice_data = invoice_data
                
                # Show preview of imported data
                with st.expander("📋 Imported Data Preview", expanded=True):
                    col_prev1, col_prev2 = st.columns(2)
                    
                    with col_prev1:
                        st.write("**Client Information:**")
                        client_data = invoice_data.get('client', {})
                        st.write(f"Name: {client_data.get('name', 'Not specified')}")
                        st.write(f"Email: {client_data.get('email', 'Not specified')}")
                        st.write(f"Address: {client_data.get('address', 'Not specified')}")
                    
                    with col_prev2:
                        st.write("**Invoice Details:**")
                        inv_data = invoice_data.get('invoice', {})
                        st.write(f"Number: {inv_data.get('number', 'Auto-generated')}")
                        st.write(f"Date: {inv_data.get('date', 'Today')}")
                        st.write(f"Currency: {inv_data.get('currency', 'USD')}")
                    
                    # Show line items
                    if invoice_data.get('items'):
                        st.write("**Line Items:**")
                        df = pd.DataFrame(invoice_data['items'])
                        st.dataframe(df, use_container_width=True)
                        
                        # Calculate total
                        total = sum(item.get('quantity', 0) * item.get('rate', 0) for item in invoice_data['items'])
                        st.metric("Total Amount", f"${total:.2f}")
                
            except Exception as e:
                st.error(f"Error processing file: {str(e)}")
        
        st.divider()
        
        # Business Information with saving (always show for profile management)
        st.subheader("💼 Your Business Profile")
        with st.expander("Business Information"):
            col_biz1, col_biz2 = st.columns([3, 1])
            
            with col_biz1:
                business_name = st.text_input(
                    "Business Name", 
                    value=st.session_state.company_profile.get("name", "Your Business")
                )
                business_address = st.text_area(
                    "Business Address", 
                    value=st.session_state.company_profile.get("address", "123 Business St\nCity, State 12345")
                )
                business_email = st.text_input(
                    "Email", 
                    value=st.session_state.company_profile.get("email", "contact@yourbusiness.com")
                )
                business_phone = st.text_input(
                    "Phone", 
                    value=st.session_state.company_profile.get("phone", "+1 (555) 123-4567")
                )
                business_industry = st.text_input(
                    "Industry", 
                    value=st.session_state.company_profile.get("industry", ""),
                    help="e.g., Consulting, Web Development, Marketing"
                )
                business_description = st.text_area(
                    "Description", 
                    value=st.session_state.company_profile.get("description", ""),
                    help="Brief description of your services"
                )
            
            with col_biz2:
                st.write("**Company Profile**")
                if st.button("💾 Save Profile", use_container_width=True):
                    st.session_state.company_profile = {
                        "name": business_name,
                        "address": business_address,
                        "email": business_email,
                        "phone": business_phone,
                        "industry": business_industry,
                        "description": business_description
                    }
                    st.success("✅ Profile saved!")
                
                if st.button("🔄 Load Profile", use_container_width=True):
                    st.rerun()
    
    with col2:
        st.subheader("Generate Invoice")
        
        # Show status
        if 'uploaded_invoice_data' in st.session_state:
            data = st.session_state.uploaded_invoice_data
            
            # Calculate totals from uploaded data
            items = data.get('items', [])
            subtotal = sum(item.get('quantity', 0) * item.get('rate', 0) for item in items)
            tax_rate = data.get('tax_rate', 0.0)
            tax_amount = subtotal * (tax_rate / 100)
            total = subtotal + tax_amount
            
            currency = data.get('invoice', {}).get('currency', 'USD')
            
            st.metric("Subtotal", f"{currency} {subtotal:.2f}")
            if tax_rate > 0:
                st.metric("Tax", f"{currency} {tax_amount:.2f}")
            st.metric("Total", f"{currency} {total:.2f}")
            
            st.divider()
            
            # Generate button
            if st.button("🎨 Generate Invoice", type="primary", use_container_width=True):
                try:
                    # Merge uploaded data with business profile
                    business_data = st.session_state.company_profile.copy()
                    if not business_data.get('name'):
                        business_data = data.get('business', {})
                    
                    invoice_data = {
                        "business": business_data,
                        "client": data.get('client', {}),
                        "invoice": data.get('invoice', {}),
                        "items": data.get('items', []),
                        "notes": data.get('notes', "Thank you for your business!"),
                        "tax_rate": data.get('tax_rate', 0.0)
                    }
                    
                    generator = InvoiceGenerator()
                    pdf_buffer = generator.create_invoice(invoice_data)
                    
                    st.success("✅ Invoice generated successfully!")
                    
                    # Download button
                    invoice_num = data.get('invoice', {}).get('number', f"INV-{datetime.now().strftime('%Y%m%d')}")
                    st.download_button(
                        label="📥 Download PDF",
                        data=pdf_buffer.getvalue(),
                        file_name=f"invoice_{invoice_num}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                    
                except Exception as e:
                    st.error(f"Error generating invoice: {str(e)}")
                    
        else:
            st.info("📤 Upload a CSV/Excel file to generate an invoice")
            
            with st.expander("📋 File Format Guidelines"):
                st.markdown("""
                **Required Data:**
                - Client information (name, address, email)
                - Line items (description, quantity, rate)
                
                **Example CSV Format:**
                ```
                Business Name,Your Company
                Client Name,Client Corp
                Client Email,billing@client.com
                Invoice Number,INV-001
                
                Description,Quantity,Rate
                Consulting,10,150
                Development,1,2500
                ```
                """)
        
        st.divider()
        
        # AI Enhancement option
        if 'uploaded_invoice_data' in st.session_state and ai_helper.is_available():
            st.subheader("🤖 AI Enhancement")
            
            if st.button("✨ Enhance with AI", use_container_width=True):
                company_info = st.session_state.company_profile
                client_info = st.session_state.uploaded_invoice_data.get('client', {})
                
                with st.spinner("AI enhancing invoice items..."):
                    enhanced_items = ai_helper.generate_invoice_items(
                        company_info,
                        client_info,
                        "Professional services based on uploaded data",
                        num_items=len(st.session_state.uploaded_invoice_data.get('items', []))
                    )
                    
                    # Merge with existing data
                    st.session_state.uploaded_invoice_data['items'] = enhanced_items
                    st.success("✅ Items enhanced with AI!")
                    st.rerun()

def bulk_import_page():
    st.header("📂 Bulk Invoice Generation")
    st.markdown("Upload Excel/CSV with multiple clients or invoices to generate multiple PDFs automatically")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Upload Bulk Invoice Data")
        
        uploaded_file = st.file_uploader(
            "Upload CSV or Excel file with multiple invoice records",
            type=['csv', 'xlsx', 'xls'],
            help="Upload a file containing multiple clients or invoice records"
        )
        
        if uploaded_file is not None:
            st.success(f"✅ File uploaded: {uploaded_file.name}")
            
            # Show file format help
            with st.expander("Bulk File Format Guidelines"):
                st.markdown("""
                **Multiple Clients Format:**
                ```
                Client,Description,Quantity,Rate,Client_Email
                ABC Corp,Consulting,10,150,billing@abc.com
                ABC Corp,Development,5,200,billing@abc.com
                XYZ Ltd,Design,3,300,finance@xyz.com
                XYZ Ltd,Support,2,100,finance@xyz.com
                ```
                
                **Multiple Invoices Format:**
                ```
                Invoice_Number,Client,Description,Quantity,Rate
                INV-001,ABC Corp,Consulting,10,150
                INV-001,ABC Corp,Development,5,200
                INV-002,XYZ Ltd,Design,3,300
                INV-002,XYZ Ltd,Support,2,100
                ```
                
                **The app will automatically detect and group by:**
                - Unique client names → Separate invoices per client
                - Unique invoice numbers → Separate invoices per number
                """)
            
            if st.button("🔍 Process Bulk File", type="primary", use_container_width=True):
                try:
                    with st.spinner("📊 Processing bulk invoices..."):
                        processor = CSVExcelProcessor()
                        bulk_invoices = processor.process_bulk_invoices(uploaded_file)
                    
                    st.session_state.bulk_invoices = bulk_invoices
                    st.success(f"✅ Processed {len(bulk_invoices)} invoice(s)!")
                    
                except Exception as e:
                    st.error(f"Error processing file: {str(e)}")
    
    with col2:
        st.subheader("Bulk Invoice Preview")
        
        if 'bulk_invoices' in st.session_state:
            invoices = st.session_state.bulk_invoices
            
            st.write(f"**Found {len(invoices)} invoice(s) to generate:**")
            
            # Show summary of each invoice
            for i, invoice in enumerate(invoices):
                with st.expander(f"Invoice {i+1}: {invoice.get('client', {}).get('name', 'Unknown Client')}", expanded=False):
                    col_inv1, col_inv2 = st.columns(2)
                    
                    with col_inv1:
                        st.write("**Client:**")
                        client = invoice.get('client', {})
                        st.write(f"Name: {client.get('name', 'N/A')}")
                        st.write(f"Email: {client.get('email', 'N/A')}")
                        
                    with col_inv2:
                        st.write("**Invoice:**")
                        inv_info = invoice.get('invoice', {})
                        st.write(f"Number: {inv_info.get('number', 'Auto')}")
                        st.write(f"Date: {inv_info.get('date', 'Today')}")
                    
                    # Show items
                    if invoice.get('items'):
                        st.write("**Items:**")
                        df = pd.DataFrame(invoice['items'])
                        st.dataframe(df, use_container_width=True)
                        
                        total = sum(item.get('quantity', 0) * item.get('rate', 0) for item in invoice['items'])
                        st.write(f"**Total: ${total:.2f}**")
            
            st.divider()
            
            # Bulk generation buttons
            col_bulk1, col_bulk2 = st.columns(2)
            
            with col_bulk1:
                if st.button("📄 Generate All Invoices", type="primary", use_container_width=True):
                    try:
                        generator = InvoiceGenerator()
                        generated_files = []
                        
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        for i, invoice_data in enumerate(invoices):
                            # Merge with business profile
                            business_data = st.session_state.company_profile.copy()
                            if not business_data.get('name'):
                                business_data = invoice_data.get('business', {})
                            
                            complete_invoice_data = {
                                "business": business_data,
                                "client": invoice_data.get('client', {}),
                                "invoice": invoice_data.get('invoice', {}),
                                "items": invoice_data.get('items', []),
                                "notes": invoice_data.get('notes', "Thank you for your business!"),
                                "tax_rate": invoice_data.get('tax_rate', 0.0)
                            }
                            
                            status_text.text(f"Generating invoice {i+1} of {len(invoices)}...")
                            
                            pdf_buffer = generator.create_invoice(complete_invoice_data)
                            
                            # Create filename
                            client_name = invoice_data.get('client', {}).get('name', 'Client')
                            invoice_num = invoice_data.get('invoice', {}).get('number', f'INV-{i+1}')
                            filename = f"invoice_{invoice_num}_{client_name.replace(' ', '_')}.pdf"
                            
                            generated_files.append({
                                'filename': filename,
                                'data': pdf_buffer.getvalue(),
                                'client': client_name
                            })
                            
                            progress_bar.progress((i + 1) / len(invoices))
                        
                        st.session_state.generated_bulk_files = generated_files
                        status_text.text("All invoices generated successfully!")
                        st.success(f"✅ Generated {len(generated_files)} invoices!")
                        
                    except Exception as e:
                        st.error(f"Error generating invoices: {str(e)}")
            
            with col_bulk2:
                if st.button("📊 Export Summary", use_container_width=True):
                    try:
                        # Create summary of all invoices
                        summary_data = []
                        for i, invoice in enumerate(invoices):
                            client = invoice.get('client', {})
                            inv_info = invoice.get('invoice', {})
                            total = sum(item.get('quantity', 0) * item.get('rate', 0) for item in invoice.get('items', []))
                            
                            summary_data.append({
                                'Invoice': inv_info.get('number', f'INV-{i+1}'),
                                'Client': client.get('name', 'Unknown'),
                                'Email': client.get('email', ''),
                                'Date': inv_info.get('date', ''),
                                'Items': len(invoice.get('items', [])),
                                'Total': total
                            })
                        
                        df_summary = pd.DataFrame(summary_data)
                        csv_summary = df_summary.to_csv(index=False)
                        
                        st.download_button(
                            label="📥 Download Summary CSV",
                            data=csv_summary,
                            file_name=f"bulk_invoices_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
                        
                    except Exception as e:
                        st.error(f"Error creating summary: {str(e)}")
            
            # Show download links for generated files
            if 'generated_bulk_files' in st.session_state:
                st.subheader("📥 Download Individual Invoices")
                
                for file_info in st.session_state.generated_bulk_files:
                    st.download_button(
                        label=f"📄 {file_info['filename']} ({file_info['client']})",
                        data=file_info['data'],
                        file_name=file_info['filename'],
                        mime="application/pdf",
                        use_container_width=True
                    )

def read_invoice_page():
    st.header("🔍 Read & Extract Invoice Data")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Upload Invoice")
        
        uploaded_file = st.file_uploader(
            "Drop any invoice here (PDF, PNG, JPG)",
            type=['pdf', 'png', 'jpg', 'jpeg'],
            help="Upload an invoice and I'll extract all the key information for you!"
        )
        
        # OCR/LLM Options
        with st.expander("Extraction Settings"):
            if ai_helper.is_available():
                extraction_method = st.selectbox(
                    "Extraction Method",
                    ["AI Enhanced (Recommended)", "OCR + AI", "OCR Only"],
                    help="AI Enhanced uses OCR + GPT for best results"
                )
            else:
                extraction_method = st.selectbox(
                    "Extraction Method", 
                    ["OCR Only"],
                    help="Add OpenAI API key in Settings to enable AI extraction"
                )
                st.info("💡 Enable AI extraction by adding your OpenAI API key in Settings")
            
            confidence_threshold = st.slider("Confidence Threshold", 0.0, 1.0, 0.7)
        
        if uploaded_file is not None:
            st.success(f"✅ File uploaded: {uploaded_file.name}")
            
            if st.button("🔍 Extract Data", type="primary", use_container_width=True):
                try:
                    with st.spinner("🤖 Analyzing invoice..."):
                        reader = InvoiceReader()
                        
                        # First extract with OCR
                        if "AI Enhanced" in extraction_method or "OCR + AI" in extraction_method:
                            # Use AI-enhanced extraction
                            ocr_text = reader.extract_text_with_ocr(uploaded_file)
                            if ai_helper.is_available():
                                ai_result = ai_helper.enhance_extraction(ocr_text)
                                if "error" not in ai_result:
                                    extracted_data = ai_result
                                else:
                                    # Fall back to regular OCR
                                    extracted_data = reader.extract_invoice_data(uploaded_file, "ocr only")
                            else:
                                extracted_data = reader.extract_invoice_data(uploaded_file, "ocr only")
                        else:
                            # Use regular OCR only
                            extracted_data = reader.extract_invoice_data(uploaded_file, "ocr only")
                    
                    st.session_state.extracted_data = extracted_data
                    st.success("✅ Data extracted successfully!")
                    
                except Exception as e:
                    st.error(f"Error extracting data: {str(e)}")
    
    with col2:
        st.subheader("Extracted Data")
        
        if 'extracted_data' in st.session_state:
            data = st.session_state.extracted_data
            
            # Display extracted information
            with st.expander("Vendor Information", expanded=True):
                col_v1, col_v2 = st.columns(2)
                with col_v1:
                    vendor_name = st.text_input("Vendor Name", value=data.get("vendor_name", ""))
                    vendor_address = st.text_area("Vendor Address", value=data.get("vendor_address", ""))
                with col_v2:
                    vendor_email = st.text_input("Vendor Email", value=data.get("vendor_email", ""))
                    vendor_phone = st.text_input("Vendor Phone", value=data.get("vendor_phone", ""))
            
            with st.expander("Invoice Details", expanded=True):
                col_i1, col_i2 = st.columns(2)
                with col_i1:
                    invoice_number = st.text_input("Invoice #", value=data.get("invoice_number", ""))
                    invoice_date = st.text_input("Date", value=data.get("invoice_date", ""))
                with col_i2:
                    due_date = st.text_input("Due Date", value=data.get("due_date", ""))
                    total_amount = st.text_input("Total Amount", value=str(data.get("total_amount", "")))
            
            # Line items table
            if "line_items" in data and data["line_items"]:
                st.subheader("Line Items")
                df = pd.DataFrame(data["line_items"])
                st.dataframe(df, use_container_width=True)
            
            # Export options
            st.subheader("Export Options")
            col_e1, col_e2, col_e3 = st.columns(3)
            
            with col_e1:
                if st.button("📊 Export to CSV", use_container_width=True):
                    csv_data = create_csv_export(data)
                    st.download_button(
                        "Download CSV",
                        csv_data,
                        f"invoice_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        "text/csv"
                    )
            
            with col_e2:
                if st.button("📋 Export to Excel", use_container_width=True):
                    try:
                        processor = CSVExcelProcessor()
                        excel_buffer = processor.export_to_excel(data)
                        
                        st.download_button(
                            "Download Excel",
                            excel_buffer.getvalue(),
                            f"invoice_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    except Exception as e:
                        st.error(f"Error exporting to Excel: {str(e)}")
            
            with col_e3:
                if st.button("📄 Export Summary", use_container_width=True):
                    summary_pdf = create_summary_pdf(data)
                    st.download_button(
                        "Download Summary",
                        summary_pdf,
                        f"invoice_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        "application/pdf"
                    )

def settings_page():
    st.header("⚙️ Settings")
    
    tab1, tab2 = st.tabs(["AI Models", "General"])
    
    with tab1:
        st.subheader("AI Model Configuration")
        
        # OpenAI API Key with persistence
        current_key = st.session_state.settings.get("openai_api_key", "")
        openai_key = st.text_input(
            "OpenAI API Key",
            value=current_key,
            type="password",
            help="For AI-powered invoice generation and data extraction"
        )
        
        # Model selection with persistence
        current_model = st.session_state.settings.get("extraction_model", "gpt-3.5-turbo")
        extraction_model = st.selectbox(
            "Default Extraction Model",
            ["gpt-3.5-turbo", "gpt-4", "gpt-3.5-turbo-16k"],
            index=["gpt-3.5-turbo", "gpt-4", "gpt-3.5-turbo-16k"].index(current_model)
        )
        
        # Save AI settings
        if st.button("💾 Save AI Settings", type="primary"):
            st.session_state.settings["openai_api_key"] = openai_key
            st.session_state.settings["extraction_model"] = extraction_model
            os.environ["OPENAI_API_KEY"] = openai_key
            
            # Reinitialize AI helper
            ai_helper._setup_openai()
            
            st.success("✅ AI settings saved!")
        
        # Show AI status
        if ai_helper.is_available():
            st.success("🤖 AI is ready and configured!")
        else:
            st.warning("⚠️ AI not available. Add OpenAI API key to enable AI features.")
        
        st.info("💡 **AI Features:** Generate invoice items, suggest client info, enhance data extraction")
    
    with tab2:
        st.subheader("General Settings")
        
        # Default currency with persistence
        current_currency = st.session_state.settings.get("default_currency", "USD")
        default_currency = st.selectbox(
            "Default Currency",
            ["USD", "EUR", "GBP", "CAD", "AUD"],
            index=["USD", "EUR", "GBP", "CAD", "AUD"].index(current_currency)
        )
        
        # File format preferences with persistence
        current_format = st.session_state.settings.get("export_format", "Excel (.xlsx)")
        export_format = st.selectbox(
            "Default Export Format",
            ["Excel (.xlsx)", "CSV (.csv)", "Both"],
            index=["Excel (.xlsx)", "CSV (.csv)", "Both"].index(current_format)
        )
        
        # OCR settings
        st.subheader("OCR Settings")
        current_language = st.session_state.settings.get("ocr_language", "English")
        ocr_language = st.selectbox(
            "OCR Language",
            ["English", "Multi-language"],
            index=["English", "Multi-language"].index(current_language)
        )
        
        current_threshold = st.session_state.settings.get("confidence_threshold", 0.7)
        confidence_threshold = st.slider(
            "OCR Confidence Threshold",
            0.0, 1.0, current_threshold,
            help="Higher values = more strict OCR accuracy"
        )
        
        # Save general settings
        if st.button("💾 Save General Settings", type="primary"):
            st.session_state.settings.update({
                "default_currency": default_currency,
                "export_format": export_format,
                "ocr_language": ocr_language,
                "confidence_threshold": confidence_threshold
            })
            st.success("✅ General settings saved!")
        
        # Show current settings
        st.subheader("Current Settings")
        st.json(st.session_state.settings)

def create_csv_export(data):
    """Create CSV export of extracted invoice data"""
    try:
        # Create main invoice data
        main_data = {
            'Date Processed': [datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
            'Vendor Name': [data.get('vendor_name', '')],
            'Vendor Address': [data.get('vendor_address', '')],
            'Vendor Email': [data.get('vendor_email', '')],
            'Vendor Phone': [data.get('vendor_phone', '')],
            'Invoice Number': [data.get('invoice_number', '')],
            'Invoice Date': [data.get('invoice_date', '')],
            'Due Date': [data.get('due_date', '')],
            'Total Amount': [data.get('total_amount', '')],
            'Line Items Count': [len(data.get('line_items', []))]
        }
        
        df = pd.DataFrame(main_data)
        csv_content = df.to_csv(index=False)
        
        # Add line items if available
        if data.get('line_items'):
            csv_content += "\n\nLine Items:\n"
            line_items_df = pd.DataFrame(data['line_items'])
            csv_content += line_items_df.to_csv(index=False)
        
        return csv_content
        
    except Exception as e:
        print(f"Failed to create CSV export: {e}")
        return "Error creating CSV export"

def create_summary_pdf(data):
    """Create PDF summary of extracted data"""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        story.append(Paragraph("Invoice Data Summary", styles['Title']))
        story.append(Spacer(1, 20))
        
        # Invoice details
        story.append(Paragraph("Invoice Information", styles['Heading2']))
        story.append(Paragraph(f"Vendor: {data.get('vendor_name', 'N/A')}", styles['Normal']))
        story.append(Paragraph(f"Email: {data.get('vendor_email', 'N/A')}", styles['Normal']))
        story.append(Paragraph(f"Invoice Number: {data.get('invoice_number', 'N/A')}", styles['Normal']))
        story.append(Paragraph(f"Total Amount: {data.get('total_amount', 'N/A')}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Line items
        if data.get('line_items'):
            story.append(Paragraph("Line Items", styles['Heading2']))
            for i, item in enumerate(data['line_items']):
                story.append(Paragraph(f"{i+1}. {item.get('description', 'N/A')} - Qty: {item.get('quantity', 'N/A')} - Amount: {item.get('amount', 'N/A')}", styles['Normal']))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
        
    except Exception as e:
        print(f"Failed to create PDF summary: {e}")
        return b"Error creating PDF summary"

if __name__ == "__main__":
    main() 