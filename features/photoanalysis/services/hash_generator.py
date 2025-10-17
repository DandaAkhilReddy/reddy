"""
Composition Hash Generator (Step 13)
Generates cryptographic fingerprint of body composition
"""
import hashlib
import json
from typing import Dict, Optional
from ..models.schemas import BodyMeasurements, BodyRatios


def generate_composition_hash(
    measurements: BodyMeasurements,
    ratios: BodyRatios
) -> str:
    """
    Generate deterministic SHA-256 hash from body composition

    Creates a unique fingerprint based on all measurements and ratios.
    Truncated to 6 uppercase alphanumeric characters.

    Args:
        measurements: BodyMeasurements object
        ratios: BodyRatios object

    Returns:
        6-character uppercase hash (e.g., "A3F7C2")
    """
    # Create deterministic composition string
    composition_data = {
        # Round measurements to 1 decimal to reduce hash collisions from tiny variations
        "chest": round(measurements.chest_circumference_cm, 1),
        "waist": round(measurements.waist_circumference_cm, 1),
        "hips": round(measurements.hip_circumference_cm, 1),
        "bicep": round(measurements.bicep_circumference_cm, 1),
        "thigh": round(measurements.thigh_circumference_cm, 1),
        "body_fat": round(measurements.body_fat_percent, 1),

        # Key ratios (rounded to 2 decimals)
        "shoulder_waist_ratio": round(ratios.shoulder_to_waist_ratio, 2),
        "waist_hip_ratio": round(ratios.waist_to_hip_ratio, 2),
        "chest_waist_ratio": round(ratios.chest_to_waist_ratio, 2),
    }

    # Convert to JSON string (sorted keys for determinism)
    composition_string = json.dumps(composition_data, sort_keys=True)

    # Generate SHA-256 hash
    hash_object = hashlib.sha256(composition_string.encode('utf-8'))
    full_hash = hash_object.hexdigest()

    # Take first 6 characters and convert to uppercase
    short_hash = full_hash[:6].upper()

    return short_hash


def generate_detailed_hash(
    measurements: BodyMeasurements,
    ratios: BodyRatios,
    include_optionals: bool = True
) -> str:
    """
    Generate more detailed hash including optional measurements

    Args:
        measurements: BodyMeasurements object
        ratios: BodyRatios object
        include_optionals: Include optional measurements (calf, shoulders)

    Returns:
        6-character hash
    """
    composition_data = {
        "chest": round(measurements.chest_circumference_cm, 1),
        "waist": round(measurements.waist_circumference_cm, 1),
        "hips": round(measurements.hip_circumference_cm, 1),
        "bicep": round(measurements.bicep_circumference_cm, 1),
        "thigh": round(measurements.thigh_circumference_cm, 1),
        "body_fat": round(measurements.body_fat_percent, 1),
        "shoulder_waist_ratio": round(ratios.shoulder_to_waist_ratio, 2),
        "waist_hip_ratio": round(ratios.waist_to_hip_ratio, 2),
    }

    # Add optional measurements if requested
    if include_optionals:
        if measurements.calf_circumference_cm:
            composition_data["calf"] = round(measurements.calf_circumference_cm, 1)

        if measurements.shoulder_width_cm:
            composition_data["shoulders"] = round(measurements.shoulder_width_cm, 1)

        if measurements.estimated_weight_kg:
            composition_data["weight"] = round(measurements.estimated_weight_kg, 1)

    # Generate hash
    composition_string = json.dumps(composition_data, sort_keys=True)
    hash_object = hashlib.sha256(composition_string.encode('utf-8'))
    return hash_object.hexdigest()[:6].upper()


def validate_hash_format(hash_str: str) -> bool:
    """
    Validate that a hash is in correct format

    Args:
        hash_str: Hash string to validate

    Returns:
        True if valid format
    """
    if not hash_str:
        return False

    # Should be 6 characters, uppercase alphanumeric
    if len(hash_str) != 6:
        return False

    if not hash_str.isalnum():
        return False

    if not hash_str.isupper():
        return False

    return True


