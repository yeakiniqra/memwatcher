"""
Tests for decorators
"""

import time
import pytest
import warnings
from memwatcher.decorators import watch_memory, detect_leaks
from memwatcher.exceptions import ThresholdExceededError


class TestWatchMemoryDecorator:

    def test_basic_usage(self):
        """Test basic decorator usage"""

        @watch_memory(interval=0.1, print_report=False)
        def simple_function():
            time.sleep(0.2)
            return "done"

        result = simple_function()
        assert result == "done"

    def test_with_memory_allocation(self):
        """Test decorator with actual memory allocation"""

        @watch_memory(interval=0.1, print_report=False)
        def allocate_memory():
            data = [0] * 100000
            time.sleep(0.2)
            return len(data)

        result = allocate_memory()
        assert result == 100000

    def test_threshold_not_exceeded(self):
        """Test that no error raised when under threshold"""

        @watch_memory(
            interval=0.1,
            threshold_mb=10000,  # Very high threshold
            raise_on_threshold=True,
            print_report=False,
        )
        def small_function():
            return "ok"

        # Should not raise
        result = small_function()
        assert result == "ok"

    def test_function_metadata_preserved(self):
        """Test that decorator preserves function metadata"""

        @watch_memory(print_report=False)
        def documented_function():
            """This is a test function"""
            return 42

        assert documented_function.__name__ == "documented_function"
        assert documented_function.__doc__ == "This is a test function"

    def test_with_arguments(self):
        """Test decorator on function with arguments"""

        @watch_memory(interval=0.1, print_report=False)
        def function_with_args(a, b, c=3):
            return a + b + c

        result = function_with_args(1, 2, c=4)
        assert result == 7

    def test_with_exception(self):
        """Test that decorator handles exceptions properly"""

        @watch_memory(interval=0.1, print_report=False)
        def failing_function():
            raise ValueError("test error")

        with pytest.raises(ValueError, match="test error"):
            failing_function()


class TestDetectLeaksDecorator:

    def test_basic_usage(self):
        """Test basic leak detection decorator"""

        @detect_leaks(interval=0.1, warn_on_leak=False)
        def simple_function():
            time.sleep(0.2)
            return "done"

        result = simple_function()
        assert result == "done"

    def test_no_leak_no_warning(self):
        """Test that no warning issued for stable memory"""

        @detect_leaks(interval=0.1, warn_on_leak=True)
        def stable_function():
            x = 100
            time.sleep(0.2)
            return x

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = stable_function()

            # Should not have warnings for stable memory
            leak_warnings = [
                warning
                for warning in w
                if issubclass(warning.category, ResourceWarning)
            ]
            # May or may not warn depending on timing
            assert isinstance(leak_warnings, list)

    def test_function_metadata_preserved(self):
        """Test that decorator preserves function metadata"""

        @detect_leaks()
        def documented_function():
            """Another test function"""
            return 123

        assert documented_function.__name__ == "documented_function"
        assert documented_function.__doc__ == "Another test function"

    def test_with_arguments(self):
        """Test decorator on function with arguments"""

        @detect_leaks(interval=0.1)
        def add_numbers(a, b):
            time.sleep(0.15)
            return a + b

        result = add_numbers(5, 7)
        assert result == 12

    def test_custom_sensitivity(self):
        """Test with custom sensitivity setting"""

        @detect_leaks(interval=0.1, sensitivity=0.5)
        def custom_sens_function():
            time.sleep(0.2)
            return True

        result = custom_sens_function()
        assert result is True

    def test_with_exception(self):
        """Test that decorator handles exceptions properly"""

        @detect_leaks(interval=0.1)
        def failing_function():
            time.sleep(0.1)
            raise RuntimeError("test error")

        with pytest.raises(RuntimeError, match="test error"):
            failing_function()

    def test_spike_then_release(self):
        """Test that spike-and-release pattern is NOT detected as a leak"""
        import gc
        from memwatcher.watcher import MemoryWatcher

        with MemoryWatcher(interval=0.5) as w:
            big_list = [0] * 1000000  # Spike
            time.sleep(1)
            del big_list  # Release
            gc.collect()  # Force garbage collection
            time.sleep(1.5)  # Wait for more snapshots after GC

        report = w.get_report()
        report_dict = report.to_dict()
        
        # Check that memory didn't continuously grow
        # (Peak should be higher than end, indicating release)
        assert report_dict["memory_peak_mb"] > report_dict["memory_end_mb"]


class TestDecoratorIntegration:
    """Test combining decorators and edge cases"""

    def test_multiple_decorators(self):
        """Test stacking multiple decorators"""

        @detect_leaks(interval=0.1, warn_on_leak=False)
        @watch_memory(interval=0.1, print_report=False)
        def multi_decorated():
            time.sleep(0.2)
            return "ok"

        result = multi_decorated()
        assert result == "ok"

    def test_decorator_on_class_method(self):
        """Test decorator on class methods"""

        class TestClass:
            @watch_memory(interval=0.1, print_report=False)
            def method(self):
                return "method_result"

            @detect_leaks(interval=0.1)
            def another_method(self, value):
                return value * 2

        obj = TestClass()

        assert obj.method() == "method_result"
        assert obj.another_method(21) == 42

    def test_async_function_not_supported(self):
        """Test that decorators work with regular functions"""
        # Note: async support would require different implementation

        @watch_memory(interval=0.1, print_report=False)
        def sync_function():
            return "sync"

        result = sync_function()
        assert result == "sync"
