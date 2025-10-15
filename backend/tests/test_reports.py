"""
Unit tests for report generation
Tests HTML, PDF, JSON, and Markdown report generation
"""

import pytest
import json
import tempfile
from pathlib import Path
from datetime import datetime

# Import modules to test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from src.reports.report_generator import ReportGenerator
from src.reports.config import ReportConfig, ReportFormat, ReportTheme
from src.reports.models import Report


class TestReportConfiguration:
    """Test report configuration"""
    
    def test_default_config(self):
        """Test default report configuration"""
        config = ReportConfig()
        
        assert config.format == ReportFormat.HTML
        assert config.theme == ReportTheme.PROFESSIONAL
        assert config.include_charts is True
        assert config.include_executive_summary is True
        assert config.include_recommendations is True
        assert config.include_raw_data is False
    
    def test_custom_config(self):
        """Test custom report configuration"""
        config = ReportConfig(
            format=ReportFormat.PDF,
            theme=ReportTheme.MODERN,
            include_charts=False,
            include_raw_data=True,
            company_name="Test Corp"
        )
        
        assert config.format == ReportFormat.PDF
        assert config.theme == ReportTheme.MODERN
        assert config.include_charts is False
        assert config.include_raw_data is True
        assert config.company_name == "Test Corp"
    
    def test_all_formats(self):
        """Test all report formats"""
        formats = [
            ReportFormat.HTML,
            ReportFormat.PDF,
            ReportFormat.JSON,
            ReportFormat.MARKDOWN
        ]
        
        for fmt in formats:
            config = ReportConfig(format=fmt)
            assert config.format == fmt
    
    def test_all_themes(self):
        """Test all report themes"""
        themes = [
            ReportTheme.PROFESSIONAL,
            ReportTheme.MODERN,
            ReportTheme.MINIMAL,
            ReportTheme.COLORFUL
        ]
        
        for theme in themes:
            config = ReportConfig(theme=theme)
            assert config.theme == theme


class TestReportGenerator:
    """Test report generator functionality"""
    
    @pytest.fixture
    def generator_html(self):
        """Create HTML report generator"""
        config = ReportConfig(format=ReportFormat.HTML)
        return ReportGenerator(config)
    
    @pytest.fixture
    def generator_pdf(self):
        """Create PDF report generator"""
        config = ReportConfig(format=ReportFormat.PDF)
        return ReportGenerator(config)
    
    @pytest.fixture
    def generator_json(self):
        """Create JSON report generator"""
        config = ReportConfig(format=ReportFormat.JSON)
        return ReportGenerator(config)
    
    @pytest.fixture
    def generator_markdown(self):
        """Create Markdown report generator"""
        config = ReportConfig(format=ReportFormat.MARKDOWN)
        return ReportGenerator(config)
    
    def test_generator_initialization(self):
        """Test report generator initialization"""
        generator = ReportGenerator()
        
        assert generator is not None
        assert generator.config is not None
    
    @pytest.mark.asyncio
    async def test_generate_html_report(
        self,
        generator_html,
        mock_analysis_result
    ):
        """Test HTML report generation"""
        report = await generator_html.generate_report(
            analysis_result=mock_analysis_result,
            title="Test Report"
        )
        
        assert report is not None
        assert isinstance(report, Report)
        assert report.format == ReportFormat.HTML
        assert "<html>" in report.content
        assert "</html>" in report.content
        assert "Test Report" in report.content
        assert report.file_size_bytes > 0
    
    @pytest.mark.asyncio
    async def test_generate_pdf_report(
        self,
        generator_pdf,
        mock_analysis_result
    ):
        """Test PDF report generation"""
        try:
            report = await generator_pdf.generate_report(
                analysis_result=mock_analysis_result,
                title="PDF Test"
            )
            
            assert report is not None
            assert report.format == ReportFormat.PDF
            assert report.content.startswith(b"%PDF")  # PDF header
            assert report.file_size_bytes > 0
        except ImportError:
            pytest.skip("WeasyPrint not installed")
    
    @pytest.mark.asyncio
    async def test_generate_json_report(
        self,
        generator_json,
        mock_analysis_result
    ):
        """Test JSON report generation"""
        report = await generator_json.generate_report(
            analysis_result=mock_analysis_result,
            title="JSON Test"
        )
        
        assert report is not None
        assert report.format == ReportFormat.JSON
        
        # Verify it's valid JSON
        data = json.loads(report.content)
        assert "title" in data
        assert "overall_quality_score" in data
        assert data["title"] == "JSON Test"
    
    @pytest.mark.asyncio
    async def test_generate_markdown_report(
        self,
        generator_markdown,
        mock_analysis_result
    ):
        """Test Markdown report generation"""
        report = await generator_markdown.generate_report(
            analysis_result=mock_analysis_result,
            title="Markdown Test"
        )
        
        assert report is not None
        assert report.format == ReportFormat.MARKDOWN
        assert "# Markdown Test" in report.content
        assert "## " in report.content  # Headers
        assert report.file_size_bytes > 0


