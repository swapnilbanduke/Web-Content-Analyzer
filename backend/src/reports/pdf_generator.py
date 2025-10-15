"""
PDF Report Generator

Converts HTML reports to PDF format using WeasyPrint.
Handles page breaks, styling, and embedded images.
"""

from typing import Optional
import base64
from io import BytesIO


class PDFGenerator:
    """
    PDF report generator.
    
    Converts HTML reports to professional PDF documents.
    """
    
    def __init__(self):
        self.weasyprint_available = False
        self.xhtml2pdf_available = False
        self.pdf_library = None
        
        # Try WeasyPrint first (better quality, but requires GTK on Windows)
        try:
            import weasyprint
            self.weasyprint = weasyprint
            self.weasyprint_available = True
            self.pdf_library = 'weasyprint'
        except (ImportError, OSError) as e:
            # WeasyPrint not available or GTK missing
            pass
        
        # Fallback to xhtml2pdf (works on Windows without GTK)
        if not self.weasyprint_available:
            try:
                from xhtml2pdf import pisa
                self.pisa = pisa
                self.xhtml2pdf_available = True
                self.pdf_library = 'xhtml2pdf'
            except ImportError:
                pass
    
    async def generate_pdf(
        self,
        html_content: str,
        base_url: Optional[str] = None
    ) -> bytes:
        """
        Generate PDF from HTML content.
        
        Args:
            html_content: HTML content to convert
            base_url: Base URL for resolving relative paths
            
        Returns:
            PDF as bytes
        """
        # Check if any PDF library is available
        if not self.weasyprint_available and not self.xhtml2pdf_available:
            # No PDF library available - return HTML with instructions
            fallback_message = """
<!DOCTYPE html>
<html>
<head>
    <title>PDF Generation Not Available</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background: #f9fafb;
        }
        .warning {
            background: #fef3c7;
            border: 2px solid #f59e0b;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }
        .instructions {
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }
        code {
            background: #e5e7eb;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: monospace;
        }
    </style>
</head>
<body>
    <h1>PDF Generation Not Available</h1>
    <div class="warning">
        <strong>⚠️ PDF libraries are not installed</strong>
        <p>PDF generation requires either WeasyPrint or xhtml2pdf library.</p>
    </div>
    <div class="instructions">
        <h2>Installation Instructions:</h2>
        <p><strong>Option 1 - xhtml2pdf (Recommended for Windows):</strong></p>
        <code>pip install xhtml2pdf</code>
        
        <p style="margin-top: 20px;"><strong>Option 2 - WeasyPrint (Better quality, requires GTK):</strong></p>
        <code>pip install weasyprint</code>
        
        <p style="margin-top: 20px;">3. Alternatively, use the HTML report format which is available now.</p>
    </div>
    <div class="instructions">
        <h2>Alternative Options:</h2>
        <ul>
            <li>Use the HTML report format (fully functional)</li>
            <li>Print the HTML report to PDF using your browser (Ctrl+P)</li>
            <li>Use online HTML-to-PDF converters</li>
        </ul>
    </div>
</body>
</html>"""
            return fallback_message.encode('utf-8')
        
        try:
            # Try WeasyPrint first (better quality)
            if self.weasyprint_available:
                html = self.weasyprint.HTML(string=html_content, base_url=base_url)
                pdf_bytes = html.write_pdf()
                return pdf_bytes
            
            # Fallback to xhtml2pdf
            elif self.xhtml2pdf_available:
                # xhtml2pdf requires BytesIO for output
                from io import BytesIO
                pdf_buffer = BytesIO()
                
                # Convert HTML to PDF
                pisa_status = self.pisa.CreatePDF(
                    html_content.encode('utf-8'),
                    dest=pdf_buffer,
                    encoding='utf-8'
                )
                
                if pisa_status.err:
                    raise Exception(f"xhtml2pdf conversion failed with {pisa_status.err} errors")
                
                # Get PDF bytes
                pdf_bytes = pdf_buffer.getvalue()
                pdf_buffer.close()
                return pdf_bytes
        
        except Exception as e:
            # Error fallback
            error_html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>PDF Generation Error</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
        }}
        .error {{
            background: #fecaca;
            border: 2px solid #ef4444;
            padding: 20px;
            border-radius: 8px;
        }}
    </style>
</head>
<body>
    <h1>PDF Generation Error</h1>
    <div class="error">
        <strong>Error:</strong> {str(e)}
        <p><strong>Library used:</strong> {self.pdf_library or 'None'}</p>
        <p>Please use the HTML format instead or try the browser print option (Ctrl+P).</p>
    </div>
