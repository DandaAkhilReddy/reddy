"""
Step 2: Image Preprocessing Pipeline
Auto-rotate, normalize brightness/contrast, resize, and compress images
"""
import cv2
import numpy as np
from PIL import Image
from typing import Tuple, Optional
import io

from ..config.settings import settings


class ImageProcessor:
    """Preprocesses images for AI analysis"""

    def __init__(self):
        self.optimal_size = settings.optimal_image_size
        self.compression_quality = settings.image_quality

    def process_image(
        self,
        image_data: bytes,
        orientation: Optional[int] = None
    ) -> Tuple[bytes, np.ndarray]:
        """
        Complete preprocessing pipeline

        Args:
            image_data: Raw image bytes
            orientation: EXIF orientation value (from Step 1)

        Returns:
            Tuple of (processed_bytes, cv2_image_array)
        """
        # Load image
        img_pil = Image.open(io.BytesIO(image_data))

        # Step 2.1: Auto-rotate based on EXIF
        if orientation:
            img_pil = self._apply_exif_rotation(img_pil, orientation)

        # Convert to OpenCV format for processing
        img_cv = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

        # Step 2.2: Normalize brightness and contrast
        img_cv = self._normalize_brightness_contrast(img_cv)

        # Step 2.3: Resize to optimal dimensions
        img_cv = self._resize_image(img_cv)

        # Step 2.4: Compress to efficient size
        processed_bytes = self._compress_image(img_cv)

        return processed_bytes, img_cv

    def _apply_exif_rotation(self, img: Image.Image, orientation: int) -> Image.Image:
        """
        Apply EXIF orientation correction

        EXIF Orientation values:
        1 = Normal
        2 = Mirror horizontal
        3 = Rotate 180
        4 = Mirror vertical
        5 = Mirror horizontal + rotate 270 CW
        6 = Rotate 90 CW
        7 = Mirror horizontal + rotate 90 CW
        8 = Rotate 270 CW
        """
        rotation_map = {
            1: lambda img: img,
            2: lambda img: img.transpose(Image.FLIP_LEFT_RIGHT),
            3: lambda img: img.rotate(180, expand=True),
            4: lambda img: img.transpose(Image.FLIP_TOP_BOTTOM),
            5: lambda img: img.transpose(Image.FLIP_LEFT_RIGHT).rotate(270, expand=True),
            6: lambda img: img.rotate(270, expand=True),
            7: lambda img: img.transpose(Image.FLIP_LEFT_RIGHT).rotate(90, expand=True),
            8: lambda img: img.rotate(90, expand=True),
        }

        transform = rotation_map.get(orientation, lambda img: img)
        return transform(img)

    def _normalize_brightness_contrast(self, img_cv: np.ndarray) -> np.ndarray:
        """
        Normalize brightness and contrast using histogram equalization

        Args:
            img_cv: OpenCV image (BGR format)

        Returns:
            Normalized image
        """
        # Convert to LAB color space
        lab = cv2.cvtColor(img_cv, cv2.COLOR_BGR2LAB)

        # Split channels
        l, a, b = cv2.split(lab)

        # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization) to L channel
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l_equalized = clahe.apply(l)

        # Merge channels
        lab_equalized = cv2.merge([l_equalized, a, b])

        # Convert back to BGR
        img_normalized = cv2.cvtColor(lab_equalized, cv2.COLOR_LAB2BGR)

        return img_normalized

    def _resize_image(self, img_cv: np.ndarray) -> np.ndarray:
        """
        Resize image to optimal dimensions while preserving aspect ratio

        Target: max dimension = optimal_size (default 1024px)

        Args:
            img_cv: OpenCV image

        Returns:
            Resized image
        """
        height, width = img_cv.shape[:2]
        max_dimension = max(height, width)

        # Only resize if larger than optimal
        if max_dimension > self.optimal_size:
            # Calculate scale factor
            scale = self.optimal_size / max_dimension

            # Calculate new dimensions
            new_width = int(width * scale)
            new_height = int(height * scale)

            # Resize with high-quality interpolation
            img_resized = cv2.resize(
                img_cv,
                (new_width, new_height),
                interpolation=cv2.INTER_LANCZOS4
            )

            return img_resized

        return img_cv

    def _compress_image(self, img_cv: np.ndarray) -> bytes:
        """
        Compress image to JPEG with specified quality

        Args:
            img_cv: OpenCV image

        Returns:
            Compressed image as bytes
        """
        # Encode as JPEG
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), self.compression_quality]
        success, encoded = cv2.imencode('.jpg', img_cv, encode_param)

        if not success:
            raise ValueError("Failed to encode image")

        return encoded.tobytes()

    def process_batch(
        self,
        images: list[Tuple[bytes, Optional[int]]]
    ) -> list[Tuple[bytes, np.ndarray]]:
        """
        Process multiple images in batch

        Args:
            images: List of (image_data, orientation) tuples

        Returns:
            List of (processed_bytes, cv2_array) tuples
        """
        processed = []
        for image_data, orientation in images:
            processed_bytes, img_cv = self.process_image(image_data, orientation)
            processed.append((processed_bytes, img_cv))

        return processed


# Global processor instance
image_processor = ImageProcessor()


def process_image(
    image_data: bytes,
    orientation: Optional[int] = None
) -> Tuple[bytes, np.ndarray]:
    """
    Convenience function for image preprocessing

    Args:
        image_data: Raw image bytes
        orientation: EXIF orientation value

    Returns:
        Tuple of (processed_bytes, cv2_image)
    """
    return image_processor.process_image(image_data, orientation)