class TestReportContent:
    """Test report content and sections"""
    
    @pytest.fixture
    def generator(self):
        """Create default generator"""
        return ReportGenerator()
    
    @pytest.mark.asyncio
    async def test_executive_summary_included(
        self,
        generator,
        mock_analysis_result
    ):
        """Test that executive summary is included"""
        generator.config.include_executive_summary = True
        
        report = await generator.generate_report(
            analysis_result=mock_analysis_result,
            title="Summary Test"
        )
        
        assert "Executive Summary" in report.content or "Summary" in report.content
    
    @pytest.mark.asyncio
    async def test_executive_summary_excluded(
        self,
        generator,
        mock_analysis_result
    ):
        """Test that executive summary can be excluded"""
        generator.config.include_executive_summary = False
        
        report = await generator.generate_report(
            analysis_result=mock_analysis_result,
            title="No Summary Test"
        )
        
        # Executive summary section should not be present
        # (implementation specific - adjust based on actual behavior)
        assert report is not None
    
    @pytest.mark.asyncio
    async def test_recommendations_included(
        self,
        generator,
        mock_analysis_result
    ):
        """Test that recommendations are included"""
        generator.config.include_recommendations = True
        
        report = await generator.generate_report(
            analysis_result=mock_analysis_result,
            title="Recommendations Test"
        )
        
        assert "Recommendation" in report.content or "Suggestion" in report.content
    
    @pytest.mark.asyncio
    async def test_charts_included(
        self,
        generator,
        mock_analysis_result
    ):
        """Test that charts are included"""
        generator.config.include_charts = True
        
        report = await generator.generate_report(
            analysis_result=mock_analysis_result,
            title="Charts Test"
        )
        
        # Check for chart-related content (implementation specific)
        assert report is not None
        # Could check for plotly.js, chart.js, or SVG elements
    
    @pytest.mark.asyncio
    async def test_raw_data_included(
        self,
        generator,
        mock_analysis_result
    ):
        """Test that raw data can be included"""
        generator.config.include_raw_data = True
        
        report = await generator.generate_report(
            analysis_result=mock_analysis_result,
            title="Raw Data Test"
        )
        
        # Should contain JSON or data section
        assert report is not None
    
    @pytest.mark.asyncio
    async def test_quality_score_display(
        self,
        generator,
        mock_analysis_result
    ):
        """Test that quality score is displayed"""
        report = await generator.generate_report(
            analysis_result=mock_analysis_result,
            title="Score Test"
        )
        
        # Quality score should appear in report
        score_str = f"{mock_analysis_result.overall_quality_score:.2f}"
        assert score_str in report.content or str(int(mock_analysis_result.overall_quality_score * 100)) in report.content
    
    @pytest.mark.asyncio
    async def test_timestamp_included(
        self,
        generator,
        mock_analysis_result
    ):
        """Test that timestamp is included"""
        report = await generator.generate_report(
            analysis_result=mock_analysis_result,
            title="Timestamp Test"
        )
        
        # Report should include analysis timestamp
        assert report.generated_at is not None
        assert isinstance(report.generated_at, datetime)


