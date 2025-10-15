"""
Main Streamlit Application
"""
import streamlit as st
import asyncio
import os
from pathlib import Path

# Add src to path
import sys
sys.path.insert(0, str(Path(__file__).parent / "src"))

from components.url_input import render_url_input
from components.results_display import render_results_display, render_error_display
from components.progress import ProgressUI, show_loading_spinner
from services.api_client import APIClient
from services.state_manager import StateManager
from utils.constants import APP_TITLE, MSG_WELCOME
from utils.validators import validate_url

# Page configuration
st.set_page_config(
    page_title="Web Content Analyzer",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize state
StateManager.init_state()

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown(f'<h1 class="main-header">{APP_TITLE}</h1>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    # API Configuration
    api_url = st.text_input(
        "Backend API URL",
        value=os.getenv("API_URL", "http://localhost:8000"),
        help="URL of the backend FastAPI server"
    )
    
    # Save API URL
    StateManager.set('api_url', api_url)
    
    st.divider()
    
    # History
    st.header("📜 History")
    history = StateManager.get_history()
    
    if history:
        for idx, item in enumerate(history[:5]):
            with st.expander(f"{item['url'][:30]}...", expanded=False):
                st.write(f"**Analyzed:** {item.get('timestamp', 'Unknown')}")
                if st.button(f"Load", key=f"load_{idx}"):
                    StateManager.set('analysis_results', item['results'])
                    st.rerun()
        
        if st.button("Clear History"):
            StateManager.clear_history()
            st.rerun()
    else:
        st.info("No analysis history yet")
    
    st.divider()
    
    # About
    st.header("ℹ️ About")
    st.write("""
    **Web Content Analyzer v1.0**
    
    A comprehensive tool for analyzing web content using AI-powered insights.
    
    Built with:
    - FastAPI (Backend)
    - Streamlit (Frontend)
    - OpenAI GPT (LLM)
    """)

# Main content
tab1, tab2 = st.tabs(["🔍 Single URL Analysis", "📊 Batch Analysis"])

with tab1:
    # Welcome message
    if not StateManager.get('analysis_results'):
        st.info(MSG_WELCOME)
    
    # URL Input
    url = render_url_input()
    
    # Process analysis
    if url:
        # Validate URL
        is_valid, error_msg = validate_url(url)
        
        if not is_valid:
            st.error(f"❌ Invalid URL: {error_msg}")
        else:
            # Create API client
            api_client = APIClient(base_url=StateManager.get('api_url'))
            
            # Show progress
            progress = ProgressUI()
            progress.start("🔄 Scraping website...")
            
            try:
                # Simulate progress steps
                progress.update(0.2, "📄 Extracting content...")
                
                # Call API
                async def analyze():
                    return await api_client.analyze_url(
                        url=url,
                        include_llm_analysis=StateManager.get('include_llm', True),
                        options={
                            'aggressive_clean': StateManager.get('aggressive_clean', False)
                        }
                    )
                
                # Run async function
                results = asyncio.run(analyze())
                
                progress.update(0.8, "🤖 Performing AI analysis...")
                progress.complete("✅ Analysis complete!")
                
                # Store results
                StateManager.set('analysis_results', results)
                StateManager.set('last_url', url)
                StateManager.add_to_history(url, results)
                
                # Display results
                render_results_display(results)
                
            except Exception as e:
                progress.error("❌ Analysis failed")
                render_error_display(str(e))
    
    # Display existing results
    elif StateManager.get('analysis_results'):
        render_results_display(StateManager.get('analysis_results'))

with tab2:
    st.subheader("📊 Batch URL Analysis")
    st.info("⚠️ Batch analysis feature coming soon!")
    
    # Batch input
    batch_urls = st.text_area(
        "Enter URLs (one per line)",
        height=200,
        placeholder="https://example1.com\nhttps://example2.com\nhttps://example3.com"
    )
    
    if st.button("Analyze Batch", type="primary"):
        st.warning("Batch analysis is not yet implemented")

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem 0;">
    <p>Web Content Analyzer | Built with ❤️ using FastAPI & Streamlit</p>
</div>
""", unsafe_allow_html=True)
