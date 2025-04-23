"""
System Information Tools

This module provides tools for gathering system information in an OS-independent way.
Each function collects specific information about a system component.
"""

import time
from typing import Any, Dict

import psutil


def get_cpu_info() -> Dict[str, Any]:
    """
    Gather CPU information including core count and usage.

    Returns:
        Dict[str, Any]: Dictionary with CPU information structured for ADK
    """
    try:
        # Get CPU information
        cpu_info = {
            "physical_cores": psutil.cpu_count(logical=False),
            "logical_cores": psutil.cpu_count(logical=True),
            "cpu_usage_per_core": [
                f"Core {i}: {percentage:.1f}%"
                for i, percentage in enumerate(
                    psutil.cpu_percent(interval=1, percpu=True)
                )
            ],
            "avg_cpu_usage": f"{psutil.cpu_percent(interval=1):.1f}%",
        }

        # Calculate some stats for the result summary
        avg_usage = float(cpu_info["avg_cpu_usage"].strip("%"))
        high_usage = avg_usage > 80

        # Format for ADK tool return structure
        return {
            "result": cpu_info,
            "stats": {
                "physical_cores": cpu_info["physical_cores"],
                "logical_cores": cpu_info["logical_cores"],
                "avg_usage_percentage": avg_usage,
                "high_usage_alert": high_usage,
            },
            "additional_info": {
                "data_format": "dictionary",
                "collection_timestamp": time.time(),
                "performance_concern": (
                    "High CPU usage detected" if high_usage else None
                ),
            },
        }
    except Exception as e:
        return {
            "result": {"error": f"Failed to gather CPU information: {str(e)}"},
            "stats": {"success": False},
            "additional_info": {"error_type": str(type(e).__name__)},
        }


def get_memory_info() -> Dict[str, Any]:
    """
    Gather memory information including RAM and swap usage.

    Returns:
        Dict[str, Any]: Dictionary with memory information structured for ADK
    """
    try:
        # Get memory information
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()

        memory_info = {
            "total_memory": f"{memory.total / (1024 ** 3):.2f} GB",
            "available_memory": f"{memory.available / (1024 ** 3):.2f} GB",
            "used_memory": f"{memory.used / (1024 ** 3):.2f} GB",
            "memory_percentage": f"{memory.percent:.1f}%",
            "swap_total": f"{swap.total / (1024 ** 3):.2f} GB",
            "swap_used": f"{swap.used / (1024 ** 3):.2f} GB",
            "swap_percentage": f"{swap.percent:.1f}%",
        }

        # Calculate stats
        memory_usage = memory.percent
        swap_usage = swap.percent
        high_memory_usage = memory_usage > 80
        high_swap_usage = swap_usage > 80

        # Format for ADK tool return structure
        return {
            "result": memory_info,
            "stats": {
                "memory_usage_percentage": memory_usage,
                "swap_usage_percentage": swap_usage,
                "total_memory_gb": memory.total / (1024**3),
                "available_memory_gb": memory.available / (1024**3),
            },
            "additional_info": {
                "data_format": "dictionary",
                "collection_timestamp": time.time(),
                "performance_concern": (
                    "High memory usage detected" if high_memory_usage else None
                ),
                "swap_concern": "High swap usage detected" if high_swap_usage else None,
            },
        }
    except Exception as e:
        return {
            "result": {"error": f"Failed to gather memory information: {str(e)}"},
            "stats": {"success": False},
            "additional_info": {"error_type": str(type(e).__name__)},
        }


def get_disk_info() -> Dict[str, Any]:
    """
    Gather disk information including partitions and usage.

    Returns:
        Dict[str, Any]: Dictionary with disk information structured for ADK
    """
    try:
        # Get disk information
        disk_info = {"partitions": []}
        partitions_over_threshold = []
        total_space = 0
        used_space = 0

        for partition in psutil.disk_partitions():
            try:
                partition_usage = psutil.disk_usage(partition.mountpoint)

                # Track high usage partitions
                if partition_usage.percent > 85:
                    partitions_over_threshold.append(
                        f"{partition.mountpoint} ({partition_usage.percent:.1f}%)"
                    )

                # Add to totals
                total_space += partition_usage.total
                used_space += partition_usage.used

                disk_info["partitions"].append(
                    {
                        "device": partition.device,
                        "mountpoint": partition.mountpoint,
                        "filesystem_type": partition.fstype,
                        "total_size": f"{partition_usage.total / (1024 ** 3):.2f} GB",
                        "used": f"{partition_usage.used / (1024 ** 3):.2f} GB",
                        "free": f"{partition_usage.free / (1024 ** 3):.2f} GB",
                        "percentage": f"{partition_usage.percent:.1f}%",
                    }
                )
            except (PermissionError, FileNotFoundError):
                # Some partitions may not be accessible
                pass

        # Calculate overall disk stats
        overall_usage_percent = (
            (used_space / total_space * 100) if total_space > 0 else 0
        )

        # Format for ADK tool return structure
        return {
            "result": disk_info,
            "stats": {
                "partition_count": len(disk_info["partitions"]),
                "total_space_gb": total_space / (1024**3),
                "used_space_gb": used_space / (1024**3),
                "overall_usage_percent": overall_usage_percent,
                "partitions_with_high_usage": len(partitions_over_threshold),
            },
            "additional_info": {
                "data_format": "dictionary",
                "collection_timestamp": time.time(),
                "high_usage_partitions": (
                    partitions_over_threshold if partitions_over_threshold else None
                ),
            },
        }
    except Exception as e:
        return {
            "result": {"error": f"Failed to gather disk information: {str(e)}"},
            "stats": {"success": False},
            "additional_info": {"error_type": str(type(e).__name__)},
        }