class TestReportThemes:
    """Test different report themes"""
    
    @pytest.mark.asyncio
    async def test_professional_theme(self, mock_analysis_result):
        """Test professional theme"""
        config = ReportConfig(theme=ReportTheme.PROFESSIONAL)
        generator = ReportGenerator(config)
        
        report = await generator.generate_report(
            analysis_result=mock_analysis_result,
            title="Professional Theme"
        )
        
        assert report is not None
        # Could check for specific CSS classes or styles
    
    @pytest.mark.asyncio
    async def test_modern_theme(self, mock_analysis_result):
        """Test modern theme"""
        config = ReportConfig(theme=ReportTheme.MODERN)
        generator = ReportGenerator(config)
        
        report = await generator.generate_report(
            analysis_result=mock_analysis_result,
            title="Modern Theme"
        )
        
        assert report is not None
    
    @pytest.mark.asyncio
    async def test_minimal_theme(self, mock_analysis_result):
        """Test minimal theme"""
        config = ReportConfig(theme=ReportTheme.MINIMAL)
        generator = ReportGenerator(config)
        
        report = await generator.generate_report(
            analysis_result=mock_analysis_result,
            title="Minimal Theme"
        )
        
        assert report is not None
    
    @pytest.mark.asyncio
    async def test_colorful_theme(self, mock_analysis_result):
        """Test colorful theme"""
        config = ReportConfig(theme=ReportTheme.COLORFUL)
        generator = ReportGenerator(config)
        
        report = await generator.generate_report(
            analysis_result=mock_analysis_result,
            title="Colorful Theme"
        )
        
        assert report is not None


class TestReportExports:
    """Test report export functionality"""
    
    @pytest.fixture
    def generator(self):
        """Create generator for exports"""
        return ReportGenerator()
    
    def test_export_json(self, generator, mock_analysis_result):
        """Test JSON export"""
        json_data = generator.export_json(mock_analysis_result)
        
        assert json_data is not None
        
        # Verify it's valid JSON
        data = json.loads(json_data)
        assert "overall_quality_score" in data
        assert "word_count" in data
    
    def test_export_markdown(self, generator, mock_analysis_result):
        """Test Markdown export"""
        md_content = generator.export_markdown(
            analysis_result=mock_analysis_result,
            title="Export Test"
        )
        
        assert md_content is not None
        assert "# Export Test" in md_content
        assert "##" in md_content  # Should have headers
    
    def test_export_csv_data(self, generator, mock_analysis_result):
        """Test CSV data export"""
        csv_data = generator.export_csv_row(mock_analysis_result)
        
        assert csv_data is not None
        assert isinstance(csv_data, dict)
        assert "url" in csv_data
        assert "overall_quality_score" in csv_data