</body>
</html>"""
            return error_html.encode('utf-8')
    
    def add_pdf_specific_styles(self, html_content: str) -> str:
        """
        Add PDF-specific CSS styles to HTML content.
        
        Args:
            html_content: Original HTML content
            
        Returns:
            HTML with PDF-specific styles
        """
        pdf_styles = """
    <style>
        @page {
            size: A4;
            margin: 2cm;
            @top-right {
                content: "Page " counter(page) " of " counter(pages);
                font-size: 10px;
                color: #6b7280;
            }
        }
        
        /* Page breaks */
        .page-break {
            page-break-before: always;
        }
        
        /* Avoid breaks inside elements */
        .stat-card, .action-item, .issue-card, .chart-container {
            page-break-inside: avoid;
        }
        
        /* Print-specific adjustments */
        @media print {
            body {
                font-size: 11pt;
            }
            
            .report-header {
                background: #1e40af !important;
                -webkit-print-color-adjust: exact;
                print-color-adjust: exact;
            }
            
            .stat-card {
                -webkit-print-color-adjust: exact;
                print-color-adjust: exact;
            }
        }
    </style>"""
        
        # Insert PDF styles before </head>
        return html_content.replace('</head>', pdf_styles + '\n</head>')
    
    def optimize_for_pdf(self, html_content: str) -> str:
        """
        Optimize HTML content for PDF rendering.
        
        Args:
            html_content: Original HTML
            
        Returns:
            Optimized HTML
        """
        # Add PDF styles
        html_content = self.add_pdf_specific_styles(html_content)
        
        # Replace Chart.js CDN with inline note (charts won't render in PDF)
        chart_note = """
        <script>
            // Note: Interactive charts are not available in PDF format.
            // Charts will be replaced with static placeholders.
        </script>"""
        
        html_content = html_content.replace(
            '<script src="https://cdn.jsdelivr.net/npm/chart.js',
            '<!-- Charts disabled for PDF --><script src="https://example.com/disabled'
        )
        
        return html_content


class VisualizationHelper:
    """
    Helper class for creating data visualizations for reports.
    """
    
    @staticmethod
    def create_bar_chart_data(
        labels: list,
        values: list,
        title: str = "",
        colors: Optional[list] = None
    ) -> dict:
        """Create data structure for bar chart"""
        
        from ..reports.report_generator import VisualizationData, ChartType
        
        return VisualizationData(
            chart_type=ChartType.BAR,
            title=title,
            labels=labels,
            values=values,
            colors=colors or [],
            data={}
        )
    
    @staticmethod
    def create_pie_chart_data(
        labels: list,
        values: list,
        title: str = "",
        colors: Optional[list] = None
    ) -> dict:
        """Create data structure for pie chart"""
        
        from ..reports.report_generator import VisualizationData, ChartType
        
        return VisualizationData(
            chart_type=ChartType.PIE,
            title=title,
            labels=labels,
            values=values,
            colors=colors or [],
            data={}
        )
    
    @staticmethod
    def create_gauge_chart_data(
        score: float,
        max_score: float = 100,
        title: str = ""
    ) -> dict:
        """Create data structure for gauge chart"""
        
        from ..reports.report_generator import VisualizationData, ChartType
        
        return VisualizationData(
            chart_type=ChartType.GAUGE,
            title=title,
            data={'score': score, 'max': max_score},
            labels=[],
            values=[],
            colors=[]
        )
    
    @staticmethod
    def create_radar_chart_data(
        labels: list,
        values: list,
        title: str = ""
    ) -> dict:
        """Create data structure for radar chart"""
        
        from ..reports.report_generator import VisualizationData, ChartType
        
        return VisualizationData(
            chart_type=ChartType.RADAR,
            title=title,
            labels=labels,
            values=values,
            colors=[],
            data={}
        )
    
    @staticmethod
    def create_score_distribution(scores: dict) -> dict:
        """
        Create visualization for score distribution.
        
        Args:
            scores: Dict of score names to values (0-100)
            
        Returns:
            VisualizationData for radar chart
        """
        labels = list(scores.keys())
        values = list(scores.values())
        
        return VisualizationHelper.create_radar_chart_data(
            labels, values, "Score Distribution"
        )
    
    @staticmethod
    def create_sentiment_breakdown(
        positive_ratio: float,
        neutral_ratio: float,
        negative_ratio: float
    ) -> dict:
        """Create pie chart for sentiment breakdown"""
        
        return VisualizationHelper.create_pie_chart_data(
            labels=['Positive', 'Neutral', 'Negative'],
            values=[positive_ratio, neutral_ratio, negative_ratio],
            title="Sentiment Distribution",
            colors=['#10b981', '#6b7280', '#ef4444']
        )
    
    @staticmethod
    def create_readability_comparison(metrics: dict) -> dict:
        """Create bar chart for readability metrics comparison"""
        
        return VisualizationHelper.create_bar_chart_data(
            labels=list(metrics.keys()),
            values=list(metrics.values()),
            title="Readability Metrics",
            colors=['#3b82f6'] * len(metrics)
        )
    
    @staticmethod
    def encode_image_to_base64(image_path: str) -> str:
        """
        Encode image file to base64 for embedding in HTML/PDF.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Base64 encoded string
        """
        try:
            with open(image_path, 'rb') as f:
                image_data = f.read()
            return base64.b64encode(image_data).decode('utf-8')
        except Exception:
            return ""
    
    @staticmethod
    def create_embedded_image_tag(image_path: str, alt: str = "") -> str:
        """
        Create embedded image tag with base64 data.
        
        Args:
            image_path: Path to image
            alt: Alt text
            
        Returns:
            HTML img tag with embedded data
        """
        base64_data = VisualizationHelper.encode_image_to_base64(image_path)
        if not base64_data:
            return ""
        
        # Detect image type from extension
        ext = image_path.split('.')[-1].lower()
        mime_type = f"image/{ext}" if ext in ['png', 'jpg', 'jpeg', 'gif', 'svg'] else "image/png"
        
        return f'<img src="data:{mime_type};base64,{base64_data}" alt="{alt}">'
