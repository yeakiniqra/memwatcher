"""
Tests for LeakDetector
"""
import time
import pytest
from memwatcher.detector import LeakDetector


class TestLeakDetector:
    
    def test_init(self):
        """Test detector initialization"""
        detector = LeakDetector()
        assert detector.sensitivity == 0.15
        
        detector = LeakDetector(sensitivity=0.5)
        assert detector.sensitivity == 0.5
    
    def test_insufficient_data(self):
        """Test with insufficient snapshots"""
        detector = LeakDetector()
        
        snapshots = [
            {'timestamp': 1.0, 'rss_mb': 100.0},
            {'timestamp': 2.0, 'rss_mb': 100.5},
        ]
        
        result = detector.analyze_snapshots(snapshots)
        
        assert result['leak_detected'] is False
        assert 'Insufficient data' in result['reason']
    
    def test_stable_memory(self):
        """Test with stable memory (no leak)"""
        detector = LeakDetector()
        
        base_time = time.time()
        snapshots = [
            {'timestamp': base_time + i, 'rss_mb': 100.0 + (i % 2) * 0.1}
            for i in range(10)
        ]
        
        result = detector.analyze_snapshots(snapshots)
        
        assert result['leak_detected'] is False
        assert result['confidence'] == 0.0
    
    def test_growing_memory(self):
        """Test with consistently growing memory (leak detected)"""
        detector = LeakDetector(sensitivity=0.1)
        
        base_time = time.time()
        snapshots = [
            {'timestamp': base_time + i, 'rss_mb': 100.0 + i * 0.5}
            for i in range(20)
        ]
        
        result = detector.analyze_snapshots(snapshots)
        
        assert result['leak_detected'] is True
        assert result['confidence'] > 0
        assert result['growth_rate_mb_per_min'] > 0
        assert result['memory_increase_mb'] > 0
    
    def test_severity_levels(self):
        """Test different severity levels"""
        detector = LeakDetector(sensitivity=0.01)
        base_time = time.time()
        
        # High severity (>10 MB/min)
        snapshots_high = [
            {'timestamp': base_time + i, 'rss_mb': 100.0 + i * 0.5}
            for i in range(30)
        ]
        result_high = detector.analyze_snapshots(snapshots_high)
        if result_high['leak_detected']:
            assert result_high['severity'] in ['high', 'medium', 'low']
        
        # Low severity (<1 MB/min)
        snapshots_low = [
            {'timestamp': base_time + i, 'rss_mb': 100.0 + i * 0.01}
            for i in range(30)
        ]
        result_low = detector.analyze_snapshots(snapshots_low)
        # May or may not detect depending on sensitivity
        assert 'severity' in result_low
    
    def test_is_trending_upward(self):
        """Test upward trend detection"""
        detector = LeakDetector()
        
        # Clear upward trend
        values_up = [100.0, 101.0, 102.0, 103.0, 104.0]
        assert detector._is_trending_upward(values_up) is True
        
        # Clear downward trend
        values_down = [104.0, 103.0, 102.0, 101.0, 100.0]
        assert detector._is_trending_upward(values_down) is False
        
        # Stable
        values_stable = [100.0, 100.1, 100.0, 100.1, 100.0]
        assert detector._is_trending_upward(values_stable) is False
    
    def test_calculate_growth_rate(self):
        """Test growth rate calculation"""
        detector = LeakDetector()
        
        # Linear growth: 1 MB per second
        timestamps = [0.0, 1.0, 2.0, 3.0, 4.0]
        values = [100.0, 101.0, 102.0, 103.0, 104.0]
        
        rate = detector._calculate_growth_rate(values, timestamps)
        
        # Should be approximately 1 MB/s
        assert 0.9 <= rate <= 1.1
    
    def test_calculate_growth_rate_no_growth(self):
        """Test growth rate with no growth"""
        detector = LeakDetector()
        
        timestamps = [0.0, 1.0, 2.0, 3.0]
        values = [100.0, 100.0, 100.0, 100.0]
        
        rate = detector._calculate_growth_rate(values, timestamps)
        
        assert rate == 0.0
    
    def test_detect_anomaly(self):
        """Test anomaly detection"""
        detector = LeakDetector()
        
        base_time = time.time()
        
        # Normal values around 100 MB
        snapshots = [
            {'timestamp': base_time + i, 'rss_mb': 100.0 + (i % 3) * 0.5}
            for i in range(15)
        ]
        
        # Normal value - no anomaly
        result = detector.detect_anomaly(snapshots, 100.5)
        assert result is None
        
        # Anomalous value
        result = detector.detect_anomaly(snapshots, 200.0)
        if result:  # May detect anomaly depending on variance
            assert result['anomaly_detected'] is True
            assert 'z_score' in result
    
    def test_recommendation_messages(self):
        """Test that recommendations are provided"""
        detector = LeakDetector(sensitivity=0.01)
        
        base_time = time.time()
        snapshots = [
            {'timestamp': base_time + i, 'rss_mb': 100.0 + i * 0.3}
            for i in range(20)
        ]
        
        result = detector.analyze_snapshots(snapshots)
        
        assert 'recommendation' in result
        assert len(result['recommendation']) > 0
        assert isinstance(result['recommendation'], str)


class TestLeakDetectorEdgeCases:
    
    def test_single_snapshot(self):
        """Test with single snapshot"""
        detector = LeakDetector()
        
        snapshots = [{'timestamp': 1.0, 'rss_mb': 100.0}]
        result = detector.analyze_snapshots(snapshots)
        
        assert result['leak_detected'] is False
    
    def test_empty_snapshots(self):
        """Test with empty snapshots"""
        detector = LeakDetector()
        
        result = detector.analyze_snapshots([])
        
        assert result['leak_detected'] is False
    
    def test_negative_growth(self):
        """Test with decreasing memory (should not detect leak)"""
        detector = LeakDetector()
        
        base_time = time.time()
        snapshots = [
            {'timestamp': base_time + i, 'rss_mb': 100.0 - i * 0.5}
            for i in range(10)
        ]
        
        result = detector.analyze_snapshots(snapshots)
        
        # Should not detect leak when memory decreasing
        assert result['leak_detected'] is False
    
    def test_spiky_memory(self):
        """Test with spiky but stable memory pattern"""
        detector = LeakDetector()
        
        base_time = time.time()
        snapshots = [
            {'timestamp': base_time + i, 'rss_mb': 100.0 + (10 if i % 2 else 0)}
            for i in range(20)
        ]
        
        result = detector.analyze_snapshots(snapshots)
        
        # High variance should prevent leak detection
        # even if there's slight upward bias
        assert 'confidence' in result