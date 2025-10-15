"""
Progress UI Component - Display loading and progress indicators
"""
import streamlit as st
from typing import Optional
import time


class ProgressUI:
    """Progress indicator manager"""
    
    def __init__(self):
        self.progress_bar = None
        self.status_text = None
    
    def start(self, message: str = "Starting analysis..."):
        """Start progress indicator"""
        self.status_text = st.empty()
        self.progress_bar = st.progress(0)
        self.status_text.text(message)
    
    def update(self, progress: float, message: str):
        """
        Update progress
        
        Args:
            progress: Progress value (0.0 to 1.0)
            message: Status message
        """
        if self.progress_bar:
            self.progress_bar.progress(progress)
        if self.status_text:
            self.status_text.text(message)
    
    def complete(self, message: str = "Analysis complete!"):
        """Complete progress indicator"""
        if self.progress_bar:
            self.progress_bar.progress(1.0)
        if self.status_text:
            self.status_text.text(message)
            time.sleep(0.5)
            self.status_text.empty()
            self.progress_bar.empty()
    
    def error(self, message: str = "Analysis failed"):
        """Show error state"""
        if self.status_text:
            self.status_text.error(message)
        if self.progress_bar:
            self.progress_bar.empty()


def show_loading_spinner(message: str = "Processing..."):
    """
    Show loading spinner
    
    Args:
        message: Loading message
    
    Returns:
        Spinner context manager
    """
    return st.spinner(message)
