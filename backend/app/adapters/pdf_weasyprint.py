"""
WeasyPrint PDF service adapter.
"""

import logging
from typing import Dict

from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

from ..core.interfaces import PDFService

logger = logging.getLogger(__name__)


class WeasyPrintPDFService:
    """WeasyPrint-based PDF generation service."""
    
    def __init__(self):
        self.font_config = FontConfiguration()
    
    def _render_html_template(self, template: str, data: Dict[str, any]) -> str:
        """Render HTML template with data."""
        
        # Simple template system (in production, use Jinja2 or similar)
        templates = {
            "certificate": f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Training Certificate</title>
                <style>
                    @page {{
                        size: A4 landscape;
                        margin: 2cm;
                    }}
                    body {{
                        font-family: 'Arial', sans-serif;
                        text-align: center;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        margin: 0;
                        padding: 40px;
                        height: 100vh;
                        display: flex;
                        flex-direction: column;
                        justify-content: center;
                    }}
                    .certificate {{
                        background: white;
                        color: #333;
                        padding: 60px;
                        border-radius: 20px;
                        box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                        max-width: 800px;
                        margin: 0 auto;
                    }}
                    .header {{
                        border-bottom: 3px solid #667eea;
                        padding-bottom: 20px;
                        margin-bottom: 40px;
                    }}
                    .title {{
                        font-size: 48px;
                        font-weight: bold;
                        color: #667eea;
                        margin: 0;
                    }}
                    .subtitle {{
                        font-size: 18px;
                        color: #666;
                        margin: 10px 0 0 0;
                    }}
                    .recipient {{
                        font-size: 36px;
                        font-weight: bold;
                        color: #333;
                        margin: 40px 0;
                    }}
                    .course {{
                        font-size: 24px;
                        color: #667eea;
                        font-style: italic;
                        margin: 20px 0;
                    }}
                    .details {{
                        display: flex;
                        justify-content: space-between;
                        margin: 40px 0;
                        font-size: 16px;
                        color: #666;
                    }}
                    .score {{
                        font-size: 20px;
                        font-weight: bold;
                        color: #28a745;
                    }}
                    .footer {{
                        margin-top: 40px;
                        padding-top: 20px;
                        border-top: 2px solid #eee;
                        font-size: 14px;
                        color: #999;
                    }}
                </style>
            </head>
            <body>
                <div class="certificate">
                    <div class="header">
                        <h1 class="title">Certificate of Completion</h1>
                        <p class="subtitle">Upper Echelon Hub Training Program</p>
                    </div>
                    
                    <p style="font-size: 18px; margin: 20px 0;">This certifies that</p>
                    
                    <div class="recipient">{data.get('user_name', 'Unknown User')}</div>
                    
                    <p style="font-size: 18px; margin: 20px 0;">has successfully completed</p>
                    
                    <div class="course">{data.get('module_title', 'Training Module')}</div>
                    
                    <div class="details">
                        <div>
                            <strong>Date Completed:</strong><br>
                            {data.get('completion_date', 'Unknown')}
                        </div>
                        <div>
                            <strong>Duration:</strong><br>
                            {data.get('duration', 'N/A')} minutes
                        </div>
                        <div>
                            <strong>Score:</strong><br>
                            <span class="score">{data.get('score', 0)}%</span>
                        </div>
                    </div>
                    
                    <div class="footer">
                        <p>Certificate ID: {data.get('certificate_id', 'N/A')}</p>
                        <p>Issued by Upper Echelon Hub Training System</p>
                    </div>
                </div>
            </body>
            </html>
            """,
            
            "report": f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>{data.get('title', 'Report')}</title>
                <style>
                    @page {{
                        size: A4;
                        margin: 2cm;
                        @bottom-right {{
                            content: "Page " counter(page) " of " counter(pages);
                        }}
                    }}
                    body {{
                        font-family: 'Arial', sans-serif;
                        line-height: 1.6;
                        color: #333;
                        margin: 0;
                        padding: 0;
                    }}
                    .header {{
                        text-align: center;
                        border-bottom: 2px solid #667eea;
                        padding-bottom: 20px;
                        margin-bottom: 30px;
                    }}
                    .title {{
                        font-size: 28px;
                        font-weight: bold;
                        color: #667eea;
                        margin: 0;
                    }}
                    .subtitle {{
                        font-size: 16px;
                        color: #666;
                        margin: 10px 0 0 0;
                    }}
                    .section {{
                        margin: 30px 0;
                    }}
                    .section h2 {{
                        font-size: 20px;
                        color: #667eea;
                        border-bottom: 1px solid #eee;
                        padding-bottom: 5px;
                    }}
                    .metric {{
                        display: inline-block;
                        background: #f8f9fa;
                        padding: 15px;
                        margin: 10px;
                        border-radius: 8px;
                        text-align: center;
                        min-width: 120px;
                    }}
                    .metric-value {{
                        font-size: 24px;
                        font-weight: bold;
                        color: #667eea;
                    }}
                    .metric-label {{
                        font-size: 12px;
                        color: #666;
                        text-transform: uppercase;
                    }}
                    table {{
                        width: 100%;
                        border-collapse: collapse;
                        margin: 20px 0;
                    }}
                    th, td {{
                        padding: 12px;
                        text-align: left;
                        border-bottom: 1px solid #eee;
                    }}
                    th {{
                        background: #f8f9fa;
                        font-weight: bold;
                        color: #667eea;
                    }}
                    .footer {{
                        margin-top: 50px;
                        padding-top: 20px;
                        border-top: 1px solid #eee;
                        font-size: 12px;
                        color: #999;
                        text-align: center;
                    }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1 class="title">{data.get('title', 'Report')}</h1>
                    <p class="subtitle">Generated on {data.get('generated_date', 'Unknown')}</p>
                </div>
                
                <div class="section">
                    <h2>Summary</h2>
                    <div style="text-align: center;">
                        {' '.join([f'<div class="metric"><div class="metric-value">{metric.get("value", 0)}</div><div class="metric-label">{metric.get("label", "Metric")}</div></div>' for metric in data.get('metrics', [])])}
                    </div>
                </div>
                
                {f'<div class="section"><h2>Details</h2><p>{data.get("content", "No additional details available.")}</p></div>' if data.get('content') else ''}
                
                {f'''
                <div class="section">
                    <h2>Data Table</h2>
                    <table>
                        <thead>
                            <tr>
                                {"".join([f"<th>{col}</th>" for col in data.get('table', {}).get('headers', [])])}
                            </tr>
                        </thead>
                        <tbody>
                            {"".join([f"<tr>{''.join([f'<td>{cell}</td>' for cell in row])}</tr>" for row in data.get('table', {}).get('rows', [])])}
                        </tbody>
                    </table>
                </div>
                ''' if data.get('table') else ''}
                
                <div class="footer">
                    <p>Generated by UE Hub Reporting System</p>
                    <p>Report ID: {data.get('report_id', 'N/A')}</p>
                </div>
            </body>
            </html>
            """
        }
        
        template_html = templates.get(template, f"<html><body><h1>Unknown template: {template}</h1></body></html>")
        return template_html
    
    async def render_certificate(
        self, 
        template: str, 
        data: Dict[str, any]
    ) -> bytes:
        """Render a certificate PDF from template and data."""
        try:
            html_content = self._render_html_template(template, data)
            
            # Create PDF
            html_doc = HTML(string=html_content)
            pdf_bytes = html_doc.write_pdf(font_config=self.font_config)
            
            logger.info(f"Generated certificate PDF for {data.get('user_name', 'unknown user')}")
            return pdf_bytes
        
        except Exception as e:
            logger.error(f"Error generating certificate PDF: {e}")
            raise
    
    async def render_report(
        self, 
        template: str, 
        data: Dict[str, any]
    ) -> bytes:
        """Render a report PDF from template and data."""
        try:
            html_content = self._render_html_template(template, data)
            
            # Create PDF
            html_doc = HTML(string=html_content)
            pdf_bytes = html_doc.write_pdf(font_config=self.font_config)
            
            logger.info(f"Generated report PDF: {data.get('title', 'Unknown Report')}")
            return pdf_bytes
        
        except Exception as e:
            logger.error(f"Error generating report PDF: {e}")
            raise
    
    async def render_custom_pdf(
        self,
        html_content: str,
        css_content: str = None
    ) -> bytes:
        """Render custom PDF from HTML and CSS."""
        try:
            html_doc = HTML(string=html_content)
            
            if css_content:
                css_doc = CSS(string=css_content)
                pdf_bytes = html_doc.write_pdf(stylesheets=[css_doc], font_config=self.font_config)
            else:
                pdf_bytes = html_doc.write_pdf(font_config=self.font_config)
            
            logger.info("Generated custom PDF")
            return pdf_bytes
        
        except Exception as e:
            logger.error(f"Error generating custom PDF: {e}")
            raise
