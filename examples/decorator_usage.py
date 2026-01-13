"""
Decorator usage examples for memwatcher
"""
import time
from memwatcher import watch_memory, detect_leaks


@watch_memory(interval=0.5, print_report=True)
def process_data():
    """Example function with watch_memory decorator"""
    print("Processing data...")
    data = []
    for i in range(5):
        data.append([0] * 100000)
        time.sleep(0.5)
    print("Done!")
    return len(data)


@detect_leaks(interval=0.5, sensitivity=0.1)
def long_running_task():
    """Example function with detect_leaks decorator"""
    print("Running long task...")
    
    # Simulate memory leak
    leaked_data = []
    for i in range(10):
        leaked_data.append([0] * 50000)
        time.sleep(0.6)
    
    print("Task completed!")
    return "success"


@watch_memory(interval=0.5, threshold_mb=500, raise_on_threshold=False)
def batch_processor(batch_size):
    """Example with parameters"""
    print(f"Processing batch of size {batch_size}...")
    
    results = []
    for i in range(batch_size):
        results.append([i] * 10000)
        time.sleep(0.2)
    
    return len(results)


class DataProcessor:
    """Example class with decorated methods"""
    
    @watch_memory(interval=0.5, print_report=False)
    def load_data(self):
        print("Loading data...")
        self.data = [0] * 500000
        time.sleep(1)
        return "loaded"
    
    @detect_leaks(interval=0.5)
    def process(self):
        print("Processing...")
        results = [x * 2 for x in self.data[:100000]]
        time.sleep(1)
        return results


if __name__ == "__main__":
    print("\n🎨 DECORATOR EXAMPLES\n")
    
    # Example 1: Basic watch_memory
    print("=" * 60)
    print("Example 1: watch_memory decorator")
    print("=" * 60)
    result = process_data()
    print(f"Result: {result}\n")
    
    # Example 2: detect_leaks
    print("=" * 60)
    print("Example 2: detect_leaks decorator")
    print("=" * 60)
    result = long_running_task()
    print(f"Result: {result}\n")
    
    # Example 3: With parameters
    print("=" * 60)
    print("Example 3: Decorator with parameters")
    print("=" * 60)
    result = batch_processor(5)
    print(f"Processed: {result} items\n")
    
    # Example 4: Class methods
    print("=" * 60)
    print("Example 4: Decorated class methods")
    print("=" * 60)
    processor = DataProcessor()
    processor.load_data()
    processor.process()
    
    print("\n✅ All decorator examples completed!")