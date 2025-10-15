"""
URL Input Component - Streamlit component for URL input
"""
import streamlit as st
from typing import Optional


def render_url_input() -> Optional[str]:
    """
    Render URL input component
    
    Returns:
        URL string if valid, None otherwise
    """
    st.subheader("🔗 Enter URL to Analyze")
    
    # URL input
    url = st.text_input(
        "Website URL",
        placeholder="https://example.com",
        help="Enter the full URL of the website you want to analyze"
    )
    
    # Analysis options in expander
    with st.expander("⚙️ Analysis Options"):
        col1, col2 = st.columns(2)
        
        with col1:
            include_llm = st.checkbox(
                "Include AI Analysis",
                value=True,
                help="Use LLM for advanced content analysis"
            )
        
        with col2:
            aggressive_clean = st.checkbox(
                "Aggressive Cleaning",
                value=False,
                help="Remove URLs, emails, and special characters"
            )
    
    # Store options in session state
    st.session_state['include_llm'] = include_llm
    st.session_state['aggressive_clean'] = aggressive_clean
    
    # Analyze button
    analyze_button = st.button(
        "🚀 Analyze Website",
        type="primary",
        use_container_width=True
    )
    
    if analyze_button and url:
        return url
    
    return None
