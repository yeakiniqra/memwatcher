"""
Custom exceptions for memwatcher
"""


class MemoryWatcherError(Exception):
    """Base exception for all memwatcher errors"""

    pass


class ThresholdExceededError(MemoryWatcherError):
    """Raised when memory usage exceeds threshold"""

    def __init__(self, current_mb, threshold_mb, message=None):
        self.current_mb = current_mb
        self.threshold_mb = threshold_mb
        if message is None:
            message = (
                f"Memory usage {current_mb:.2f}MB exceeds "
                f"threshold {threshold_mb:.2f}MB"
            )
        super().__init__(message)


class WatcherNotStartedError(MemoryWatcherError):
    """Raised when trying to stop a watcher that hasn't been started"""

    pass


class InvalidConfigError(MemoryWatcherError):
    """Raised when configuration is invalid"""

    pass
