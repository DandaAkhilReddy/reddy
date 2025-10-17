"""
Unique ID Generator (Step 15)
Generates human-readable unique body signature IDs
"""
import re
from typing import Dict, Optional
from ..models.schemas import BodyType


def generate_body_signature_id(
    body_type: BodyType,
    body_fat_percent: float,
    composition_hash: str,
    adonis_index: float
) -> str:
    """
    Generate unique body signature ID

    Format: {BodyType}-BF{%}-{Hash}-AI{ratio}
    Example: VTaper-BF15.5-A3F7C2-AI1.54

    Args:
        body_type: Classified body type
        body_fat_percent: Body fat percentage
        composition_hash: 6-character composition hash
        adonis_index: Adonis Index (shoulder:waist ratio)

    Returns:
        Formatted body signature ID string
    """
    # Format body type (remove spaces, use camelCase)
    body_type_str = format_body_type(body_type)

    # Format body fat (1 decimal)
    bf_str = f"BF{body_fat_percent:.1f}"

    # Hash (already 6 chars uppercase)
    hash_str = composition_hash

    # Format Adonis Index (2 decimals)
    ai_str = f"AI{adonis_index:.2f}"

    # Combine all components
    signature_id = f"{body_type_str}-{bf_str}-{hash_str}-{ai_str}"

    return signature_id


def format_body_type(body_type: BodyType) -> str:
    """
    Format body type for signature ID

    Args:
        body_type: BodyType enum

    Returns:
        Formatted string (camelCase, no spaces)
    """
    # Convert BodyType enum to string
    type_str = body_type.value

    # Remove spaces and use camelCase
    # e.g., "V-Taper" -> "VTaper", "Balanced" -> "Balanced"
    formatted = type_str.replace(" ", "").replace("-", "")

    return formatted


def parse_body_signature_id(signature_id: str) -> Optional[Dict[str, any]]:
    """
    Parse body signature ID back into components

    Args:
        signature_id: Body signature ID string

    Returns:
        Dictionary with parsed components, or None if invalid
    """
    # Expected format: BodyType-BFX.X-XXXXXX-AIX.XX
    # Example: VTaper-BF15.5-A3F7C2-AI1.54

    # Regex pattern to match the format
    pattern = r'^([A-Za-z]+)-BF(\d+\.\d+)-([A-F0-9]{6})-AI(\d+\.\d+)$'

    match = re.match(pattern, signature_id)

    if not match:
        return None

    body_type_str, bf_str, hash_str, ai_str = match.groups()

    try:
        parsed = {
            "body_type": body_type_str,
            "body_fat_percent": float(bf_str),
            "composition_hash": hash_str,
            "adonis_index": float(ai_str),
            "original_id": signature_id
        }
        return parsed

    except ValueError:
        return None


def validate_signature_id_format(signature_id: str) -> bool:
    """
    Validate that signature ID is in correct format

    Args:
        signature_id: Signature ID to validate

    Returns:
        True if valid format
    """
    parsed = parse_body_signature_id(signature_id)
    return parsed is not None


def generate_short_id(signature_id: str) -> str:
    """
    Generate shortened version of signature ID

    Takes just the hash component for brevity.
    Example: "VTaper-BF15.5-A3F7C2-AI1.54" -> "A3F7C2"

    Args:
        signature_id: Full signature ID

    Returns:
        6-character short ID (the hash)
    """
    parsed = parse_body_signature_id(signature_id)

    if parsed:
        return parsed["composition_hash"]

    # Fallback: try to extract hash directly
    # Hash is always 6 uppercase alphanumeric chars
    match = re.search(r'[A-F0-9]{6}', signature_id)
    if match:
        return match.group(0)

    return "INVALID"


