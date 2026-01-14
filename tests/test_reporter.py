"""
Tests for MemoryReport
"""

import time
import pytest
from memwatcher.reporter import MemoryReport
from memwatcher.detector import LeakDetector


class TestMemoryReport:

    def test_no_data_report(self):
        """Test report with no snapshots"""
        detector = LeakDetector()
        report = MemoryReport([], None, detector)

        report_dict = report.to_dict()

        assert report_dict["status"] == "no_data"
        assert "message" in report_dict

    def test_basic_report(self):
        """Test basic report generation"""
        detector = LeakDetector()

        base_time = time.time()
        snapshots = [
            {
                "timestamp": base_time + i,
                "rss_mb": 100.0 + i * 0.5,
                "vms_mb": 200.0,
                "percent": 5.0,
                "num_threads": 2,
                "num_fds": 10,
            }
            for i in range(5)
        ]

        report = MemoryReport(snapshots, base_time, detector)
        report_dict = report.to_dict()

        assert "duration_seconds" in report_dict
        assert "snapshots_count" in report_dict
        assert report_dict["snapshots_count"] == 5
        assert "memory_start_mb" in report_dict
        assert "memory_end_mb" in report_dict
        assert "memory_change_mb" in report_dict
        assert "memory_peak_mb" in report_dict
        assert "memory_min_mb" in report_dict

    def test_memory_calculations(self):
        """Test memory calculation accuracy"""
        detector = LeakDetector()

        base_time = time.time()
        snapshots = [
            {"timestamp": base_time + i, "rss_mb": 100.0 + i} for i in range(10)
        ]

        report = MemoryReport(snapshots, base_time, detector)
        report_dict = report.to_dict()

        assert report_dict["memory_start_mb"] == 100.0
        assert report_dict["memory_end_mb"] == 109.0
        assert report_dict["memory_change_mb"] == 9.0
        assert report_dict["memory_peak_mb"] == 109.0
        assert report_dict["memory_min_mb"] == 100.0

    def test_with_leak_analysis(self):
        """Test report includes leak analysis"""
        detector = LeakDetector(sensitivity=0.01)

        base_time = time.time()
        snapshots = [
            {"timestamp": base_time + i, "rss_mb": 100.0 + i * 0.5} for i in range(20)
        ]

        report = MemoryReport(snapshots, base_time, detector)
        report_dict = report.to_dict()

        assert "leak_analysis" in report_dict
        analysis = report_dict["leak_analysis"]

        assert "leak_detected" in analysis
        assert "confidence" in analysis
        assert "recommendation" in analysis

    def test_with_threshold(self):
        """Test report with threshold"""
        detector = LeakDetector()

        base_time = time.time()
        snapshots = [
            {"timestamp": base_time + i, "rss_mb": 100.0 + i} for i in range(5)
        ]

        report = MemoryReport(snapshots, base_time, detector, threshold_mb=102.0)
        report_dict = report.to_dict()

        assert "threshold_mb" in report_dict
        assert report_dict["threshold_mb"] == 102.0
        assert "threshold_exceeded" in report_dict
        assert report_dict["threshold_exceeded"] is True  # Last value is 104.0

    def test_string_representation(self):
        """Test string conversion"""
        detector = LeakDetector()

        base_time = time.time()
        snapshots = [
            {
                "timestamp": base_time + i,
                "rss_mb": 100.0,
                "vms_mb": 200.0,
                "percent": 5.0,
                "num_threads": 2,
            }
            for i in range(3)
        ]

        report = MemoryReport(snapshots, base_time, detector)
        report_str = report.to_string()

        assert isinstance(report_str, str)
        assert "MEMORY WATCHER REPORT" in report_str
        assert "Duration:" in report_str
        assert "MB" in report_str

    def test_detailed_string_report(self):
        """Test detailed string report"""
        detector = LeakDetector()

        base_time = time.time()
        snapshots = [
            {
                "timestamp": base_time + i,
                "rss_mb": 100.0 + i,
                "vms_mb": 200.0,
                "percent": 5.0,
                "num_threads": 2,
            }
            for i in range(5)
        ]

        report = MemoryReport(snapshots, base_time, detector)
        report_str = report.to_string(detailed=True)

        assert "DETAILED SNAPSHOTS" in report_str
        assert "RSS:" in report_str
        assert "VMS:" in report_str

    def test_format_duration(self):
        """Test duration formatting"""
        detector = LeakDetector()
        report = MemoryReport([], None, detector)

        # Test seconds
        assert "s" in report._format_duration(30.0)

        # Test minutes
        assert "m" in report._format_duration(120.0)

        # Test hours
        assert "h" in report._format_duration(7200.0)

    def test_repr(self):
        """Test __repr__ method"""
        detector = LeakDetector()

        snapshots = [{"timestamp": time.time() + i, "rss_mb": 100.0} for i in range(5)]

        report = MemoryReport(snapshots, time.time(), detector)

        repr_str = repr(report)
        assert "MemoryReport" in repr_str
        assert "5" in repr_str

    def test_leak_detected_in_string(self):
        """Test that leak detection appears in string report"""
        detector = LeakDetector(sensitivity=0.01)

        base_time = time.time()
        snapshots = [
            {"timestamp": base_time + i, "rss_mb": 100.0 + i * 0.5} for i in range(20)
        ]

        report = MemoryReport(snapshots, base_time, detector)
        report_str = report.to_string()

        # Should contain leak detection section
        assert "Leak Detection:" in report_str

        # Check if leak was actually detected
        if "LEAK DETECTED" in report_str:
            assert "Severity:" in report_str
            assert "Growth Rate:" in report_str
            assert "Recommendation:" in report_str


class TestMemoryReportEdgeCases:

    def test_single_snapshot(self):
        """Test report with single snapshot"""
        detector = LeakDetector()

        snapshot = [
            {
                "timestamp": time.time(),
                "rss_mb": 100.0,
            }
        ]

        report = MemoryReport(snapshot, time.time(), detector)
        report_dict = report.to_dict()

        # Should still generate valid report
        assert report_dict["snapshots_count"] == 1
        assert report_dict["memory_change_mb"] == 0.0

    def test_decreasing_memory(self):
        """Test report with decreasing memory"""
        detector = LeakDetector()

        base_time = time.time()
        snapshots = [
            {"timestamp": base_time + i, "rss_mb": 100.0 - i} for i in range(5)
        ]

        report = MemoryReport(snapshots, base_time, detector)
        report_dict = report.to_dict()

        assert report_dict["memory_change_mb"] < 0
        assert report_dict["memory_peak_mb"] == 100.0
        assert report_dict["memory_min_mb"] == 96.0
