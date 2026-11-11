"""Pure-Python image analyzer for rendered preview verification."""

import os
import struct
import zlib
from pathlib import Path
from typing import Any, Dict, Optional


class ImageAnalyzer:
    """Zero-dependency image inspector and metric extractor."""

    @staticmethod
    def analyze_image(filepath: str) -> Dict[str, Any]:
        """Extract dimensions, format, file size, and brightness metrics from an image file."""
        path = Path(filepath).resolve()
        if not path.exists():
            raise FileNotFoundError(f"Image file '{filepath}' does not exist")

        file_size = path.stat().st_size
        with open(path, "rb") as f:
            header = f.read(64)
            f.seek(0)
            full_data = f.read()

        # PNG format
        if header.startswith(b"\x89PNG\r\n\x1a\n"):
            w, h, bit_depth, color_type = struct.unpack(">IIBB", full_data[16:26])
            luminance_est = ImageAnalyzer._estimate_png_luminance(full_data, w, h, color_type)
            aspect_ratio = round(w / h, 3) if h > 0 else 0.0

            return {
                "format": "PNG",
                "filepath": str(path),
                "width": w,
                "height": h,
                "aspect_ratio": aspect_ratio,
                "file_size_bytes": file_size,
                "bit_depth": bit_depth,
                "color_type": color_type,
                "mean_luminance": luminance_est,
                "is_empty": file_size == 0,
            }

        # JPEG format
        elif header.startswith(b"\xff\xd8"):
            w, h = ImageAnalyzer._parse_jpeg_dimensions(full_data)
            aspect_ratio = round(w / h, 3) if h and h > 0 else 0.0
            return {
                "format": "JPEG",
                "filepath": str(path),
                "width": w,
                "height": h,
                "aspect_ratio": aspect_ratio,
                "file_size_bytes": file_size,
                "mean_luminance": 0.5,  # Fallback estimate
                "is_empty": file_size == 0,
            }

        else:
            return {
                "format": "UNKNOWN",
                "filepath": str(path),
                "file_size_bytes": file_size,
                "is_empty": file_size == 0,
            }

    @staticmethod
    def _estimate_png_luminance(data: bytes, width: int, height: int, color_type: int) -> float:
        """Decompress IDAT chunks to compute sample mean luminance (0.0 to 1.0)."""
        try:
            idat_parts = []
            offset = 8
            while offset < len(data):
                length = struct.unpack(">I", data[offset:offset+4])[0]
                chunk_type = data[offset+4:offset+8]
                if chunk_type == b"IDAT":
                    idat_parts.append(data[offset+8:offset+8+length])
                offset += 12 + length

            if not idat_parts:
                return 0.5

            raw_scanlines = zlib.decompress(b"".join(idat_parts))
            # Sample first 2000 bytes
            sample = raw_scanlines[:min(len(raw_scanlines), 2000)]
            if not sample:
                return 0.0
            avg_val = sum(sample) / len(sample)
            return round(avg_val / 255.0, 3)
        except Exception:
            return 0.5

    @staticmethod
    def _parse_jpeg_dimensions(data: bytes) -> tuple:
        """Parse SOF0 marker for JPEG width and height."""
        offset = 2
        while offset < len(data) - 8:
            marker, length = struct.unpack(">HH", data[offset:offset+4])
            if 0xFFC0 <= marker <= 0xFFC3:
                h, w = struct.unpack(">HH", data[offset+5:offset+9])
                return w, h
            offset += 2 + length
        return 0, 0
