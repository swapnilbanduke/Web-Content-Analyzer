"""
Reports Package

Professional report generation for content analysis results.

Features:
- HTML reports with embedded charts
- PDF reports (requires WeasyPrint)
- JSON exports
- Markdown reports
- Multiple themes (Professional, Modern, Minimal, Colorful)
- Executive summaries
- Visualizations and charts
- Actionable recommendations
"""

from .report_generator import (
    ReportGenerator,
    ReportConfig,
    ReportFormat,
    ReportTheme,
    ReportSection,
    ExecutiveSummary,
    GeneratedReport,
    VisualizationData,
    ChartType,
)

from .html_template import HTMLReportTemplate

from .pdf_generator import (
    PDFGenerator,
    VisualizationHelper,
)


__all__ = [
    # Main generator
    'ReportGenerator',
    
    # Configuration
    'ReportConfig',
    'ReportFormat',
    'ReportTheme',
    
    # Data structures
    'ReportSection',
    'ExecutiveSummary',
    'GeneratedReport',
    'VisualizationData',
    'ChartType',
    
    # Templates and generators
    'HTMLReportTemplate',
    'PDFGenerator',
    
    # Helpers
    'VisualizationHelper',
]

__version__ = '1.0.0'
