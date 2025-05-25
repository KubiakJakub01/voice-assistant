"""
Core package for the Gastronomy Voice Assistant.
Contains the voice pipeline and other core functionality.
"""

from .text_agent import TextAgent
from .voice_agent import VoiceAgent

__all__ = ['VoiceAgent', 'TextAgent']