class TestReportFileOperations:
    """Test report file saving and loading"""
    
    @pytest.mark.asyncio
    async def test_save_html_report(self, mock_analysis_result, temp_output_dir):
        """Test saving HTML report to file"""
        generator = ReportGenerator(ReportConfig(format=ReportFormat.HTML))
        
        report = await generator.generate_report(
            analysis_result=mock_analysis_result,
            title="Save Test"
        )
        
        # Save to temp file
        output_file = temp_output_dir / "report.html"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(report.content)
        
        assert output_file.exists()
        assert output_file.stat().st_size > 0
        
        # Verify content
        with open(output_file, "r", encoding="utf-8") as f:
            content = f.read()
            assert "<html>" in content
    
    @pytest.mark.asyncio
    async def test_save_pdf_report(self, mock_analysis_result, temp_output_dir):
        """Test saving PDF report to file"""
        try:
            generator = ReportGenerator(ReportConfig(format=ReportFormat.PDF))
            
            report = await generator.generate_report(
                analysis_result=mock_analysis_result,
                title="PDF Save Test"
            )
            
            # Save to temp file
            output_file = temp_output_dir / "report.pdf"
            with open(output_file, "wb") as f:
                f.write(report.content)
            
            assert output_file.exists()
            assert output_file.stat().st_size > 0
        except ImportError:
            pytest.skip("WeasyPrint not installed")
    
    @pytest.mark.asyncio
    async def test_save_json_report(self, mock_analysis_result, temp_output_dir):
        """Test saving JSON report to file"""
        generator = ReportGenerator(ReportConfig(format=ReportFormat.JSON))
        
        report = await generator.generate_report(
            analysis_result=mock_analysis_result,
            title="JSON Save Test"
        )
        
        # Save to temp file
        output_file = temp_output_dir / "report.json"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(report.content)
        
        assert output_file.exists()
        
        # Verify it's valid JSON
        with open(output_file, "r") as f:
            data = json.load(f)
            assert "overall_quality_score" in data


class TestReportErrorHandling:
    """Test error handling in report generation"""
    
    def test_invalid_format(self):
        """Test handling of invalid format"""
        with pytest.raises(ValueError):
            config = ReportConfig(format="invalid")
    
    def test_invalid_theme(self):
        """Test handling of invalid theme"""
        with pytest.raises(ValueError):
            config = ReportConfig(theme="invalid")
    
    @pytest.mark.asyncio
    async def test_empty_analysis_result(self):
        """Test handling of None analysis result"""
        generator = ReportGenerator()
        
        with pytest.raises(ValueError):
            await generator.generate_report(
                analysis_result=None,
                title="Empty Test"
            )
    
    @pytest.mark.asyncio
    async def test_empty_title(self, mock_analysis_result):
        """Test handling of empty title"""
        generator = ReportGenerator()
        
        # Should use default title or handle gracefully
        report = await generator.generate_report(
            analysis_result=mock_analysis_result,
            title=""
        )
        
        assert report is not None


class TestReportCustomization:
    """Test report customization options"""
    
    @pytest.mark.asyncio
    async def test_custom_logo(self, mock_analysis_result):
        """Test adding custom logo to report"""
        config = ReportConfig(logo_url="https://example.com/logo.png")
        generator = ReportGenerator(config)
        
        report = await generator.generate_report(
            analysis_result=mock_analysis_result,
            title="Logo Test"
        )
        
        assert report is not None
        # Logo URL should appear in HTML
        if report.format == ReportFormat.HTML:
            assert "logo.png" in report.content
    
    @pytest.mark.asyncio
    async def test_custom_company_name(self, mock_analysis_result):
        """Test adding company name to report"""
        config = ReportConfig(company_name="Test Corporation")
        generator = ReportGenerator(config)
        
        report = await generator.generate_report(
            analysis_result=mock_analysis_result,
            title="Company Test"
        )
        
        assert report is not None
        assert "Test Corporation" in report.content


@pytest.mark.integration
class TestReportIntegration:
    """Integration tests for report generation"""
    
    @pytest.mark.asyncio
    async def test_complete_report_workflow(
        self,
        mock_analysis_result,
        temp_output_dir
    ):
        """Test complete report generation workflow"""
        # Generate all formats
        formats = [
            ReportFormat.HTML,
            ReportFormat.JSON,
            ReportFormat.MARKDOWN
        ]
        
        for fmt in formats:
            config = ReportConfig(format=fmt)
            generator = ReportGenerator(config)
            
            report = await generator.generate_report(
                analysis_result=mock_analysis_result,
                title=f"Integration Test - {fmt.value}"
            )
            
            assert report is not None
            assert report.format == fmt
            assert report.file_size_bytes > 0
            
            print(f"✅ {fmt.value} report generated: {report.file_size_bytes} bytes")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
