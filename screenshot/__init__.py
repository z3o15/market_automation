#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
截图管理模块
负责屏幕截图获取、图片处理、任务调度等功能
"""

from .screenshot_manager import ScreenshotManager
from .image_processor import ImageProcessor
from .capture_manager import CaptureManager

__all__ = [
    "ScreenshotManager",
    "ImageProcessor", 
    "CaptureManager"
]