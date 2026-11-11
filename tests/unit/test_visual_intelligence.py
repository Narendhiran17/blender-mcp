"""Unit tests for Visual Intelligence analysis and evaluation."""

import struct
import tempfile
import zlib
from pathlib import Path
import pytest

from mcp_server.visual.analyzer import ImageAnalyzer
from mcp_server.visual.evaluator import VisualEvaluator


def _create_minimal_png(filepath: Path, width: int = 120, height: int = 120, color_byte: int = 180):
    """Create a valid uncompressed-scanline PNG file for testing."""
    signature = b"\x89PNG\r\n\x1a\n"
    # IHDR
    ihdr_data = struct.pack(">IIBBBBB", width, height, 8, 0, 0, 0, 0)
    ihdr_crc = zlib.crc32(b"IHDR" + ihdr_data)
    ihdr = struct.pack(">I", len(ihdr_data)) + b"IHDR" + ihdr_data + struct.pack(">I", ihdr_crc)

    # IDAT (Grayscale image with 0 filter byte per line)
    raw_lines = bytearray()
    for _ in range(height):
        raw_lines.append(0)  # filter type 0
        raw_lines.extend([color_byte] * width)

    compressed = zlib.compress(bytes(raw_lines))
    idat_crc = zlib.crc32(b"IDAT" + compressed)
    idat = struct.pack(">I", len(compressed)) + b"IDAT" + compressed + struct.pack(">I", idat_crc)

    # IEND
    iend_crc = zlib.crc32(b"IEND")
    iend = struct.pack(">I", 0) + b"IEND" + struct.pack(">I", iend_crc)

    with open(filepath, "wb") as f:
        f.write(signature + ihdr + idat + iend)


def test_image_analyzer_png():
    with tempfile.TemporaryDirectory() as td:
        img_path = Path(td) / "test_sample.png"
        _create_minimal_png(img_path, width=200, height=100, color_byte=128)

        analysis = ImageAnalyzer.analyze_image(str(img_path))
        assert analysis["format"] == "PNG"
        assert analysis["width"] == 200
        assert analysis["height"] == 100
        assert analysis["aspect_ratio"] == 2.0
        assert analysis["is_empty"] is False
        assert 0.4 <= analysis["mean_luminance"] <= 0.6


def test_visual_evaluator_passes():
    with tempfile.TemporaryDirectory() as td:
        img_path = Path(td) / "good_render.png"
        _create_minimal_png(img_path, width=320, height=240, color_byte=150)

        result = VisualEvaluator.evaluate(
            str(img_path),
            expected_min_width=200,
            expected_min_height=150,
        )
        assert result["verdict"] == "PASS"
        assert result["passes_quality_gate"] is True
        assert len(result["errors"]) == 0


def test_visual_evaluator_dark_warning():
    with tempfile.TemporaryDirectory() as td:
        dark_path = Path(td) / "dark_render.png"
        _create_minimal_png(dark_path, width=320, height=240, color_byte=2)

        result = VisualEvaluator.evaluate(str(dark_path))
        assert result["verdict"] == "WARN"
        assert any("dark" in w.lower() for w in result["warnings"])
