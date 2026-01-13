"""
Basic usage examples for memwatcher
"""
import time
from memwatcher import MemoryWatcher


def example_1_basic_monitoring():
    """Example 1: Basic memory monitoring"""
    print("=" * 60)
    print("Example 1: Basic Memory Monitoring")
    print("=" * 60)
    
    watcher = MemoryWatcher(interval=1.0)
    watcher.start()
    
    # Simulate some work
    print("Doing some work...")
    data = []
    for i in range(5):
        data.append([0] * 100000)  # Allocate memory
        time.sleep(1)
    
    watcher.stop()
    
    report = watcher.get_report()
    print(report.to_string())
    print()


def example_2_context_manager():
    """Example 2: Using context manager"""
    print("=" * 60)
    print("Example 2: Context Manager")
    print("=" * 60)
    
    with MemoryWatcher(interval=0.5) as watcher:
        print("Working inside context...")
        data = [i for i in range(1000000)]
        time.sleep(2)
    
    # Report automatically generated
    report = watcher.get_report()
    print(report.to_string())
    print()


def example_3_with_threshold():
    """Example 3: Using threshold alerts"""
    print("=" * 60)
    print("Example 3: With Threshold")
    print("=" * 60)
    
    watcher = MemoryWatcher(
        interval=0.5,
        threshold_mb=100.0  # Set reasonable threshold
    )
    
    watcher.start()
    
    print("Running with memory threshold...")
    time.sleep(2)
    
    watcher.stop()
    
    report = watcher.get_report()
    print(report.to_string())
    print()


def example_4_with_callback():
    """Example 4: Custom callback on leak detection"""
    print("=" * 60)
    print("Example 4: Custom Callback")
    print("=" * 60)
    
    def my_alert(leak_info):
        print(f"\n⚠️  ALERT: {leak_info['recommendation']}")
    
    watcher = MemoryWatcher(
        interval=0.5,
        callback=my_alert
    )
    watcher._detector.sensitivity = 0.05  # More sensitive
    
    watcher.start()
    
    print("Creating gradual memory growth...")
    data = []
    for i in range(10):
        data.append([0] * 50000)
        time.sleep(0.6)
    
    watcher.stop()
    
    report = watcher.get_report()
    print("\n" + report.to_string())
    print()


def example_5_tracemalloc():
    """Example 5: Using tracemalloc for detailed tracking"""
    print("=" * 60)
    print("Example 5: With Tracemalloc")
    print("=" * 60)
    
    watcher = MemoryWatcher(
        interval=1.0,
        enable_tracemalloc=True
    )
    
    watcher.start()
    
    print("Running with detailed tracking...")
    time.sleep(3)
    
    watcher.stop()
    
    report = watcher.get_report()
    print(report.to_string(detailed=True))
    print()


if __name__ == "__main__":
    print("\n🔍 MEMWATCHER EXAMPLES\n")
    
    # Run examples
    example_1_basic_monitoring()
    example_2_context_manager()
    example_3_with_threshold()
    example_4_with_callback()
    example_5_tracemalloc()
    
    print("\n✅ All examples completed!")