# -*- coding: UTF-8 -*-

"""
This module provides templates for news postman and info extractor.

Highly recommended to extend news postman and info extractor for specific
situation, and create a new file named as news source to record it.
"""

from .common import (
    InfoExtractor,
    InfoExtractorJSON,
    InfoExtractorXML,
    NewsPostman,
    NewsPostmanJSON,
    NewsPostmanXML,
)
