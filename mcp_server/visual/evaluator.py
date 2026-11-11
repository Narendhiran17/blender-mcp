"""Visual Evaluator comparing preview renders against acceptance criteria."""

from typing import Any, Dict, List, Optional
from .analyzer import ImageAnalyzer


class VisualEvaluator:
    """Evaluates rendered preview images for quality, exposure, and composition."""

    @staticmethod
    def evaluate(
        filepath: str,
        expected_min_width: int = 100,
        expected_min_height: int = 100,
        min_luminance: float = 0.04,
        max_luminance: float = 0.96,
    ) -> Dict[str, Any]:
        """Evaluate an image against deterministic and visual exposure criteria."""
        analysis = ImageAnalyzer.analyze_image(filepath)

        verdict = "PASS"
        warnings: List[str] = []
        errors: List[str] = []

        # Check dimensions
        width = analysis.get("width", 0)
        height = analysis.get("height", 0)
        if width < expected_min_width or height < expected_min_height:
            errors.append(f"Image resolution ({width}x{height}) is below expected minimum ({expected_min_width}x{expected_min_height})")
            verdict = "FAIL"

        # Check empty file
        if analysis.get("is_empty"):
            errors.append("Render output file is empty or corrupted")
            verdict = "FAIL"

        # Check luminance
        lum = analysis.get("mean_luminance", 0.5)
        if lum < min_luminance:
            warnings.append(f"Image is exceptionally dark (luminance: {lum}). Scene lights may be missing, too weak, or camera is obstructed.")
            if verdict == "PASS":
                verdict = "WARN"
        elif lum > max_luminance:
            warnings.append(f"Image is overexposed/blown out (luminance: {lum}). Lights or world background may be too intense.")
            if verdict == "PASS":
                verdict = "WARN"

        return {
            "filepath": filepath,
            "verdict": verdict,
            "metrics": analysis,
            "warnings": warnings,
            "errors": errors,
            "passes_quality_gate": verdict in ("PASS", "WARN"),
        }
