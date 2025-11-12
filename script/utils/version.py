"""
Version management for Nidec Commander CDE application.

This module provides a centralized version tracking system following Semantic Versioning 2.0.0
(https://semver.org/) for the Nidec Commander CDE project.
"""

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union

# Version information follows Semantic Versioning 2.0.0 (https://semver.org/)
VERSION_MAJOR = 0
VERSION_MINOR = 0  # Added improved update system and documentation
VERSION_PATCH = 5  # Additional version qualifiers
VERSION_QUALIFIER = 'beta'  # Could be 'alpha', 'beta', 'rc', or ''
VERSION_METADATA = ''  # Build metadata (e.g., 'build.1')

@dataclass
class VersionInfo:
    """Dataclass to hold version information."""
    major: int
    minor: int
    patch: int
    qualifier: str = ''
    metadata: str = ''

    def __str__(self) -> str:
        """Return the version as a string."""
        return self.full_version

    @property
    def full_version(self) -> str:
        """Generate a full version string."""
        version_parts = [str(self.major), str(self.minor), str(self.patch)]
        version_str = '.'.join(version_parts)
        
        if self.qualifier:
            version_str += f'-{self.qualifier}'
        
        if self.metadata:
            version_str += f'+{self.metadata}'
        
        return version_str
    
    @property
    def is_stable(self) -> bool:
        """Check if this is a stable release (no qualifier or metadata)."""
        return not (self.qualifier or self.metadata)
    
    @property
    def is_prerelease(self) -> bool:
        """Check if this is a pre-release version."""
        return bool(self.qualifier)
    
    def to_dict(self) -> Dict[str, Union[int, str]]:
        """Convert version info to a dictionary."""
        return {
            'major': self.major,
            'minor': self.minor,
            'patch': self.patch,
            'qualifier': self.qualifier,
            'metadata': self.metadata,
            'full_version': self.full_version,
            'is_stable': self.is_stable,
            'is_prerelease': self.is_prerelease,
            'build_date': get_build_date(),
            'build_year': datetime.now().year
        }

def get_version_info() -> Dict[str, Union[int, str, bool]]:
    """
    Get detailed version information.
    
    Returns:
        Dict containing comprehensive version information.
    """
    version = VersionInfo(
        major=VERSION_MAJOR,
        minor=VERSION_MINOR,
        patch=VERSION_PATCH,
        qualifier=VERSION_QUALIFIER,
        metadata=VERSION_METADATA
    )
    return version.to_dict()

def get_version() -> str:
    """
    Get the full version string.
    
    Returns:
        str: Formatted version string (e.g., '1.2.3-beta')
    """
    return str(VersionInfo(
        major=VERSION_MAJOR,
        minor=VERSION_MINOR,
        patch=VERSION_PATCH,
        qualifier=VERSION_QUALIFIER,
        metadata=VERSION_METADATA
    ))

def parse_version(version_str: str) -> VersionInfo:
    """
    Parse a version string into a VersionInfo object.
    
    Args:
        version_str: Version string to parse (e.g., '1.2.3-beta+123')
        
    Returns:
        VersionInfo: Parsed version information
        
    Raises:
        ValueError: If the version string is invalid
    """
    # Match semver pattern (major.minor.patch[-qualifier][+metadata])
    match = re.match(
        r'^(\d+)\.(\d+)\.(\d+)(?:-([\w\.]+))?(?:\+([\w\.]+))?$',
        version_str
    )
    
    if not match:
        raise ValueError(f"Invalid version string: {version_str}")
    
    major, minor, patch, qualifier, metadata = match.groups()
    return VersionInfo(
        major=int(major),
        minor=int(minor),
        patch=int(patch),
        qualifier=qualifier or '',
        metadata=metadata or ''
    )

def check_version_compatibility(
    min_version: str,
    current_version: Optional[str] = None
) -> bool:
    """
    Check if the current version meets the minimum required version.
    
    Args:
        min_version: Minimum version to compare against (e.g., '1.2.3')
        current_version: Version to check (defaults to current version)
        
    Returns:
        bool: True if current version is compatible, False otherwise
        
    Raises:
        ValueError: If version strings are invalid
    """
    try:
        current = parse_version(current_version if current_version else get_version())
        minimum = parse_version(min_version)
        
        # Compare major, minor, patch versions
        current_tuple = (current.major, current.minor, current.patch)
        min_tuple = (minimum.major, minimum.minor, minimum.patch)
        
        return current_tuple >= min_tuple
    except (ValueError, AttributeError) as e:
        raise ValueError(f"Invalid version string: {e}")

def get_build_date() -> str:
    """
    Get the build date in ISO format.
    
    Returns:
        str: ISO formatted build date (YYYY-MM-DD)
    """
    return datetime.now().strftime("%Y-%m-%d")

# Module-level attributes for backward compatibility
__version__ = get_version()
__version_info__ = get_version_info()

# Example usage
if __name__ == "__main__":
    print(f"Version: {__version__}")
    print(f"Version Info: {__version_info__}")
    print(f"Is stable: {__version_info__['is_stable']}")
    print(f"Is pre-release: {__version_info__['is_prerelease']}")
    print(f"Build date: {__version_info__['build_date']}")
