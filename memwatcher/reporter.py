"""
Memory report generation
"""

from typing import List, Dict, Any, Optional
from .detector import LeakDetector


class MemoryReport:
    """
    Generate human-readable memory usage reports
    """

    def __init__(
        self,
        snapshots: List[Dict[str, Any]],
        start_time: Optional[float],
        detector: LeakDetector,
        threshold_mb: Optional[float] = None,
    ):
        self.snapshots = snapshots
        self.start_time = start_time
        self.detector = detector
        self.threshold_mb = threshold_mb

        self._analysis = None
        if len(snapshots) >= 3:
            self._analysis = detector.analyze_snapshots(snapshots)

    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary"""
        if not self.snapshots:
            return {"status": "no_data", "message": "No snapshots recorded yet"}

        first = self.snapshots[0]
        last = self.snapshots[-1]

        duration = last["timestamp"] - first["timestamp"]

        report = {
            "duration_seconds": duration,
            "duration_formatted": self._format_duration(duration),
            "snapshots_count": len(self.snapshots),
            "memory_start_mb": first["rss_mb"],
            "memory_end_mb": last["rss_mb"],
            "memory_change_mb": last["rss_mb"] - first["rss_mb"],
            "memory_peak_mb": max(s["rss_mb"] for s in self.snapshots),
            "memory_min_mb": min(s["rss_mb"] for s in self.snapshots),
        }

        if self._analysis:
            report["leak_analysis"] = self._analysis

        if self.threshold_mb:
            report["threshold_mb"] = self.threshold_mb
            report["threshold_exceeded"] = last["rss_mb"] > self.threshold_mb

        return report

    def to_string(self, detailed: bool = False) -> str:
        """Generate human-readable string report"""
        data = self.to_dict()

        if data.get("status") == "no_data":
            return data["message"]

        lines = [
            "=" * 60,
            "MEMORY WATCHER REPORT",
            "=" * 60,
            "",
            f"Duration: {data['duration_formatted']}",
            f"Snapshots: {data['snapshots_count']}",
            "",
            "Memory Usage:",
            f"  Start:  {data['memory_start_mb']:.2f} MB",
            f"  End:    {data['memory_end_mb']:.2f} MB",
            f"  Change: {data['memory_change_mb']:+.2f} MB",
            f"  Peak:   {data['memory_peak_mb']:.2f} MB",
            f"  Min:    {data['memory_min_mb']:.2f} MB",
        ]

        if "leak_analysis" in data:
            analysis = data["leak_analysis"]
            status = (
                "⚠️  LEAK DETECTED"
                if analysis["leak_detected"]
                else "✓ No leak detected"
            )
            lines.extend(
                [
                    "",
                    "Leak Detection:",
                    f"  Status: {status}",
                ]
            )

            if analysis["leak_detected"]:
                lines.extend(
                    [
                        f"  Severity: {analysis['severity'].upper()}",
                        f"  Confidence: {analysis['confidence']*100:.1f}%",
                        f"  Growth Rate: "
                        f"{analysis['growth_rate_mb_per_min']:.3f} MB/min",
                        f"  Total Increase: {analysis['memory_increase_mb']:.2f} MB",
                        "",
                        f"Recommendation: {analysis['recommendation']}",
                    ]
                )

        if self.threshold_mb and data.get("threshold_exceeded"):
            lines.extend(
                [
                    "",
                    "⚠️  WARNING: Memory threshold exceeded!",
                    f"   Current: {data['memory_end_mb']:.2f} MB",
                    f"   Threshold: {self.threshold_mb:.2f} MB",
                ]
            )

        if detailed and len(self.snapshots) > 0:
            lines.extend(
                [
                    "",
                    "=" * 60,
                    "DETAILED SNAPSHOTS (last 10):",
                    "=" * 60,
                ]
            )

            for snapshot in self.snapshots[-10:]:
                elapsed = snapshot["timestamp"] - self.snapshots[0]["timestamp"]
                lines.append(
                    f"  [{elapsed:7.1f}s] RSS: {snapshot['rss_mb']:7.2f} MB | "
                    f"VMS: {snapshot['vms_mb']:7.2f} MB | "
                    f"Threads: {snapshot['num_threads']}"
                )

        lines.append("=" * 60)
        return "\n".join(lines)

    def _format_duration(self, seconds: float) -> str:
        """Format duration in human-readable format"""
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}m"
        else:
            hours = seconds / 3600
            return f"{hours:.1f}h"

    def __str__(self) -> str:
        return self.to_string()

    def __repr__(self) -> str:
        return f"<MemoryReport snapshots={len(self.snapshots)}>"
