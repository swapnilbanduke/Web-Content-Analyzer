"""
State Manager - Streamlit session state management
"""
import streamlit as st
from typing import Any, Optional


class StateManager:
    """
    Manages Streamlit session state
    """
    
    @staticmethod
    def init_state():
        """Initialize session state variables"""
        if 'analysis_results' not in st.session_state:
            st.session_state.analysis_results = None
        
        if 'last_url' not in st.session_state:
            st.session_state.last_url = ""
        
        if 'include_llm' not in st.session_state:
            st.session_state.include_llm = True
        
        if 'aggressive_clean' not in st.session_state:
            st.session_state.aggressive_clean = False
        
        if 'analysis_history' not in st.session_state:
            st.session_state.analysis_history = []
    
    @staticmethod
    def get(key: str, default: Any = None) -> Any:
        """
        Get value from session state
        
        Args:
            key: State key
            default: Default value if key not found
            
        Returns:
            State value
        """
        return st.session_state.get(key, default)
    
    @staticmethod
    def set(key: str, value: Any):
        """
        Set value in session state
        
        Args:
            key: State key
            value: Value to set
        """
        st.session_state[key] = value
    
    @staticmethod
    def add_to_history(url: str, results: dict):
        """
        Add analysis to history
        
        Args:
            url: Analyzed URL
            results: Analysis results
        """
        if 'analysis_history' not in st.session_state:
            st.session_state.analysis_history = []
        
        # Add to beginning of history
        st.session_state.analysis_history.insert(0, {
            'url': url,
            'timestamp': results.get('timestamp'),
            'results': results
        })
        
        # Keep only last 10
        st.session_state.analysis_history = st.session_state.analysis_history[:10]
    
    @staticmethod
    def get_history() -> list:
        """
        Get analysis history
        
        Returns:
            List of previous analyses
        """
        return st.session_state.get('analysis_history', [])
    
    @staticmethod
    def clear_history():
        """Clear analysis history"""
        st.session_state.analysis_history = []
