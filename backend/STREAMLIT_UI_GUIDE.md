# Advanced Streamlit Interface - User Guide

## 🚀 Quick Start

### Installation

1. **Install Streamlit dependencies**:
```bash
cd backend
pip install -r streamlit_requirements.txt
```

2. **Launch the application**:
```bash
python launch_ui.py
```

Or directly with Streamlit:
```bash
streamlit run src/ui/streamlit_app.py
```

The app will automatically open in your browser at `http://localhost:8501`

## 📋 Features

### 1. Single URL Analysis
- Analyze individual web pages in real-time
- Interactive visualizations with Plotly charts
- Comprehensive scoring across 6 dimensions
- Detailed recommendations and insights

### 2. Batch Processing
- Process multiple URLs simultaneously
- Real-time progress tracking
- Bulk export capabilities
- Summary statistics and comparisons

### 3. Advanced Visualizations
- **Gauge Charts**: Quality, SEO, and Readability scores
- **Pie Charts**: Sentiment distribution
- **Bar Charts**: Topic relevance and readability formulas
- **Radar Charts**: Multi-dimensional SEO analysis
- All charts are interactive and responsive

### 4. Export Functionality

#### PDF Reports
- Professional HTML-to-PDF conversion
- Customizable themes (Professional, Modern, Minimal, Colorful)
- Embedded charts and visualizations
- Print-optimized layout

#### JSON Export
- Complete structured data export
- All analysis results included
- Easy integration with other tools
- Machine-readable format

#### CSV Export
- Tabular data for batch results
- Import into Excel or Google Sheets
- Quick comparison and filtering
- Perfect for reporting

#### HTML Reports
- Interactive web reports
- Embedded Chart.js visualizations
- Shareable via email or cloud storage
- Print-friendly design

### 5. Analysis History
- Track all previous analyses
- Filter by status (Success/Failed)
- Time-based filtering (24h, 7d, 30d)
- Quick re-access to past results
- Automatic cleanup (keeps last 100)

## 🎨 Interface Overview

### Sidebar Configuration

#### API Settings
- **AI Provider**: Choose between OpenAI or Anthropic
- **Model Selection**: Select specific model (GPT-4, Claude, etc.)
- **API Key**: Securely enter your API credentials

#### Analysis Options
- **Competitive Analysis**: Enable/disable competitor comparison
- **Competitor URLs**: Add URLs for competitive benchmarking
- **Include all analyzers**: Summary, Sentiment, Topics, SEO, Readability

#### Report Theme
- **Professional**: Blue/gray corporate theme
- **Modern**: Purple/teal contemporary design
- **Minimal**: Black/white clean look
- **Colorful**: Multi-color vibrant style

#### Statistics
- Total analyses count
- Batch results count
- Real-time metrics

### Main Interface Tabs

#### 🔍 Single Analysis Tab
1. Enter URL in the input field
2. Click "Analyze" button
3. Watch real-time progress
4. Explore results in tabbed interface:
   - **Overview**: Gauge charts and quick stats
   - **Summary**: Content summaries and key points
   - **Sentiment**: Emotional analysis and tone
   - **Topics**: Main themes and entities
   - **SEO**: Keyword analysis and recommendations
   - **Readability**: Reading level and accessibility
   - **Recommendations**: Actionable improvements

5. Export results in your preferred format

#### 📋 Batch Processing Tab
1. Enter multiple URLs (one per line)
2. Click "Process Batch"
3. Monitor progress bar
4. View summary table with all results
5. Export batch data (CSV, JSON)

#### 📚 History Tab
1. Browse all previous analyses
2. Filter by status or time period
3. Click to re-view any analysis
4. Clear history when needed

## 📊 Understanding the Metrics

### Quality Score (0-100%)
Overall content quality combining:
- Content depth and completeness
- SEO optimization
- Readability
- Engagement potential

**Interpretation**:
- 80-100%: Excellent (Green)
- 60-79%: Good (Blue)
- 40-59%: Fair (Orange)
- 0-39%: Needs Improvement (Red)

### SEO Score (0-100%)
Search engine optimization effectiveness:
- Keyword optimization
- Meta tags quality
- Content structure
- Internal linking
- Technical SEO
- Mobile-friendliness

