"""
Decorators for easy memory monitoring
"""

import functools
import warnings
from typing import Callable, Optional

from .watcher import MemoryWatcher
from .exceptions import ThresholdExceededError


def watch_memory(
    interval: float = 1.0,
    threshold_mb: Optional[float] = None,
    raise_on_threshold: bool = False,
    print_report: bool = True,
):
    """
    Decorator to monitor memory usage of a function

    Args:
        interval: Seconds between snapshots
        threshold_mb: Alert threshold in MB
        raise_on_threshold: Raise exception if threshold exceeded
        print_report: Print report after function completes

    Example:
        @watch_memory(threshold_mb=500)
        def process_large_data():
            # your code here
            pass
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            watcher = MemoryWatcher(interval=interval, threshold_mb=threshold_mb)

            watcher.start()

            try:
                result = func(*args, **kwargs)
                return result
            finally:
                watcher.stop()
                report = watcher.get_report()

                if print_report:
                    print(report.to_string())

                if threshold_mb and raise_on_threshold:
                    current = watcher.get_current_memory()
                    if current > threshold_mb:
                        raise ThresholdExceededError(current, threshold_mb)

        return wrapper

    return decorator


def detect_leaks(
    interval: float = 2.0, sensitivity: float = 0.15, warn_on_leak: bool = True
):
    """
    Decorator to detect memory leaks in a function

    Args:
        interval: Seconds between snapshots
        sensitivity: Leak detection sensitivity (0-1)
        warn_on_leak: Issue warning if leak detected

    Example:
        @detect_leaks(sensitivity=0.1)
        def long_running_task():
            # your code here
            pass
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            watcher = MemoryWatcher(interval=interval)
            watcher._detector.sensitivity = sensitivity
            watcher.start()

            try:
                result = func(*args, **kwargs)
                return result
            finally:
                watcher.stop()
                report = watcher.get_report()
                analysis = report.to_dict().get("leak_analysis", {})

                if analysis.get("leak_detected") and warn_on_leak:
                    warnings.warn(
                        f"Memory leak detected in {func.__name__}: "
                        f"{analysis['recommendation']}",
                        ResourceWarning,
                        stacklevel=2,
                    )

        return wrapper

    return decorator
