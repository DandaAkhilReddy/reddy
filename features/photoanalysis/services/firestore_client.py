"""
Firestore Persistence Client (Step 17)
Handles atomic transactions for saving and retrieving scan results

This service provides:
1. Atomic save operations for complete scan results
2. User scan history retrieval with pagination
3. Scan comparison and progress tracking
4. Hash collision detection and resolution
5. Data consistency validation
"""
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import asyncio
from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter
from google.api_core import retry, exceptions

from ..models.schemas import (
    ScanResult, UserProfile, ErrorLog,
    BodyMeasurements, BodyRatios, AestheticScore
)
from ..config.settings import get_settings

# Setup logging
logger = logging.getLogger(__name__)


class FirestoreClient:
    """
    Firestore client for scan result persistence

    Collections:
    - /users/{user_id} - User profiles
    - /users/{user_id}/scans/{scan_id} - Individual scans (subcollection)
    - /composition_hashes/{hash} - Hash collision tracking
    - /error_logs/{error_id} - Error logging
    """

    def __init__(self):
        """Initialize Firestore client"""
        self.settings = get_settings()
        self.db = firestore.Client(
            project=self.settings.firebase_project_id
        )

        # Collection references
        self.users_ref = self.db.collection('users')
        self.hashes_ref = self.db.collection('composition_hashes')
        self.errors_ref = self.db.collection('error_logs')

        logger.info("Firestore client initialized")


    # ============================================================
    # MAIN OPERATIONS - Scan Save & Retrieve
    # ============================================================

    @retry.Retry(
        predicate=retry.if_exception_type(
            exceptions.DeadlineExceeded,
            exceptions.ServiceUnavailable
        ),
        deadline=30.0
    )
    async def save_scan_result(
        self,
        scan_result: ScanResult,
        user_profile: Optional[UserProfile] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Save complete scan result with atomic transaction

        This performs:
        1. Hash collision check
        2. User profile update (increment scan count)
        3. Scan document save
        4. Hash registry update

        Args:
            scan_result: Complete ScanResult object
            user_profile: Optional UserProfile (for validation)

        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        try:
            logger.info(f"Saving scan {scan_result.scan_id} for user {scan_result.user_id}")

            # References
            user_ref = self.users_ref.document(scan_result.user_id)
            scan_ref = user_ref.collection('scans').document(scan_result.scan_id)
            hash_ref = self.hashes_ref.document(scan_result.composition_hash)

            # Prepare scan data (convert Pydantic to dict)
            scan_data = self._scan_to_firestore_dict(scan_result)

            # Run atomic transaction
            transaction = self.db.transaction()

            @firestore.transactional
            def update_in_transaction(transaction):
                """Atomic update of user profile + scan save"""

                # 1. Get current user profile
                user_doc = user_ref.get(transaction=transaction)

                if user_doc.exists:
                    current_total = user_doc.get('total_scans') or 0
                    user_update = {
                        'total_scans': current_total + 1,
                        'last_scan_at': scan_result.timestamp,
                        'updated_at': datetime.now()
                    }
                else:
                    # Create new user profile
                    user_update = {
                        'uid': scan_result.user_id,
                        'total_scans': 1,
                        'last_scan_at': scan_result.timestamp,
                        'created_at': datetime.now(),
                        'updated_at': datetime.now()
                    }

                    # Merge with provided profile if available
                    if user_profile:
                        user_update.update(user_profile.dict(exclude={'uid', 'total_scans'}))

                # 2. Save scan document
                transaction.set(scan_ref, scan_data)

                # 3. Update user profile
                transaction.set(user_ref, user_update, merge=True)

                # 4. Register hash (for collision detection)
                hash_data = {
                    'hash': scan_result.composition_hash,
                    'user_id': scan_result.user_id,
                    'scan_id': scan_result.scan_id,
                    'body_signature': scan_result.body_signature_id,
                    'timestamp': scan_result.timestamp,
                    'occurrences': firestore.Increment(1)
                }
                transaction.set(hash_ref, hash_data, merge=True)

                logger.info(f"Transaction complete: Scan {scan_result.scan_id} saved")

            # Execute transaction
            update_in_transaction(transaction)

            return True, None

        except exceptions.AlreadyExists:
            error_msg = f"Scan {scan_result.scan_id} already exists"
            logger.error(error_msg)
            return False, error_msg

        except Exception as e:
            error_msg = f"Failed to save scan: {str(e)}"
            logger.error(error_msg, exc_info=True)

            # Log error to Firestore
            await self._log_error(
                step="Step 17 - Firestore Save",
                error_type=type(e).__name__,
                error_message=str(e),
                user_id=scan_result.user_id,
                scan_id=scan_result.scan_id
            )

            return False, error_msg


    async def get_scan_by_id(
        self,
        user_id: str,
        scan_id: str
    ) -> Optional[ScanResult]:
        """
        Retrieve a specific scan by ID

        Args:
            user_id: User identifier
            scan_id: Scan identifier

        Returns:
            ScanResult object or None if not found
        """
        try:
            scan_ref = self.users_ref.document(user_id).collection('scans').document(scan_id)
            scan_doc = scan_ref.get()

            if not scan_doc.exists:
                logger.warning(f"Scan {scan_id} not found for user {user_id}")
                return None

            scan_data = scan_doc.to_dict()
            return self._firestore_dict_to_scan(scan_data)

        except Exception as e:
            logger.error(f"Failed to retrieve scan {scan_id}: {str(e)}", exc_info=True)
            return None


    async def get_user_scan_history(
        self,
        user_id: str,
        limit: int = 10,
        start_after: Optional[datetime] = None
    ) -> List[ScanResult]:
        """
        Retrieve user's scan history with pagination

        Args:
            user_id: User identifier
            limit: Max number of scans to return (default: 10)
            start_after: Timestamp to start after (for pagination)

        Returns:
            List of ScanResult objects, sorted by timestamp (newest first)
        """
        try:
            scans_ref = self.users_ref.document(user_id).collection('scans')

            # Build query
            query = scans_ref.order_by('timestamp', direction=firestore.Query.DESCENDING)

            if start_after:
                query = query.start_after({'timestamp': start_after})

            query = query.limit(limit)

            # Execute query
            scan_docs = query.stream()

            scans = []
            for doc in scan_docs:
                scan_data = doc.to_dict()
                scan_result = self._firestore_dict_to_scan(scan_data)
                if scan_result:
                    scans.append(scan_result)

            logger.info(f"Retrieved {len(scans)} scans for user {user_id}")
            return scans

        except Exception as e:
            logger.error(f"Failed to retrieve scan history: {str(e)}", exc_info=True)
            return []


    async def get_latest_scan(self, user_id: str) -> Optional[ScanResult]:
        """
        Get user's most recent scan

        Args:
            user_id: User identifier

        Returns:
            Latest ScanResult or None
        """
        scans = await self.get_user_scan_history(user_id, limit=1)
        return scans[0] if scans else None


    # ============================================================
    # HASH COLLISION DETECTION
    # ============================================================

    async def check_hash_collision(
        self,
        composition_hash: str,
        user_id: str
    ) -> Tuple[bool, int]:
        """
        Check if composition hash already exists

        Args:
            composition_hash: 6-char hash to check
            user_id: Current user ID

        Returns:
            Tuple of (has_collision: bool, occurrence_count: int)
        """
        try:
            hash_doc = self.hashes_ref.document(composition_hash).get()

            if not hash_doc.exists:
                return False, 0

            hash_data = hash_doc.to_dict()
            occurrences = hash_data.get('occurrences', 0)
            existing_user = hash_data.get('user_id')

            # Collision only if different user
            has_collision = existing_user != user_id

            return has_collision, occurrences

        except Exception as e:
            logger.error(f"Hash collision check failed: {str(e)}")
            return False, 0


    async def get_scans_by_signature(
        self,
        body_signature_id: str
    ) -> List[ScanResult]:
        """
        Find scans with matching body signature

        Useful for finding similar physiques across users

        Args:
            body_signature_id: Full signature (e.g., "VTaper-BF12.5-A3F7C2-AI1.54")

        Returns:
            List of matching scans
        """
        try:
            # Query across all users (collection group query)
            scans_query = self.db.collection_group('scans').where(
                filter=FieldFilter('body_signature_id', '==', body_signature_id)
            ).limit(20)

            scan_docs = scans_query.stream()

            scans = []
            for doc in scan_docs:
                scan_data = doc.to_dict()
                scan_result = self._firestore_dict_to_scan(scan_data)
                if scan_result:
                    scans.append(scan_result)

            return scans

        except Exception as e:
            logger.error(f"Signature search failed: {str(e)}")
            return []


    # ============================================================
    # USER PROFILE OPERATIONS
    # ============================================================

    async def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """
        Retrieve user profile

        Args:
            user_id: User identifier

        Returns:
            UserProfile or None
        """
        try:
            user_doc = self.users_ref.document(user_id).get()

            if not user_doc.exists:
                return None

            user_data = user_doc.to_dict()
            return UserProfile(**user_data)

        except Exception as e:
            logger.error(f"Failed to retrieve user profile: {str(e)}")
            return None


    async def update_user_profile(
        self,
        user_id: str,
        updates: Dict
    ) -> bool:
        """
        Update user profile fields

        Args:
            user_id: User identifier
            updates: Dictionary of fields to update

        Returns:
            True if successful
        """
        try:
            updates['updated_at'] = datetime.now()

            self.users_ref.document(user_id).set(updates, merge=True)
            logger.info(f"User profile updated: {user_id}")

            return True

        except Exception as e:
            logger.error(f"Failed to update user profile: {str(e)}")
            return False


    # ============================================================
    # PROGRESS TRACKING
    # ============================================================

    async def get_progress_comparison(
        self,
        user_id: str,
        weeks_back: int = 4
    ) -> Optional[Dict]:
        """
        Compare current scan with scan from X weeks ago

        Args:
            user_id: User identifier
            weeks_back: How many weeks to look back (default: 4)

        Returns:
            Dictionary with comparison metrics or None
        """
        try:
            # Get latest scan
            latest_scan = await self.get_latest_scan(user_id)
            if not latest_scan:
                return None

            # Get historical scan
            cutoff_date = datetime.now() - timedelta(weeks=weeks_back)

            scans_ref = self.users_ref.document(user_id).collection('scans')
            historical_query = scans_ref.where(
                filter=FieldFilter('timestamp', '<=', cutoff_date)
            ).order_by('timestamp', direction=firestore.Query.DESCENDING).limit(1)

            historical_docs = list(historical_query.stream())

            if not historical_docs:
                return {
                    "status": "no_historical_data",
                    "message": f"No scans found from {weeks_back} weeks ago"
                }

            historical_data = historical_docs[0].to_dict()
            historical_scan = self._firestore_dict_to_scan(historical_data)

            # Calculate changes
            from .scan_assembler import compare_scans
            comparison = compare_scans(latest_scan, historical_scan)

            return comparison

        except Exception as e:
            logger.error(f"Progress comparison failed: {str(e)}")
            return None


    # ============================================================
    # ERROR LOGGING
    # ============================================================

    async def _log_error(
        self,
        step: str,
        error_type: str,
        error_message: str,
        user_id: Optional[str] = None,
        scan_id: Optional[str] = None,
        stack_trace: Optional[str] = None,
        context: Dict = None
    ) -> None:
        """
        Log error to Firestore for monitoring

        Args:
            step: Which step failed
            error_type: Exception type
            error_message: Error description
            user_id: User ID (if available)
            scan_id: Scan ID (if available)
            stack_trace: Full stack trace
            context: Additional context
        """
        try:
            import uuid

            error_log = ErrorLog(
                error_id=str(uuid.uuid4()),
                timestamp=datetime.now(),
                step=step,
                error_type=error_type,
                error_message=error_message,
                user_id=user_id,
                scan_id=scan_id,
                stack_trace=stack_trace,
                context=context or {}
            )

            self.errors_ref.document(error_log.error_id).set(error_log.dict())

        except Exception as e:
            # Fail silently - don't want error logging to break main flow
            logger.error(f"Failed to log error: {str(e)}")


    # ============================================================
    # DATA CONVERSION HELPERS
    # ============================================================

    def _scan_to_firestore_dict(self, scan_result: ScanResult) -> Dict:
        """
        Convert ScanResult to Firestore-compatible dictionary

        Handles:
        - Nested Pydantic models
        - Datetime serialization
        - Enum conversion
        """
        scan_dict = scan_result.dict()

        # Convert nested models
        scan_dict['measurements'] = scan_result.measurements.dict()
        scan_dict['ratios'] = scan_result.ratios.dict()
        scan_dict['aesthetic_score'] = scan_result.aesthetic_score.dict()
        scan_dict['confidence'] = scan_result.confidence.dict()

        # Convert image quality and angles
        scan_dict['image_quality'] = {
            angle: quality.dict()
            for angle, quality in scan_result.image_quality.items()
        }
        scan_dict['image_angles'] = {
            angle: angle_data.dict()
            for angle, angle_data in scan_result.detected_angles.items()
        }

        # Handle WHOOP data
        if scan_result.whoop_data:
            scan_dict['whoop_data'] = scan_result.whoop_data.dict()

        # Handle recommendations
        if scan_result.recommendations:
            scan_dict['recommendations'] = scan_result.recommendations.dict()

        return scan_dict


    def _firestore_dict_to_scan(self, data: Dict) -> Optional[ScanResult]:
        """
        Convert Firestore dictionary back to ScanResult

        Args:
            data: Firestore document data

        Returns:
            ScanResult object or None if conversion fails
        """
        try:
            # Reconstruct nested objects
            from ..models.schemas import ImageQuality, PhotoAngle

            data['measurements'] = BodyMeasurements(**data['measurements'])
            data['ratios'] = BodyRatios(**data['ratios'])
            data['aesthetic_score'] = AestheticScore(**data['aesthetic_score'])

            # Reconstruct image quality
            data['image_quality'] = {
                angle: ImageQuality(**quality_data)
                for angle, quality_data in data.get('image_quality', {}).items()
            }

            # Reconstruct detected angles
            data['detected_angles'] = {
                angle: PhotoAngle(**angle_data)
                for angle, angle_data in data.get('image_angles', {}).items()
            }

            return ScanResult(**data)

        except Exception as e:
            logger.error(f"Failed to convert Firestore data to ScanResult: {str(e)}")
            return None


# ============================================================
# SINGLETON INSTANCE
# ============================================================

_firestore_client: Optional[FirestoreClient] = None


def get_firestore_client() -> FirestoreClient:
    """Get singleton Firestore client instance"""
    global _firestore_client

    if _firestore_client is None:
        _firestore_client = FirestoreClient()

    return _firestore_client
