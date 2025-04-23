"""
System Information Tools Package

This package provides tools for gathering system information in an OS-independent way.
"""

from .tools import get_cpu_info, get_disk_info, get_memory_info

__all__ = ["get_cpu_info", "get_memory_info", "get_disk_info"]
