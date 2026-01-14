# MemWatcher

[![Tests](https://github.com/yeakiniqra/memwatcher/actions/workflows/test.yml/badge.svg)](https://github.com/yeakiniqra/memwatcher/actions/workflows/test.yml)
[![PyPI version](https://badge.fury.io/py/memwatcher.svg)](https://badge.fury.io/py/memwatcher)
[![Python versions](https://img.shields.io/pypi/pyversions/memwatcher.svg)](https://pypi.org/project/memwatcher/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Coverage](https://codecov.io/gh/yeakiniqra/memwatcher/branch/main/graph/badge.svg)](https://codecov.io/gh/yeakiniqra/memwatcher)

**Intelligent Memory Leak Detective for Python**

MemWatcher is a lightweight, easy-to-use Python library for detecting memory leaks in your applications. It monitors memory usage in real-time, analyzes patterns, and alerts you to potential leaks before they become critical issues.

## Table of Contents

- [Features](#features)
- [Quick Start](#quick-start)
  - [Installation](#installation)
  - [Basic Usage](#basic-usage)
  - [Using Decorators](#using-decorators)
  - [Context Manager](#context-manager)
- [Example Report](#example-report)
- [Use Cases](#use-cases)
- [Advanced Configuration](#advanced-configuration)
- [Documentation](#documentation)
- [Running Tests](#running-tests)
- [Contributing](#contributing)
- [License](#license)
- [Credits](#credits)

## Features

- **Lightweight & Fast** - Minimal overhead, runs in background thread
- **Smart Detection** - Statistical algorithms detect real leaks, not just growth
- **Beautiful Reports** - Human-readable reports with actionable insights
- **Simple API** - Decorators, context managers, or manual control
- **Framework Ready** - Works with Django, FastAPI, Flask, and more
- **Real-time Monitoring** - Continuous monitoring with customizable intervals
- **Configurable** - Thresholds, sensitivity, callbacks - all customizable

## Quick Start

### Installation

```bash
pip install memwatcher
```

### Basic Usage

```python
from memwatcher import MemoryWatcher

# Start monitoring
watcher = MemoryWatcher(interval=5.0)
watcher.start()

# Your application code here
# ...

# Stop and get report
watcher.stop()
report = watcher.get_report()
print(report)
```

### Using Decorators

```python
from memwatcher import watch_memory, detect_leaks

@watch_memory(interval=1.0)
def process_large_dataset():
    # Your code here
    pass

@detect_leaks(sensitivity=0.1)
def long_running_task():
    # Your code here
    pass
```

### Context Manager

```python
from memwatcher import MemoryWatcher

with MemoryWatcher(interval=2.0) as watcher:
    # Your code here
    pass

# Report automatically generated
report = watcher.get_report()
```

## Example Report

```
============================================================
MEMORY WATCHER REPORT
============================================================

Duration: 45.2s
Snapshots: 9

Memory Usage:
  Start:  145.23 MB
  End:    289.67 MB
  Change: +144.44 MB
  Peak:   289.67 MB
  Min:    145.23 MB

Leak Detection:
  Status: ⚠️  LEAK DETECTED
  Severity: MEDIUM
  Confidence: 87.3%
  Growth Rate: 3.197 MB/min
  Total Increase: 144.44 MB

Recommendation: Warning: Potential memory leak detected. Monitor closely.
============================================================
```

## Use Cases

- **Development**: Catch leaks during development before they hit production
- **Testing**: Add memory checks to your test suite
- **Production**: Lightweight monitoring in production environments
- **CI/CD**: Automated leak detection in your pipeline
- **Profiling**: Quick memory profiling for specific functions

## Advanced Configuration

```python
from memwatcher import MemoryWatcher

watcher = MemoryWatcher(
    interval=5.0,              # Snapshot every 5 seconds
    threshold_mb=500.0,        # Alert if exceeds 500MB
    enable_tracemalloc=True,   # Detailed tracking (higher overhead)
    callback=my_alert_function,# Custom callback on leak detection
    max_snapshots=100          # Keep last 100 snapshots
)
```

## Documentation

Full documentation coming soon!

For now, check out the `examples/` directory for more usage patterns.

## Running Tests

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=memwatcher --cov-report=html
```

## Contributing

We welcome contributions from the community! Whether you're fixing bugs, adding features, or improving documentation, your help is appreciated.

### How to Contribute

1. **Fork the Repository**
   - Click the "Fork" button at the top right of this repository

2. **Clone Your Fork**
   ```bash
   git clone https://github.com/your-username/memwatcher.git
   cd memwatcher
   ```

3. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

4. **Set Up Development Environment**
   ```bash
   # Install in development mode with all dependencies
   pip install -e ".[dev]"
   ```

5. **Make Your Changes**
   - Write clean, readable code
   - Follow PEP 8 style guidelines
   - Add tests for new features
   - Update documentation as needed

6. **Run Tests**
   ```bash
   # Run all tests
   pytest
   
   # Run with coverage
   pytest --cov=memwatcher --cov-report=html
   ```

7. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```
   
   Follow [Conventional Commits](https://www.conventionalcommits.org/) format:
   - `feat:` for new features
   - `fix:` for bug fixes
   - `docs:` for documentation changes
   - `test:` for test additions/changes
   - `refactor:` for code refactoring

8. **Push to Your Fork**
   ```bash
   git push origin feature/your-feature-name
   ```

9. **Submit a Pull Request**
   - Go to the original repository
   - Click "New Pull Request"
   - Provide a clear description of your changes

### Reporting Issues

Found a bug or have a feature request? Please [open an issue](https://github.com/yeakiniqra/memwatcher/issues) with:
- Clear description of the problem or suggestion
- Steps to reproduce (for bugs)
- Expected vs actual behavior
- Your environment (Python version, OS, etc.)

### Code of Conduct

Please be respectful and constructive in all interactions. We're here to build something great together!

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Credits

Built with ❤️ by Yeakin Iqra

---

**Star us on GitHub if MemWatcher helps you catch those sneaky memory leaks!**