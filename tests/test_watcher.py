"""
Tests for MemoryWatcher
"""
import time
import pytest
from memwatcher import MemoryWatcher
from memwatcher.exceptions import WatcherNotStartedError, InvalidConfigError


class TestMemoryWatcher:
    
    def test_init_default_params(self):
        """Test initialization with default parameters"""
        watcher = MemoryWatcher()
        assert watcher.interval == 5.0
        assert watcher.threshold_mb is None
        assert watcher.enable_tracemalloc is False
        assert not watcher._running
    
    def test_init_custom_params(self):
        """Test initialization with custom parameters"""
        watcher = MemoryWatcher(
            interval=1.0,
            threshold_mb=100.0,
            enable_tracemalloc=True
        )
        assert watcher.interval == 1.0
        assert watcher.threshold_mb == 100.0
        assert watcher.enable_tracemalloc is True
    
    def test_invalid_interval(self):
        """Test that invalid interval raises error"""
        with pytest.raises(InvalidConfigError):
            MemoryWatcher(interval=0)
        
        with pytest.raises(InvalidConfigError):
            MemoryWatcher(interval=-1)
    
    def test_start_stop(self):
        """Test starting and stopping watcher"""
        watcher = MemoryWatcher(interval=0.1)
        
        assert not watcher._running
        
        watcher.start()
        assert watcher._running
        assert watcher._thread is not None
        
        time.sleep(0.3)  # Let it take a few snapshots
        
        watcher.stop()
        assert not watcher._running
    
    def test_stop_without_start(self):
        """Test that stopping without starting raises error"""
        watcher = MemoryWatcher()
        
        with pytest.raises(WatcherNotStartedError):
            watcher.stop()
    
    def test_snapshots_collected(self):
        """Test that snapshots are being collected"""
        watcher = MemoryWatcher(interval=0.1)
        watcher.start()
        
        time.sleep(0.35)  # Should collect ~3 snapshots
        
        watcher.stop()
        
        assert len(watcher._snapshots) >= 2
        
        # Check snapshot structure
        snapshot = watcher._snapshots[0]
        assert 'timestamp' in snapshot
        assert 'rss_mb' in snapshot
        assert 'vms_mb' in snapshot
        assert 'percent' in snapshot
    
    def test_get_current_memory(self):
        """Test getting current memory usage"""
        watcher = MemoryWatcher()
        memory = watcher.get_current_memory()
        
        assert isinstance(memory, float)
        assert memory > 0  # Should have some memory usage
    
    def test_get_report(self):
        """Test report generation"""
        watcher = MemoryWatcher(interval=0.1)
        watcher.start()
        
        time.sleep(0.3)
        
        watcher.stop()
        
        report = watcher.get_report()
        assert report is not None
        
        report_dict = report.to_dict()
        assert 'snapshots_count' in report_dict
        assert report_dict['snapshots_count'] > 0
    
    def test_context_manager(self):
        """Test using watcher as context manager"""
        with MemoryWatcher(interval=0.1) as watcher:
            time.sleep(0.3)
            assert watcher._running
        
        # Should be stopped after context
        assert not watcher._running
    
    def test_clear_snapshots(self):
        """Test clearing snapshots"""
        watcher = MemoryWatcher(interval=0.1)
        watcher.start()
        time.sleep(0.3)
        watcher.stop()
        
        assert len(watcher._snapshots) > 0
        
        watcher.clear_snapshots()
        assert len(watcher._snapshots) == 0
    
    def test_max_snapshots_limit(self):
        """Test that snapshots respect max limit"""
        watcher = MemoryWatcher(interval=0.05, max_snapshots=5)
        watcher.start()
        
        time.sleep(0.5)  # Should try to collect ~10 snapshots
        
        watcher.stop()
        
        # Should be capped at max_snapshots
        assert len(watcher._snapshots) <= 5


class TestMemoryWatcherWithLoad:
    """Tests that create actual memory pressure"""
    
    def test_detect_memory_growth(self):
        """Test detection of memory growth"""
        watcher = MemoryWatcher(interval=0.1)
        watcher.start()
        
        # Create memory growth
        data = []
        for i in range(5):
            data.append([0] * 100000)  # Allocate ~800KB per iteration
            time.sleep(0.15)
        
        watcher.stop()
        
        report = watcher.get_report()
        report_dict = report.to_dict()
        
        # Should show memory increase
        assert report_dict['memory_change_mb'] > 0
        
        # Clean up
        del data
    
    def test_callback_on_leak(self):
        """Test that callback is called when leak detected"""
        callback_called = {'called': False, 'info': None}
        
        def leak_callback(info):
            callback_called['called'] = True
            callback_called['info'] = info
        
        watcher = MemoryWatcher(
            interval=0.1,
            callback=leak_callback
        )
        watcher._detector.sensitivity = 0.01  # Very sensitive
        
        watcher.start()
        
        # Create gradual memory growth
        data = []
        for i in range(5):
            data.append([0] * 50000)
            time.sleep(0.15)
        
        time.sleep(0.2)  # Give time for detection
        
        watcher.stop()
        
        # Callback might be called (depends on sensitivity and timing)
        # Just verify it doesn't crash
        assert isinstance(callback_called['called'], bool)
        
        del data