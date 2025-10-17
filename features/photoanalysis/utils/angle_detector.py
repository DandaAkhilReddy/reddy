"""
Step 3: Multi-Photo Angle Detection
Uses MediaPipe Pose to detect front/side/back angles and validate poses
"""
import mediapipe as mp
import cv2
import numpy as np
from typing import Dict, List, Tuple
from ..models.schemas import AngleType, PhotoAngle


class AngleDetector:
    """Detects body angles and validates poses using MediaPipe"""

    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=True,
            model_complexity=2,  # Highest accuracy
            min_detection_confidence=0.5
        )

    def detect_angle(self, img_cv: np.ndarray) -> PhotoAngle:
        """
        Detect angle type (front/side/back) from image

        Args:
            img_cv: OpenCV image (BGR format)

        Returns:
            PhotoAngle object with detection results
        """
        # Convert BGR to RGB for MediaPipe
        img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)

        # Process image
        results = self.pose.process(img_rgb)

        if not results.pose_landmarks:
            return PhotoAngle(
                angle_type=AngleType.UNKNOWN,
                confidence=0.0,
                detected_pose_keypoints=0,
                is_standing=False
            )

        # Extract landmarks
        landmarks = results.pose_landmarks.landmark
        keypoint_count = len([lm for lm in landmarks if lm.visibility > 0.5])

        # Determine angle type
        angle_type, confidence = self._classify_angle(landmarks)

        # Check if standing
        is_standing = self._check_standing_pose(landmarks)

        return PhotoAngle(
            angle_type=angle_type,
            confidence=confidence,
            detected_pose_keypoints=keypoint_count,
            is_standing=is_standing
        )

    def _classify_angle(
        self,
        landmarks: List
    ) -> Tuple[AngleType, float]:
        """
        Classify image as front, side, or back based on landmark visibility

        Logic:
        - Front: Both shoulders visible, body is symmetric (left/right similar depth)
        - Side: One shoulder much more visible, profile view
        - Back: Both shoulders visible, but back-facing (nose not visible)

        Args:
            landmarks: MediaPipe pose landmarks

        Returns:
            Tuple of (angle_type, confidence)
        """
        # Key landmark indices
        NOSE = 0
        LEFT_SHOULDER = 11
        RIGHT_SHOULDER = 12
        LEFT_HIP = 23
        RIGHT_HIP = 24
        LEFT_ANKLE = 27
        RIGHT_ANKLE = 28

        # Get visibility scores
        nose_vis = landmarks[NOSE].visibility
        left_shoulder_vis = landmarks[LEFT_SHOULDER].visibility
        right_shoulder_vis = landmarks[RIGHT_SHOULDER].visibility
        left_hip_vis = landmarks[LEFT_HIP].visibility
        right_hip_vis = landmarks[RIGHT_HIP].visibility

        # Calculate symmetry (how similar left vs right visibility)
        shoulder_symmetry = 1.0 - abs(left_shoulder_vis - right_shoulder_vis)
        hip_symmetry = 1.0 - abs(left_hip_vis - right_hip_vis)
        overall_symmetry = (shoulder_symmetry + hip_symmetry) / 2

        # Calculate depth difference (Z-coordinate difference)
        shoulder_depth_diff = abs(
            landmarks[LEFT_SHOULDER].z - landmarks[RIGHT_SHOULDER].z
        )

        # Determine angle
        if shoulder_depth_diff > 0.15:
            # Side view: significant depth difference
            angle_type = AngleType.SIDE
            confidence = min(0.95, 0.5 + shoulder_depth_diff)

        elif nose_vis < 0.3 and overall_symmetry > 0.7:
            # Back view: symmetric but nose not visible
            angle_type = AngleType.BACK
            confidence = overall_symmetry

        elif nose_vis > 0.5 and overall_symmetry > 0.65:
            # Front view: nose visible and symmetric
            angle_type = AngleType.FRONT
            confidence = (nose_vis + overall_symmetry) / 2

        else:
            # Unclear angle
            angle_type = AngleType.UNKNOWN
            confidence = 0.3

        return angle_type, confidence

    def _check_standing_pose(self, landmarks: List) -> bool:
        """
        Check if person is standing upright with arms down

        Args:
            landmarks: MediaPipe pose landmarks

        Returns:
            True if standing correctly
        """
        # Key indices
        NOSE = 0
        LEFT_HIP = 23
        RIGHT_HIP = 24
        LEFT_ANKLE = 27
        RIGHT_ANKLE = 28
        LEFT_WRIST = 15
        RIGHT_WRIST = 16

        # Check vertical alignment (nose above hips above ankles)
        nose_y = landmarks[NOSE].y
        hip_y = (landmarks[LEFT_HIP].y + landmarks[RIGHT_HIP].y) / 2
        ankle_y = (landmarks[LEFT_ANKLE].y + landmarks[RIGHT_ANKLE].y) / 2

        # Y increases downward, so nose < hip < ankle
        vertical_alignment = (nose_y < hip_y < ankle_y)

        # Check wrists are below hips (arms down)
        left_wrist_y = landmarks[LEFT_WRIST].y
        right_wrist_y = landmarks[RIGHT_WRIST].y
        arms_down = (left_wrist_y > hip_y - 0.1 and right_wrist_y > hip_y - 0.1)

        # Check posture isn't too bent
        # Hip-to-nose vertical distance should be reasonable
        torso_height = hip_y - nose_y
        posture_good = 0.2 < torso_height < 0.6  # Normalized coordinates

        return vertical_alignment and arms_down and posture_good

    def validate_three_angles(
        self,
        photos: List[Tuple[np.ndarray, str]]
    ) -> Dict[str, PhotoAngle]:
        """
        Validate that we have all three required angles

        Args:
            photos: List of (img_cv, label) tuples

        Returns:
            Dict mapping label to PhotoAngle

        Raises:
            ValueError: If angles are missing or duplicated
        """
        results = {}
        detected_angles = []

        for img_cv, label in photos:
            photo_angle = self.detect_angle(img_cv)
            results[label] = photo_angle
            detected_angles.append(photo_angle.angle_type)

        # Check we have exactly one of each required angle
        required = {AngleType.FRONT, AngleType.SIDE, AngleType.BACK}
        detected_set = set(detected_angles)

        if AngleType.UNKNOWN in detected_set:
            raise ValueError("Could not detect angle for one or more photos")

        if not required.issubset(detected_set):
            missing = required - detected_set
            raise ValueError(f"Missing required angles: {missing}")

        # Check for duplicates (if 3 photos, all should be unique)
        if len(photos) == 3 and len(set(detected_angles)) != 3:
            raise ValueError("Detected duplicate angles. Please provide front, side, and back.")

        return results

    def close(self):
        """Clean up MediaPipe resources"""
        self.pose.close()


# Global detector instance
angle_detector = AngleDetector()


def detect_angles(
    images: List[Tuple[np.ndarray, str]]
) -> Dict[str, PhotoAngle]:
    """
    Convenience function for angle detection

    Args:
        images: List of (cv2_image, label) tuples

    Returns:
        Dict of angle detection results

    Raises:
        ValueError: If required angles missing
    """
    return angle_detector.validate_three_angles(images)
