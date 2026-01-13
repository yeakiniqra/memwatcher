"""
memwatcher - Intelligent Memory Leak Detective for Python
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A lightweight library for detecting memory leaks in Python applications.

Basic usage:

    from memwatcher import MemoryWatcher
    
    watcher = MemoryWatcher()
    watcher.start()
    
    # Your application code here
    
    watcher.stop()
    report = watcher.get_report()
    print(report)

:copyright: (c) 2025
:license: MIT
"""

__version__ = '0.1.0'
__author__ = 'Yeakin Iqra'
__license__ = 'MIT'

from .watcher import MemoryWatcher
from .detector import LeakDetector
from .reporter import MemoryReport
from .decorators import watch_memory, detect_leaks
from .exceptions import MemoryWatcherError, ThresholdExceededError

__all__ = [
    'MemoryWatcher',
    'LeakDetector',
    'MemoryReport',
    'watch_memory',
    'detect_leaks',
    'MemoryWatcherError',
    'ThresholdExceededError',
]