from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from io import BytesIO
from datetime import datetime
import os

class InvoiceGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Setup custom styles for the invoice"""
        self.styles.add(ParagraphStyle(
            name='CompanyName',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=12,
            textColor=colors.HexColor('#2E3440')
        ))
        
        self.styles.add(ParagraphStyle(
            name='InvoiceTitle',
            parent=self.styles['Heading1'],
            fontSize=20,
            spaceAfter=20,
            alignment=TA_RIGHT,
            textColor=colors.HexColor('#5E81AC')
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceBefore=20,
            spaceAfter=10,
            textColor=colors.HexColor('#434C5E')
        ))
        
        self.styles.add(ParagraphStyle(
            name='Address',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            leading=12
        ))
        
        self.styles.add(ParagraphStyle(
            name='TableHeader',
            parent=self.styles['Normal'],
            fontSize=11,
            alignment=TA_CENTER,
            textColor=colors.white
        ))
    
    def create_invoice(self, data):
        """Create a professional invoice PDF"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=inch,
            leftMargin=inch,
            topMargin=inch,
            bottomMargin=inch
        )
        
        story = []
        
        # Header section
        story.extend(self._create_header(data))
        
        # Business and client info
        story.extend(self._create_business_client_info(data))
        
        # Invoice details
        story.extend(self._create_invoice_details(data))
        
        # Line items table
        story.extend(self._create_line_items_table(data))
        
        # Totals section
        story.extend(self._create_totals_section(data))
        
        # Notes section
        story.extend(self._create_notes_section(data))
        
        # Footer
        story.extend(self._create_footer(data))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def _create_header(self, data):
        """Create the invoice header"""
        elements = []
        
        # Company name and Invoice title in a table
        header_data = [
            [
                Paragraph(data['business']['name'], self.styles['CompanyName']),
                Paragraph('INVOICE', self.styles['InvoiceTitle'])
            ]
        ]
        
        header_table = Table(header_data, colWidths=[3*inch, 3*inch])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ]))
        
        elements.append(header_table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_business_client_info(self, data):
        """Create business and client information section"""
        elements = []
        
        # Create two-column layout for business and client info
        info_data = [
            [
                Paragraph('<b>From:</b>', self.styles['SectionHeader']),
                Paragraph('<b>Bill To:</b>', self.styles['SectionHeader'])
            ],
            [
                Paragraph(f"<b>{data['business']['name']}</b><br/>{data['business']['address']}<br/>{data['business']['email']}<br/>{data['business']['phone']}", self.styles['Address']),
                Paragraph(f"<b>{data['client']['name']}</b><br/>{data['client']['address']}<br/>{data['client']['email']}", self.styles['Address'])
            ]
        ]
        
        info_table = Table(info_data, colWidths=[3*inch, 3*inch])
        info_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ]))
        
        elements.append(info_table)
        elements.append(Spacer(1, 30))
        
        return elements
    
    def _create_invoice_details(self, data):
        """Create invoice details section"""
        elements = []
        
        # Invoice details table
        details_data = [
            ['Invoice Number:', data['invoice']['number']],
            ['Invoice Date:', data['invoice']['date']],
            ['Due Date:', data['invoice']['due_date']],
            ['Currency:', data['invoice']['currency']]
        ]
        
        details_table = Table(details_data, colWidths=[1.5*inch, 2*inch])
        details_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E0E0E0')),
        ]))
        
        # Right-align the details table
        details_wrapper = Table([[details_table]], colWidths=[6*inch])
        details_wrapper.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'RIGHT'),
        ]))
        
        elements.append(details_wrapper)
        elements.append(Spacer(1, 30))
        
        return elements
    
    def _create_line_items_table(self, data):
        """Create the line items table"""
        elements = []
        
        # Table headers
        headers = ['Description', 'Quantity', 'Rate', 'Amount']
        table_data = [headers]
        
        # Add line items
        subtotal = 0
        for item in data['items']:
            amount = float(item['quantity']) * float(item['rate'])
            subtotal += amount
            table_data.append([
                item['description'],
                str(item['quantity']),
                f"{data['invoice']['currency']} {float(item['rate']):.2f}",
                f"{data['invoice']['currency']} {amount:.2f}"
            ])
        
        # Create table
        items_table = Table(table_data, colWidths=[3*inch, 1*inch, 1*inch, 1*inch])
        items_table.setStyle(TableStyle([
            # Header row styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#5E81AC')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            
            # Data rows styling
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            
            # Alternating row colors
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8F9FA')]),
            
            # Grid lines
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E0E0E0')),
            
            # Padding
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(items_table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_totals_section(self, data):
        """Create the totals section"""
        elements = []
        
        # Calculate totals
        subtotal = sum(float(item['quantity']) * float(item['rate']) for item in data['items'])
        tax_rate = data.get('tax_rate', 0)
        tax_amount = subtotal * (tax_rate / 100)
        total = subtotal + tax_amount
        
        currency = data['invoice']['currency']
        
        # Totals data
        totals_data = [
            ['Subtotal:', f"{currency} {subtotal:.2f}"],
        ]
        
        if tax_rate > 0:
            totals_data.append([f'Tax ({tax_rate}%):', f"{currency} {tax_amount:.2f}"])
        
        totals_data.append(['Total:', f"{currency} {total:.2f}"])
        
        # Create totals table
        totals_table = Table(totals_data, colWidths=[1.5*inch, 1.5*inch])
        totals_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -2), 'Helvetica'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('FONTSIZE', (0, -1), (-1, -1), 12),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.HexColor('#2E3440')),
            ('LINEBELOW', (0, -1), (-1, -1), 2, colors.HexColor('#5E81AC')),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        
        # Right-align the totals table
        totals_wrapper = Table([[totals_table]], colWidths=[6*inch])
        totals_wrapper.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'RIGHT'),
        ]))
        
        elements.append(totals_wrapper)
        elements.append(Spacer(1, 30))
        
        return elements
    
    def _create_notes_section(self, data):
        """Create the notes section"""
        elements = []
        
        if data.get('notes'):
            elements.append(Paragraph('<b>Notes:</b>', self.styles['SectionHeader']))
            elements.append(Paragraph(data['notes'], self.styles['Normal']))
            elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_footer(self, data):
        """Create the invoice footer"""
        elements = []
        
        # Footer text
        footer_text = f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        footer_style = ParagraphStyle(
            name='Footer',
            parent=self.styles['Normal'],
            fontSize=8,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#888888')
        )
        
        elements.append(Spacer(1, 40))
        elements.append(Paragraph(footer_text, footer_style))
        
        return elements

# Usage example and testing
if __name__ == "__main__":
    # Test data
    test_data = {
        "business": {
            "name": "Your Business Name",
            "address": "123 Business Street\nCity, State 12345",
            "email": "contact@yourbusiness.com",
            "phone": "+1 (555) 123-4567"
        },
        "client": {
            "name": "Client Company Inc.",
            "address": "456 Client Avenue\nCity, State 67890",
            "email": "billing@clientcompany.com"
        },
        "invoice": {
            "number": "INV-20241201",
            "date": "2024-12-01",
            "due_date": "2024-12-31",
            "currency": "USD"
        },
        "items": [
            {"description": "Web Development Services", "quantity": 40, "rate": 75.00},
            {"description": "UI/UX Design", "quantity": 20, "rate": 85.00},
            {"description": "Project Management", "quantity": 10, "rate": 90.00}
        ],
        "notes": "Thank you for your business! Payment is due within 30 days.",
        "tax_rate": 8.25
    }
    
    generator = InvoiceGenerator()
    pdf_buffer = generator.create_invoice(test_data)
    
    # Save test invoice
    with open("test_invoice.pdf", "wb") as f:
        f.write(pdf_buffer.getvalue())
    
    print("Test invoice generated successfully!") 