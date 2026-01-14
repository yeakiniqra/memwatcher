"""
Memory leak detection algorithms
"""

import statistics
from typing import List, Dict, Any, Optional


class LeakDetector:
    """
    Analyzes memory snapshots to detect potential leaks
    """

    def __init__(self, sensitivity: float = 0.15):
        """
        Args:
            sensitivity: Threshold for detecting growth trend (0-1)
                        Lower = more sensitive to small leaks
        """
        self.sensitivity = sensitivity

    def analyze_snapshots(self, snapshots: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze a series of snapshots for potential memory leaks

        Returns dict with:
            - leak_detected: bool
            - confidence: float (0-1)
            - growth_rate_mb_per_min: float
            - recommendation: str
        """
        if len(snapshots) < 3:
            return {
                "leak_detected": False,
                "confidence": 0.0,
                "reason": "Insufficient data",
            }

        # Extract memory values and timestamps
        memory_values = [s["rss_mb"] for s in snapshots]
        timestamps = [s["timestamp"] for s in snapshots]

        # Calculate growth trend
        growth_rate = self._calculate_growth_rate(memory_values, timestamps)

        # Check for consistent upward trend
        is_trending_up = self._is_trending_upward(memory_values)

        # Calculate variance (low variance + growth = likely leak)
        variance = statistics.variance(memory_values) if len(memory_values) > 1 else 0
        mean = statistics.mean(memory_values)
        coefficient_of_variation = (variance**0.5) / mean if mean > 0 else 0

        # Detect leak
        leak_detected = (
            is_trending_up
            and growth_rate > self.sensitivity
            and coefficient_of_variation < 0.3  # Consistent growth
        )

        # Calculate confidence
        confidence = min(1.0, growth_rate * 2) if leak_detected else 0.0

        result = {
            "leak_detected": leak_detected,
            "confidence": confidence,
            "growth_rate_mb_per_min": growth_rate * 60,
            "current_memory_mb": memory_values[-1],
            "memory_increase_mb": memory_values[-1] - memory_values[0],
            "snapshots_analyzed": len(snapshots),
        }

        # Add recommendation
        if leak_detected:
            if growth_rate * 60 > 10:  # >10MB/min
                result["severity"] = "high"
                result["recommendation"] = (
                    "Critical: Investigate immediately. Memory growing rapidly."
                )
            elif growth_rate * 60 > 1:  # >1MB/min
                result["severity"] = "medium"
                result["recommendation"] = (
                    "Warning: Potential memory leak detected. Monitor closely."
                )
            else:
                result["severity"] = "low"
                result["recommendation"] = (
                    "Info: Slow memory growth detected. "
                    "May be normal for your workload."
                )
        else:
            result["severity"] = "none"
            result["recommendation"] = "Memory usage appears stable."

        return result

    def _calculate_growth_rate(
        self, values: List[float], timestamps: List[float]
    ) -> float:
        """Calculate memory growth rate in MB per second"""
        if len(values) < 2:
            return 0.0

        # Simple linear regression
        n = len(values)
        time_deltas = [timestamps[i] - timestamps[0] for i in range(n)]

        mean_x = statistics.mean(time_deltas)
        mean_y = statistics.mean(values)

        numerator = sum(
            (time_deltas[i] - mean_x) * (values[i] - mean_y) for i in range(n)
        )
        denominator = sum((time_deltas[i] - mean_x) ** 2 for i in range(n))

        if denominator == 0:
            return 0.0

        slope = numerator / denominator
        return max(0.0, slope)  # Only care about positive growth

    def _is_trending_upward(self, values: List[float], window: int = 5) -> bool:
        """Check if values are consistently trending upward"""
        if len(values) < window:
            window = len(values)

        recent_values = values[-window:]

        # Count how many times each value is greater than previous
        increases = sum(
            1
            for i in range(1, len(recent_values))
            if recent_values[i] > recent_values[i - 1]
        )

        # If more than 60% are increases, consider it trending up
        return (
            increases / (len(recent_values) - 1) > 0.6
            if len(recent_values) > 1
            else False
        )

    def detect_anomaly(
        self, snapshots: List[Dict[str, Any]], current_value: float
    ) -> Optional[Dict[str, Any]]:
        """
        Detect if current memory value is anomalous compared to history
        Uses simple statistical approach
        """
        if len(snapshots) < 10:
            return None

        historical_values = [s["rss_mb"] for s in snapshots[:-1]]
        mean = statistics.mean(historical_values)
        stdev = statistics.stdev(historical_values)

        # Check if current value is more than 3 standard deviations away
        z_score = (current_value - mean) / stdev if stdev > 0 else 0

        if abs(z_score) > 3:
            return {
                "anomaly_detected": True,
                "z_score": z_score,
                "expected_range": (mean - 2 * stdev, mean + 2 * stdev),
                "current_value": current_value,
            }

        return None
