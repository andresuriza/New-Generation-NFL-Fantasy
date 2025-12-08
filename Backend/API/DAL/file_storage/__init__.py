"""
File Storage Package

Contains services for handling file operations, including:
- Image upload and storage
- Thumbnail generation
- CDN management
- File validation and processing

Available services:
- cdn_service: Central service for image and file management
"""

from DAL.file_storage.cdn_service import cdn_service

__all__ = ['cdn_service']
