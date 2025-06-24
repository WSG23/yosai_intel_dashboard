#!/usr/bin/env python3
"""
Simplified Services Package
"""
import logging

logger = logging.getLogger(__name__)

# Only import existing services
try:
    from .file_processor import FileProcessor
    FILE_PROCESSOR_AVAILABLE = True
except ImportError:
    logger.warning("File processor not available")
    FILE_PROCESSOR_AVAILABLE = False
    FileProcessor = None

__all__ = ['FileProcessor', 'FILE_PROCESSOR_AVAILABLE']