### Readability Score (0-100%)
Content accessibility and clarity:
- Reading level (grade)
- Sentence complexity
- Word difficulty
- WCAG compliance
- Audience match

### Sentiment Score (-1 to +1)
Emotional tone of content:
- -1.0 to -0.3: Negative
- -0.3 to +0.3: Neutral
- +0.3 to +1.0: Positive

## 🎯 Advanced Features

### Real-Time Progress Tracking
- Live updates during analysis
- Current step indication
- Estimated time remaining
- Success/failure notifications

### Interactive Charts
All visualizations are built with Plotly and support:
- Zoom and pan
- Hover for details
- Download as PNG
- Responsive sizing
- Dark/light mode

### Theme Customization
Choose your report theme based on use case:

**Professional** (Default):
- Best for: Corporate reports, client presentations
- Colors: Blue and gray
- Style: Conservative, trustworthy

**Modern**:
- Best for: Tech companies, startups
- Colors: Purple and teal
- Style: Contemporary, innovative

**Minimal**:
- Best for: Academic, research
- Colors: Black and white
- Style: Clean, focused

**Colorful**:
- Best for: Creative industries, marketing
- Colors: Multi-color palette
- Style: Vibrant, engaging

### Batch Processing Tips

**Optimal Batch Size**:
- Small batches (1-5 URLs): ~30s - 2min
- Medium batches (5-20 URLs): ~2-10min
- Large batches (20-50 URLs): ~10-30min

**Best Practices**:
1. Group similar content types
2. Monitor API rate limits
3. Start small to test settings
4. Use CSV export for large datasets
5. Save results incrementally

### Export Format Selection Guide

**Use PDF when**:
- Creating client deliverables
- Formal documentation needed
- Print versions required
- Offline sharing

**Use JSON when**:
- Integrating with other tools
- Automated processing
- API consumption
- Data archival

**Use CSV when**:
- Need spreadsheet analysis
- Comparing multiple URLs
- Creating charts in Excel
- Sharing with non-technical users

**Use HTML when**:
- Interactive charts needed
- Web-based sharing
- Email distribution
- Maximum compatibility

## 🔧 Configuration Tips

### API Key Management
Store API keys in environment variables for security:

**Windows PowerShell**:
```powershell
$env:OPENAI_API_KEY = "your-key-here"
$env:ANTHROPIC_API_KEY = "your-key-here"
```

**Linux/Mac**:
```bash
export OPENAI_API_KEY="your-key-here"
export ANTHROPIC_API_KEY="your-key-here"
```

Or create a `.env` file (add to `.gitignore`):
```
OPENAI_API_KEY=your-key-here
ANTHROPIC_API_KEY=your-key-here
```

### Performance Optimization

**Faster Analysis**:
- Use GPT-3.5-turbo instead of GPT-4
- Use Claude Haiku instead of Opus
- Disable competitive analysis if not needed
- Process smaller batches

**Higher Quality**:
- Use GPT-4-turbo or Claude Opus
- Enable all analyzers
- Include competitive analysis
- Allow longer processing time

### Memory Management
The app automatically:
- Keeps last 100 history items
- Clears old batch results
- Manages session state efficiently

Manual cleanup:
- Click "Clear History" in History tab
- Click "Clear Results" in Batch tab
- Restart app to reset completely

## 🐛 Troubleshooting

### Common Issues

**"API key not configured"**:
- Check API key is entered in sidebar
- Verify key is valid and active
- Check for extra spaces or characters

**"Analysis failed"**:
- Verify URL is accessible
- Check internet connection
- Ensure sufficient API credits
- Try a different URL

**"Charts not loading"**:
- Check browser console for errors
- Refresh the page (Ctrl+R)
- Clear browser cache
- Try different browser

**"PDF generation failed"**:
- Install WeasyPrint: `pip install weasyprint`
- On Windows, install GTK: `pip install weasyprint[gtk]`
- Use HTML export as alternative

**"Slow performance"**:
- Reduce batch size
- Use faster AI model
- Check internet speed
- Disable unnecessary analyzers

### Browser Compatibility
Recommended browsers:
- ✅ Chrome/Edge (Best)
- ✅ Firefox
- ✅ Safari
- ⚠️ IE/Old browsers (Limited support)

