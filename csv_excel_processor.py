import pandas as pd
import io
from typing import Dict, List, Any, Optional
from datetime import datetime
import xlsxwriter

class CSVExcelProcessor:
    def __init__(self):
        self.supported_formats = ['csv', 'xlsx', 'xls']
    
    def read_invoice_data_from_file(self, uploaded_file) -> Dict[str, Any]:
        """
        Read invoice data from uploaded CSV/Excel file
        Expected format:
        - First sheet/section: Business info, Client info, Invoice details
        - Second sheet/section: Line items
        """
        try:
            file_extension = uploaded_file.name.lower().split('.')[-1]
            
            if file_extension not in self.supported_formats:
                raise ValueError(f"Unsupported file format: {file_extension}")
            
            # Read the file
            if file_extension == 'csv':
                df = pd.read_csv(uploaded_file)
                return self._process_csv_data(df)
            else:
                # Read Excel file - try to get multiple sheets
                excel_data = pd.read_excel(uploaded_file, sheet_name=None)
                return self._process_excel_data(excel_data)
                
        except Exception as e:
            raise Exception(f"Error reading file: {str(e)}")
    
    def _process_csv_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Process CSV data into invoice format"""
        invoice_data = {
            "business": {},
            "client": {},
            "invoice": {},
            "items": [],
            "notes": "",
            "tax_rate": 0.0
        }
        
        try:
            # Look for specific sections or patterns in the CSV
            # Method 1: Try structured format with headers
            if self._is_structured_format(df):
                return self._parse_structured_format(df)
            
            # Method 2: Try line items format
            elif self._is_line_items_format(df):
                return self._parse_line_items_format(df)
            
            # Method 3: Generic parsing
            else:
                return self._parse_generic_format(df)
                
        except Exception as e:
            raise Exception(f"Error processing CSV data: {str(e)}")
    
    def _process_excel_data(self, excel_data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """Process Excel data with multiple sheets"""
        invoice_data = {
            "business": {},
            "client": {},
            "invoice": {},
            "items": [],
            "notes": "",
            "tax_rate": 0.0
        }
        
        try:
            # If multiple sheets, try to parse them separately
            if len(excel_data) > 1:
                # Look for specific sheet names
                info_sheet = None
                items_sheet = None
                
                for sheet_name, df in excel_data.items():
                    sheet_lower = sheet_name.lower()
                    if any(word in sheet_lower for word in ['info', 'details', 'header', 'main']):
                        info_sheet = df
                    elif any(word in sheet_lower for word in ['items', 'lines', 'products', 'services']):
                        items_sheet = df
                
                # If we found specific sheets, process them
                if info_sheet is not None and items_sheet is not None:
                    # Process info sheet for business/client/invoice data
                    info_data = self._parse_info_sheet(info_sheet)
                    invoice_data.update(info_data)
                    
                    # Process items sheet
                    items = self._parse_items_sheet(items_sheet)
                    invoice_data["items"] = items
                    
                    return invoice_data
            
            # Fall back to processing first sheet
            first_sheet = list(excel_data.values())[0]
            return self._process_csv_data(first_sheet)
            
        except Exception as e:
            raise Exception(f"Error processing Excel data: {str(e)}")
    
    def _is_structured_format(self, df: pd.DataFrame) -> bool:
        """Check if CSV has structured format with clear sections"""
        # Look for key indicators
        text_content = ' '.join(df.astype(str).values.flatten()).lower()
        indicators = ['business name', 'client name', 'invoice number', 'description', 'quantity', 'rate']
        return sum(indicator in text_content for indicator in indicators) >= 3
    
    def _is_line_items_format(self, df: pd.DataFrame) -> bool:
        """Check if CSV is primarily line items"""
        columns = [col.lower() for col in df.columns]
        line_item_indicators = ['description', 'quantity', 'qty', 'rate', 'price', 'amount']
        return sum(indicator in ' '.join(columns) for indicator in line_item_indicators) >= 2
    
    def _parse_structured_format(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Parse structured CSV with clear sections"""
        invoice_data = {
            "business": {"name": "", "address": "", "email": "", "phone": ""},
            "client": {"name": "", "address": "", "email": ""},
            "invoice": {"number": "", "date": "", "due_date": "", "currency": "USD"},
            "items": [],
            "notes": "",
            "tax_rate": 0.0
        }
        
        # Convert dataframe to text for pattern matching
        text_data = []
        for _, row in df.iterrows():
            text_data.extend([str(val) for val in row.values if pd.notna(val)])
        
        # Extract business info
        for i, item in enumerate(text_data):
            item_lower = str(item).lower()
            if 'business name' in item_lower and i + 1 < len(text_data):
                invoice_data["business"]["name"] = text_data[i + 1]
            elif 'business email' in item_lower and i + 1 < len(text_data):
                invoice_data["business"]["email"] = text_data[i + 1]
            elif 'business phone' in item_lower and i + 1 < len(text_data):
                invoice_data["business"]["phone"] = text_data[i + 1]
            elif 'client name' in item_lower and i + 1 < len(text_data):
                invoice_data["client"]["name"] = text_data[i + 1]
            elif 'client email' in item_lower and i + 1 < len(text_data):
                invoice_data["client"]["email"] = text_data[i + 1]
            elif 'invoice number' in item_lower and i + 1 < len(text_data):
                invoice_data["invoice"]["number"] = text_data[i + 1]
        
        # Look for line items table
        items = self._extract_line_items_from_df(df)
        invoice_data["items"] = items
        
        return invoice_data
    
    def _parse_line_items_format(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Parse CSV that's primarily line items"""
        invoice_data = {
            "business": {"name": "Your Business", "address": "", "email": "", "phone": ""},
            "client": {"name": "Client", "address": "", "email": ""},
            "invoice": {
                "number": f"INV-{datetime.now().strftime('%Y%m%d')}",
                "date": datetime.now().strftime('%Y-%m-%d'),
                "due_date": "",
                "currency": "USD"
            },
            "items": [],
            "notes": "",
            "tax_rate": 0.0
        }
        
        # Extract line items
        items = self._extract_line_items_from_df(df)
        invoice_data["items"] = items
        
        return invoice_data
    
    def _parse_generic_format(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generic parsing for unknown format"""
        invoice_data = {
            "business": {"name": "Your Business", "address": "", "email": "", "phone": ""},
            "client": {"name": "Client", "address": "", "email": ""},
            "invoice": {
                "number": f"INV-{datetime.now().strftime('%Y%m%d')}",
                "date": datetime.now().strftime('%Y-%m-%d'),
                "due_date": "",
                "currency": "USD"
            },
            "items": [],
            "notes": "Imported from uploaded file",
            "tax_rate": 0.0
        }
        
        # Try to extract line items
        items = self._extract_line_items_from_df(df)
        if items:
            invoice_data["items"] = items
        else:
            # Create default item from first row
            if not df.empty:
                first_row = df.iloc[0]
                invoice_data["items"] = [{
                    "description": str(first_row.iloc[0]) if len(first_row) > 0 else "Service",
                    "quantity": 1,
                    "rate": float(first_row.iloc[1]) if len(first_row) > 1 and pd.notna(first_row.iloc[1]) else 100.0
                }]
        
        return invoice_data
    
    def _extract_line_items_from_df(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Extract line items from dataframe"""
        items = []
        
        # Map common column names
        column_mapping = {
            'description': ['description', 'item', 'service', 'product', 'details'],
            'quantity': ['quantity', 'qty', 'amount', 'units'],
            'rate': ['rate', 'price', 'unit_price', 'cost', 'amount'],
            'total': ['total', 'line_total', 'amount']
        }
        
        # Find matching columns
        columns = {key: None for key in column_mapping.keys()}
        df_columns_lower = [col.lower() for col in df.columns]
        
        for col_type, variations in column_mapping.items():
            for variation in variations:
                for i, df_col in enumerate(df_columns_lower):
                    if variation in df_col:
                        columns[col_type] = df.columns[i]
                        break
                if columns[col_type]:
                    break
        
        # Extract items
        for _, row in df.iterrows():
            if pd.isna(row).all():  # Skip empty rows
                continue
                
            item = {
                "description": "",
                "quantity": 1,
                "rate": 0.0
            }
            
            # Map values
            if columns['description']:
                item["description"] = str(row[columns['description']]) if pd.notna(row[columns['description']]) else ""
            
            if columns['quantity']:
                try:
                    item["quantity"] = float(row[columns['quantity']]) if pd.notna(row[columns['quantity']]) else 1
                except (ValueError, TypeError):
                    item["quantity"] = 1
            
            if columns['rate']:
                try:
                    item["rate"] = float(row[columns['rate']]) if pd.notna(row[columns['rate']]) else 0.0
                except (ValueError, TypeError):
                    item["rate"] = 0.0
            
            # Only add if we have some content
            if item["description"] or item["rate"] > 0:
                items.append(item)
        
        return items
    
    def _parse_info_sheet(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Parse info sheet for business/client/invoice data"""
        data = {
            "business": {"name": "", "address": "", "email": "", "phone": ""},
            "client": {"name": "", "address": "", "email": ""},
            "invoice": {"number": "", "date": "", "due_date": "", "currency": "USD"},
            "notes": "",
            "tax_rate": 0.0
        }
        
        # Convert to key-value pairs
        for _, row in df.iterrows():
            if len(row) >= 2:
                key = str(row.iloc[0]).lower()
                value = str(row.iloc[1]) if pd.notna(row.iloc[1]) else ""
                
                # Map to appropriate fields
                if 'business' in key and 'name' in key:
                    data["business"]["name"] = value
                elif 'business' in key and 'email' in key:
                    data["business"]["email"] = value
                elif 'business' in key and 'phone' in key:
                    data["business"]["phone"] = value
                elif 'client' in key and 'name' in key:
                    data["client"]["name"] = value
                elif 'client' in key and 'email' in key:
                    data["client"]["email"] = value
                elif 'invoice' in key and 'number' in key:
                    data["invoice"]["number"] = value
                elif 'tax' in key:
                    try:
                        data["tax_rate"] = float(value)
                    except (ValueError, TypeError):
                        pass
        
        return data
    
    def _parse_items_sheet(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Parse items sheet"""
        return self._extract_line_items_from_df(df)
    
    def export_to_excel(self, data: Dict[str, Any], filename: Optional[str] = None) -> io.BytesIO:
        """Export extracted invoice data to Excel format"""
        if filename is None:
            filename = f"invoice_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        # Create BytesIO buffer
        buffer = io.BytesIO()
        
        # Create workbook and worksheets
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            # Main invoice info
            main_data = {
                'Field': [
                    'Date Processed',
                    'Vendor Name',
                    'Vendor Address', 
                    'Vendor Email',
                    'Vendor Phone',
                    'Invoice Number',
                    'Invoice Date',
                    'Due Date',
                    'Total Amount',
                    'Currency'
                ],
                'Value': [
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    data.get('vendor_name', ''),
                    data.get('vendor_address', ''),
                    data.get('vendor_email', ''),
                    data.get('vendor_phone', ''),
                    data.get('invoice_number', ''),
                    data.get('invoice_date', ''),
                    data.get('due_date', ''),
                    data.get('total_amount', ''),
                    'USD'  # Default currency
                ]
            }
            
            main_df = pd.DataFrame(main_data)
            main_df.to_excel(writer, sheet_name='Invoice Info', index=False)
            
            # Line items if available
            if data.get('line_items'):
                items_df = pd.DataFrame(data['line_items'])
                items_df.to_excel(writer, sheet_name='Line Items', index=False)
            
            # Get workbook and worksheets for formatting
            workbook = writer.book
            info_worksheet = writer.sheets['Invoice Info']
            
            # Format headers
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#4F81BD',
                'font_color': 'white',
                'border': 1
            })
            
            # Apply header formatting
            for col_num, value in enumerate(main_df.columns.values):
                info_worksheet.write(0, col_num, value, header_format)
            
            # Auto-adjust column widths
            info_worksheet.set_column('A:A', 20)
            info_worksheet.set_column('B:B', 30)
            
            if 'Line Items' in writer.sheets:
                items_worksheet = writer.sheets['Line Items']
                items_worksheet.set_column('A:A', 30)  # Description
                items_worksheet.set_column('B:D', 15)  # Quantity, Rate, Amount
        
        buffer.seek(0)
        return buffer
    
    def process_bulk_invoices(self, uploaded_file) -> List[Dict[str, Any]]:
        """
        Process file to extract multiple invoice records
        Returns a list of invoice data dictionaries
        """
        try:
            file_extension = uploaded_file.name.lower().split('.')[-1]
            
            if file_extension not in self.supported_formats:
                raise ValueError(f"Unsupported file format: {file_extension}")
            
            # Read the file
            if file_extension == 'csv':
                df = pd.read_csv(uploaded_file)
            else:
                # For Excel, read first sheet for bulk processing
                df = pd.read_excel(uploaded_file, sheet_name=0)
            
            # Detect if this is multiple invoices or single invoice
            return self._extract_multiple_invoices(df)
                
        except Exception as e:
            raise Exception(f"Error processing bulk file: {str(e)}")
    
    def _extract_multiple_invoices(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Extract multiple invoice records from a dataframe"""
        invoices = []
        
        # Method 1: Group by client name (if multiple clients)
        if 'client' in ' '.join(df.columns).lower() or 'customer' in ' '.join(df.columns).lower():
            # Find client column
            client_col = None
            for col in df.columns:
                if 'client' in col.lower() or 'customer' in col.lower():
                    client_col = col
                    break
            
            if client_col:
                # Group by unique clients
                unique_clients = df[client_col].dropna().unique()
                
                for client in unique_clients:
                    client_rows = df[df[client_col] == client]
                    invoice_data = self._create_invoice_from_rows(client_rows, client)
                    if invoice_data:
                        invoices.append(invoice_data)
                
                return invoices
        
        # Method 2: Group by invoice number (if multiple invoice numbers)
        invoice_num_col = None
        for col in df.columns:
            if 'invoice' in col.lower() and ('number' in col.lower() or 'num' in col.lower() or '#' in col):
                invoice_num_col = col
                break
        
        if invoice_num_col:
            unique_invoices = df[invoice_num_col].dropna().unique()
            
            for inv_num in unique_invoices:
                inv_rows = df[df[invoice_num_col] == inv_num]
                invoice_data = self._create_invoice_from_rows(inv_rows, invoice_number=inv_num)
                if invoice_data:
                    invoices.append(invoice_data)
            
            return invoices
        
        # Method 3: Treat each row as a separate line item for one invoice
        # Group by reasonable chunks (e.g., every 10 rows or based on empty rows)
        return [self._process_csv_data(df)]
    
    def _create_invoice_from_rows(self, rows: pd.DataFrame, client_name: str = None, invoice_number: str = None) -> Dict[str, Any]:
        """Create invoice data from a group of rows"""
        if rows.empty:
            return None
        
        invoice_data = {
            "business": {"name": "Your Business", "address": "", "email": "", "phone": ""},
            "client": {"name": client_name or "Client", "address": "", "email": ""},
            "invoice": {
                "number": invoice_number or f"INV-{datetime.now().strftime('%Y%m%d')}-{len(str(client_name or ''))[:3]}",
                "date": datetime.now().strftime('%Y-%m-%d'),
                "due_date": "",
                "currency": "USD"
            },
            "items": [],
            "notes": "",
            "tax_rate": 0.0
        }
        
        # Extract client information from first row
        first_row = rows.iloc[0]
        
        # Look for client email, address columns
        for col in rows.columns:
            col_lower = col.lower()
            if 'email' in col_lower and 'client' in col_lower:
                invoice_data["client"]["email"] = str(first_row[col]) if pd.notna(first_row[col]) else ""
            elif 'address' in col_lower and 'client' in col_lower:
                invoice_data["client"]["address"] = str(first_row[col]) if pd.notna(first_row[col]) else ""
        
        # Extract line items
        items = self._extract_line_items_from_df(rows)
        invoice_data["items"] = items
        
        return invoice_data

# Testing and usage example
if __name__ == "__main__":
    processor = CSVExcelProcessor()
    print("CSV/Excel Processor initialized successfully!") 