"""
Core memory watching functionality
"""

import gc
import os
import sys
import time
import threading
import tracemalloc
from typing import Optional, Callable, Dict, Any
from collections import deque

from .detector import LeakDetector
from .reporter import MemoryReport
from .exceptions import WatcherNotStartedError, InvalidConfigError


class MemoryWatcher:
    """
    Main class for monitoring memory usage and detecting leaks.

    Args:
        interval: Seconds between memory snapshots (default: 5.0)
        threshold_mb: Alert if memory exceeds this threshold in MB
        enable_tracemalloc: Enable detailed tracemalloc tracking (adds overhead)
        callback: Optional callback function when leak detected
    """

    def __init__(
        self,
        interval: float = 5.0,
        threshold_mb: Optional[float] = None,
        enable_tracemalloc: bool = False,
        callback: Optional[Callable] = None,
        max_snapshots: int = 100,
    ):
        if interval <= 0:
            raise InvalidConfigError("Interval must be positive")

        self.interval = interval
        self.threshold_mb = threshold_mb
        self.enable_tracemalloc = enable_tracemalloc
        self.callback = callback
        self.max_snapshots = max_snapshots

        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._snapshots = deque(maxlen=max_snapshots)
        self._start_time: Optional[float] = None
        self._detector = LeakDetector()

        if enable_tracemalloc:
            tracemalloc.start()

    def start(self) -> None:
        """Start monitoring memory usage"""
        if self._running:
            return

        self._running = True
        self._start_time = time.time()
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stop monitoring memory usage"""
        if not self._running:
            raise WatcherNotStartedError("Watcher is not running")

        self._running = False
        if self._thread:
            self._thread.join(timeout=self.interval + 1)

    def _monitor_loop(self) -> None:
        """Main monitoring loop running in background thread"""
        while self._running:
            try:
                snapshot = self._take_snapshot()
                self._snapshots.append(snapshot)

                # Check for potential leaks
                if len(self._snapshots) >= 3:
                    leak_info = self._detector.analyze_snapshots(list(self._snapshots))

                    if leak_info.get("leak_detected") and self.callback:
                        self.callback(leak_info)

                time.sleep(self.interval)
            except Exception as e:
                # Don't crash the monitoring thread
                print(f"Error in memory monitor: {e}", file=sys.stderr)

    def _take_snapshot(self) -> Dict[str, Any]:
        """Take a snapshot of current memory usage"""
        import psutil

        process = psutil.Process(os.getpid())
        mem_info = process.memory_info()

        snapshot = {
            "timestamp": time.time(),
            "rss_mb": mem_info.rss / 1024 / 1024,  # Resident Set Size
            "vms_mb": mem_info.vms / 1024 / 1024,  # Virtual Memory Size
            "percent": process.memory_percent(),
            "num_fds": process.num_fds() if hasattr(process, "num_fds") else None,
            "num_threads": process.num_threads(),
        }

        # Add garbage collector stats
        gc_stats = gc.get_stats()
        if gc_stats:
            snapshot["gc_collections"] = gc_stats[0].get("collections", 0)

        # Add tracemalloc data if enabled
        if self.enable_tracemalloc and tracemalloc.is_tracing():
            current, peak = tracemalloc.get_traced_memory()
            snapshot["traced_current_mb"] = current / 1024 / 1024
            snapshot["traced_peak_mb"] = peak / 1024 / 1024

        return snapshot

    def get_current_memory(self) -> float:
        """Get current memory usage in MB"""
        import psutil

        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024

    def get_report(self) -> MemoryReport:
        """Generate a memory usage report"""
        return MemoryReport(
            snapshots=list(self._snapshots),
            start_time=self._start_time,
            detector=self._detector,
            threshold_mb=self.threshold_mb,
        )

    def clear_snapshots(self) -> None:
        """Clear all stored snapshots"""
        self._snapshots.clear()

    def __enter__(self):
        """Context manager support"""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager cleanup"""
        self.stop()
        return False