def check_hash_similarity(hash1: str, hash2: str) -> float:
    """
    Calculate similarity between two hashes

    Args:
        hash1: First hash
        hash2: Second hash

    Returns:
        Similarity score 0-100 (100 = identical)
    """
    if not validate_hash_format(hash1) or not validate_hash_format(hash2):
        return 0.0

    # Count matching characters
    matches = sum(1 for c1, c2 in zip(hash1, hash2) if c1 == c2)

    # Calculate percentage
    similarity = (matches / 6) * 100

    return similarity


def generate_hash_with_salt(
    measurements: BodyMeasurements,
    ratios: BodyRatios,
    salt: str = ""
) -> str:
    """
    Generate hash with optional salt for uniqueness

    Useful if you want to ensure different hashes for the same composition
    taken at different times.

    Args:
        measurements: BodyMeasurements object
        ratios: BodyRatios object
        salt: Additional string to add to hash (e.g., timestamp)

    Returns:
        6-character hash
    """
    composition_data = {
        "chest": round(measurements.chest_circumference_cm, 1),
        "waist": round(measurements.waist_circumference_cm, 1),
        "hips": round(measurements.hip_circumference_cm, 1),
        "bicep": round(measurements.bicep_circumference_cm, 1),
        "thigh": round(measurements.thigh_circumference_cm, 1),
        "body_fat": round(measurements.body_fat_percent, 1),
        "shoulder_waist_ratio": round(ratios.shoulder_to_waist_ratio, 2),
    }

    # Add salt if provided
    if salt:
        composition_data["salt"] = salt

    composition_string = json.dumps(composition_data, sort_keys=True)
    hash_object = hashlib.sha256(composition_string.encode('utf-8'))
    return hash_object.hexdigest()[:6].upper()


def detect_hash_collision(
    new_hash: str,
    existing_hashes: list,
    threshold: float = 100.0
) -> Optional[str]:
    """
    Detect if new hash collides with existing hashes

    Args:
        new_hash: Newly generated hash
        existing_hashes: List of existing hashes for user
        threshold: Similarity threshold to consider collision (default 100 = exact match)

    Returns:
        Colliding hash if found, None otherwise
    """
    for existing_hash in existing_hashes:
        similarity = check_hash_similarity(new_hash, existing_hash)

        if similarity >= threshold:
            return existing_hash

    return None


def explain_hash_components(
    measurements: BodyMeasurements,
    ratios: BodyRatios
) -> Dict[str, any]:
    """
    Explain what went into the hash calculation

    Useful for debugging or showing users what makes them unique.

    Args:
        measurements: BodyMeasurements object
        ratios: BodyRatios object

    Returns:
        Dictionary explaining hash components
    """
    components = {
        "measurements": {
            "chest_cm": round(measurements.chest_circumference_cm, 1),
            "waist_cm": round(measurements.waist_circumference_cm, 1),
            "hips_cm": round(measurements.hip_circumference_cm, 1),
            "bicep_cm": round(measurements.bicep_circumference_cm, 1),
            "thigh_cm": round(measurements.thigh_circumference_cm, 1),
            "body_fat_percent": round(measurements.body_fat_percent, 1),
        },
        "ratios": {
            "shoulder_to_waist": round(ratios.shoulder_to_waist_ratio, 2),
            "waist_to_hip": round(ratios.waist_to_hip_ratio, 2),
            "chest_to_waist": round(ratios.chest_to_waist_ratio, 2),
        },
        "hash": generate_composition_hash(measurements, ratios)
    }

    # Add human-readable summary
    components["summary"] = (
        f"Your body composition fingerprint is based on {len(components['measurements'])} "
        f"measurements and {len(components['ratios'])} key ratios, "
        f"creating a unique identifier: {components['hash']}"
    )

    return components


def validate_hash_uniqueness(
    hash_str: str,
    user_id: str,
    existing_scans: list = None
) -> bool:
    """
    Validate that hash is unique for this user

    In production, this would query Firestore for user's previous scans.
    For now, accepts a list of existing scan hashes.

    Args:
        hash_str: Hash to validate
        user_id: User ID
        existing_scans: List of existing scan hashes (optional)

    Returns:
        True if hash is unique (no exact collision)
    """
    if not existing_scans:
        # No existing scans, hash is unique
        return True

    # Check for exact matches
    collision = detect_hash_collision(hash_str, existing_scans, threshold=100.0)

    if collision:
        # Exact collision found
        return False

    return True
