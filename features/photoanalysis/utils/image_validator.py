"""
Step 1: Photo Upload Quality Validation
Validates uploaded images meet quality standards before processing
"""
import cv2
import numpy as np
from PIL import Image
from PIL.ExifTags import TAGS
from typing import Tuple, Dict, Any
from pathlib import Path
import io

from ..models.schemas import ImageQuality
from ..config.settings import settings


class ImageValidator:
    """Validates image quality for body scan analysis"""

    def __init__(self):
        self.min_resolution = settings.min_image_resolution
        self.max_resolution = settings.max_image_resolution
        self.min_file_size_kb = settings.min_image_size_kb
        self.max_file_size_mb = settings.max_image_size_mb
        self.min_sharpness = settings.min_sharpness_score

    def validate_image(self, image_data: bytes, filename: str) -> ImageQuality:
        """
        Comprehensive image quality validation

        Args:
            image_data: Raw image bytes
            filename: Original filename

        Returns:
            ImageQuality object with validation results
        """
        # Load image
        img_pil = Image.open(io.BytesIO(image_data))
        img_cv = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_COLOR)

        # Basic metrics
        width, height = img_pil.size
        file_size_kb = len(image_data) / 1024
        img_format = img_pil.format or self._guess_format(filename)

        # EXIF data
        exif_data = self._extract_exif(img_pil)
        has_exif = len(exif_data) > 0
        orientation = exif_data.get("Orientation")

        # Sharpness check
        sharpness_score = self._calculate_sharpness(img_cv)

        # Quality score calculation
        quality_score = self._calculate_quality_score(
            width, height, file_size_kb, sharpness_score
        )

        # Validation
        is_valid = self._is_valid(width, height, file_size_kb, sharpness_score)

        return ImageQuality(
            width=width,
            height=height,
            file_size_kb=round(file_size_kb, 2),
            format=img_format,
            sharpness_score=round(sharpness_score, 2),
            has_exif=has_exif,
            orientation=orientation,
            is_valid=is_valid,
            quality_score=round(quality_score, 2)
        )

    def _calculate_sharpness(self, img_cv: np.ndarray) -> float:
        """
        Calculate image sharpness using Laplacian variance

        Args:
            img_cv: OpenCV image array

        Returns:
            Sharpness score (higher = sharper)
        """
        if img_cv is None or img_cv.size == 0:
            return 0.0

        # Convert to grayscale
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)

        # Calculate Laplacian
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)

        # Return variance as sharpness metric
        return float(laplacian.var())

    def _extract_exif(self, img_pil: Image.Image) -> Dict[str, Any]:
        """
        Extract EXIF metadata from image

        Args:
            img_pil: PIL Image object

        Returns:
            Dictionary of EXIF data
        """
        exif_data = {}

        try:
            exif = img_pil._getexif()
            if exif:
                for tag_id, value in exif.items():
                    tag = TAGS.get(tag_id, tag_id)
                    exif_data[tag] = value
        except (AttributeError, KeyError, IndexError):
            pass

        return exif_data

    def _calculate_quality_score(
        self,
        width: int,
        height: int,
        file_size_kb: float,
        sharpness: float
    ) -> float:
        """
        Calculate overall quality score (0-100)

        Factors:
        - Resolution (40%): Higher is better within reasonable range
        - File size (20%): Should be adequate for resolution
        - Sharpness (40%): Critical for body detection
        """
        # Resolution score (target ~1024-2048 on longest side)
        longest = max(width, height)
        if longest < self.min_resolution[1]:
            res_score = 0
        elif longest > self.max_resolution[1]:
            res_score = 70  # Too high, but workable
        elif longest >= 1024:
            res_score = 100
        else:
            res_score = (longest / 1024) * 100

        # File size score (relative to resolution)
        pixels = width * height
        expected_size_kb = pixels / 1000  # Rough estimate
        size_ratio = file_size_kb / expected_size_kb if expected_size_kb > 0 else 0

        if 0.5 <= size_ratio <= 2.0:
            size_score = 100
        elif size_ratio < 0.1:
            size_score = 30  # Too compressed
        elif size_ratio > 5:
            size_score = 70  # Inefficient but ok
        else:
            size_score = 80

        # Sharpness score (normalize to 100)
        # Typical sharp images: 100-1000+, blurry: 0-100
        if sharpness >= 200:
            sharp_score = 100
        elif sharpness >= self.min_sharpness:
            sharp_score = (sharpness / 200) * 100
        else:
            sharp_score = (sharpness / self.min_sharpness) * 50

        # Weighted average
        quality = (res_score * 0.4) + (size_score * 0.2) + (sharp_score * 0.4)

        return min(100, max(0, quality))

    def _is_valid(
        self,
        width: int,
        height: int,
        file_size_kb: float,
        sharpness: float
    ) -> bool:
        """
        Determine if image passes validation

        Args:
            width: Image width in pixels
            height: Image height in pixels
            file_size_kb: File size in kilobytes
            sharpness: Sharpness score

        Returns:
            True if image is valid for analysis
        """
        # Check resolution
        if width < self.min_resolution[0] or height < self.min_resolution[1]:
            return False

        if width > self.max_resolution[0] or height > self.max_resolution[1]:
            return False

        # Check file size
        if file_size_kb < self.min_file_size_kb:
            return False

        if file_size_kb > (self.max_file_size_mb * 1024):
            return False

        # Check sharpness
        if sharpness < self.min_sharpness:
            return False

        return True

    def _guess_format(self, filename: str) -> str:
        """Guess image format from filename"""
        ext = Path(filename).suffix.lower().lstrip('.')
        format_map = {
            'jpg': 'JPEG',
            'jpeg': 'JPEG',
            'png': 'PNG',
            'heic': 'HEIC',
            'heif': 'HEIF',
        }
        return format_map.get(ext, 'UNKNOWN')


# Global validator instance
image_validator = ImageValidator()


def validate_image(image_data: bytes, filename: str) -> ImageQuality:
    """
    Convenience function for image validation

    Args:
        image_data: Raw image bytes
        filename: Original filename

    Returns:
        ImageQuality validation result
    """
    return image_validator.validate_image(image_data, filename)