### Port Already in Use
If port 8501 is busy:
```bash
streamlit run src/ui/streamlit_app.py --server.port=8502
```

## 💡 Usage Examples

### Example 1: Quick Single Analysis
1. Open app
2. Enter API key in sidebar
3. Paste URL: `https://example.com/blog-post`
4. Click "Analyze"
5. Wait ~20 seconds
6. Explore results in tabs
7. Export as PDF

### Example 2: Batch Competitive Analysis
1. Enable "Competitive Analysis" in sidebar
2. Add competitor URLs
3. Go to Batch tab
4. Paste your URLs (one per line)
5. Click "Process Batch"
6. Wait for completion
7. Export as CSV
8. Analyze in Excel

### Example 3: Historical Comparison
1. Analyze URL today
2. Wait 1 week
3. Analyze same URL again
4. Go to History tab
5. Compare both results
6. Track improvements

## 📈 Metrics Reference

### Content Quality Components
- **Depth**: Comprehensive coverage
- **Structure**: Logical organization
- **Clarity**: Easy to understand
- **Engagement**: Keeps readers interested
- **Value**: Usefulness to audience

### SEO Breakdown
- **Content Score**: Keyword usage, relevance
- **Technical Score**: Meta tags, structure
- **Keywords Score**: Optimization level
- **Structure Score**: Headings, hierarchy
- **Links Score**: Internal/external linking
- **Meta Score**: Title, description quality

### Readability Formulas
- **Flesch Reading Ease**: 0-100 (higher = easier)
- **Flesch-Kincaid Grade**: US grade level
- **SMOG Index**: Years of education needed
- **Coleman-Liau**: Based on characters
- **ARI**: Automated Readability Index

## 🔐 Security Best Practices

1. **Never commit API keys** to version control
2. **Use environment variables** for sensitive data
3. **Rotate keys regularly** for security
4. **Monitor API usage** to detect anomalies
5. **Limit key permissions** to necessary scopes

## 🚀 Advanced Workflows

### Workflow 1: Content Audit
1. Export all blog URLs to CSV
2. Paste into Batch tab
3. Process all URLs
4. Export results to CSV
5. Identify low-quality content
6. Create improvement plan

### Workflow 2: Competitor Analysis
1. List competitor articles
2. Enable competitive analysis
3. Add your URL as target
4. Add competitor URLs
5. Analyze
6. Review competitive gaps
7. Plan content strategy

### Workflow 3: SEO Optimization
1. Analyze target page
2. Review SEO tab
3. Note all issues
4. Implement fixes
5. Re-analyze
6. Compare scores
7. Iterate until optimal

## 📞 Support

For issues or questions:
- Check this documentation
- Review troubleshooting section
- Check example scripts in `backend/examples/`
- Review code comments in `streamlit_app.py`

## 🎓 Learning Resources

**Streamlit**:
- [Official Documentation](https://docs.streamlit.io/)
- [Gallery](https://streamlit.io/gallery)
- [Cheat Sheet](https://docs.streamlit.io/library/cheatsheet)

**Plotly**:
- [Graph Reference](https://plotly.com/python/reference/)
- [Chart Types](https://plotly.com/python/)
- [Styling Guide](https://plotly.com/python/styling-plotly-express/)

**Content Analysis**:
- SEO best practices
- Readability guidelines
- Sentiment analysis techniques
- Topic modeling approaches

## 🔄 Version History

### v1.0.0 (Current)
- ✅ Single URL analysis
- ✅ Batch processing
- ✅ Advanced visualizations (Plotly)
- ✅ Export to PDF, JSON, CSV, HTML
- ✅ Analysis history management
- ✅ Theme customization
- ✅ Real-time progress tracking
- ✅ Responsive design

### Planned Features
- 📧 Email delivery of reports
- 📊 Custom dashboard creation
- 🔄 Scheduled analysis jobs
- 📱 Mobile app version
- 🌐 Multi-language support
- 🤖 AI-powered recommendations
- 📈 Trend analysis over time
- 🔗 API endpoint generation

---

**Built with ❤️ using Streamlit, Plotly, and advanced AI models**