def compare_signature_ids(id1: str, id2: str) -> Dict[str, any]:
    """
    Compare two signature IDs to analyze changes

    Args:
        id1: First signature ID
        id2: Second signature ID

    Returns:
        Dictionary with comparison results
    """
    parsed1 = parse_body_signature_id(id1)
    parsed2 = parse_body_signature_id(id2)

    if not parsed1 or not parsed2:
        return {"error": "Invalid signature ID format"}

    comparison = {
        "body_type_changed": parsed1["body_type"] != parsed2["body_type"],
        "body_fat_change": parsed2["body_fat_percent"] - parsed1["body_fat_percent"],
        "adonis_index_change": parsed2["adonis_index"] - parsed1["adonis_index"],
        "composition_changed": parsed1["composition_hash"] != parsed2["composition_hash"]
    }

    # Add interpretations
    if comparison["body_fat_change"] < -1:
        comparison["body_fat_interpretation"] = f"Lost {abs(comparison['body_fat_change']):.1f}% body fat"
    elif comparison["body_fat_change"] > 1:
        comparison["body_fat_interpretation"] = f"Gained {comparison['body_fat_change']:.1f}% body fat"
    else:
        comparison["body_fat_interpretation"] = "Minimal body fat change"

    if comparison["adonis_index_change"] > 0.05:
        comparison["proportion_interpretation"] = "Improved shoulder:waist ratio (better V-taper)"
    elif comparison["adonis_index_change"] < -0.05:
        comparison["proportion_interpretation"] = "Decreased shoulder:waist ratio"
    else:
        comparison["proportion_interpretation"] = "Proportions relatively unchanged"

    return comparison


def get_signature_id_insights(signature_id: str) -> Dict[str, str]:
    """
    Get human-readable insights from signature ID

    Args:
        signature_id: Body signature ID

    Returns:
        Dictionary of insights
    """
    parsed = parse_body_signature_id(signature_id)

    if not parsed:
        return {"error": "Invalid signature ID"}

    insights = {
        "body_type": f"Body Type: {parsed['body_type']}",
        "body_composition": f"Body Fat: {parsed['body_fat_percent']}%",
        "proportions": f"Adonis Index: {parsed['adonis_index']} (shoulder:waist ratio)",
        "unique_id": f"Composition ID: {parsed['composition_hash']}"
    }

    # Add body fat category
    bf = parsed["body_fat_percent"]
    if bf < 10:
        insights["bf_category"] = "Very Lean (Athletic/Competition)"
    elif bf < 15:
        insights["bf_category"] = "Lean (Fitness)"
    elif bf < 20:
        insights["bf_category"] = "Average (Healthy)"
    elif bf < 25:
        insights["bf_category"] = "Above Average"
    else:
        insights["bf_category"] = "High Body Fat"

    # Add Adonis Index interpretation
    ai = parsed["adonis_index"]
    if ai >= 1.6:
        insights["proportion_category"] = "Excellent V-Taper (Elite proportions)"
    elif ai >= 1.4:
        insights["proportion_category"] = "Good V-Taper (Athletic proportions)"
    elif ai >= 1.2:
        insights["proportion_category"] = "Moderate Taper (Average proportions)"
    else:
        insights["proportion_category"] = "Minimal Taper (Needs shoulder development)"

    return insights


def generate_qr_friendly_id(signature_id: str) -> str:
    """
    Generate QR-code friendly version of signature ID

    Removes dashes for easier encoding.

    Args:
        signature_id: Full signature ID

    Returns:
        QR-friendly format
    """
    # Remove dashes, keep all info
    qr_id = signature_id.replace("-", "")
    return qr_id


def restore_from_qr_id(qr_id: str) -> Optional[str]:
    """
    Restore full signature ID from QR format

    Args:
        qr_id: QR-friendly ID (no dashes)

    Returns:
        Full signature ID with dashes, or None if invalid
    """
    # Expected format without dashes: BodyTypeBFX.XXXXXXAI X.XX
    # Need to intelligently re-add dashes

    # Pattern: [BodyType][BF][number][.][number][hash 6 chars][AI][number][.][number]
    pattern = r'^([A-Za-z]+)(BF\d+\.\d+)([A-F0-9]{6})(AI\d+\.\d+)$'

    match = re.match(pattern, qr_id)

    if match:
        body_type, bf_part, hash_part, ai_part = match.groups()
        return f"{body_type}-{bf_part}-{hash_part}-{ai_part}"

    return None


def generate_display_name(signature_id: str, user_name: Optional[str] = None) -> str:
    """
    Generate friendly display name from signature ID

    Args:
        signature_id: Body signature ID
        user_name: User's name (optional)

    Returns:
        Friendly display string
    """
    parsed = parse_body_signature_id(signature_id)

    if not parsed:
        return "Unknown Body Type"

    body_type = parsed["body_type"]
    bf = parsed["body_fat_percent"]

    if user_name:
        return f"{user_name}'s {body_type} ({bf:.1f}% BF)"
    else:
        return f"{body_type} Physique ({bf:.1f}% BF)"
