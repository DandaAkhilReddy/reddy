"""
WHOOP API Client with Mock Data Support
Integrates with DandaAkhilReddy/whoopmockdataset for development/testing
"""
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import httpx
import random
from ..photoanalysis.models.schemas import WHOOPData


class WHOOPClient:
    """
    WHOOP API Client with fallback to mock data
    Uses the GitHub mock dataset: https://github.com/DandaAkhilReddy/whoopmockdataset
    """

    def __init__(self, use_mock: bool = True, mock_api_url: Optional[str] = None):
        """
        Initialize WHOOP client

        Args:
            use_mock: Whether to use mock data (default True for development)
            mock_api_url: URL to mock API server (if None, generates realistic mock data)
        """
        self.use_mock = use_mock
        self.mock_api_url = mock_api_url or "http://localhost:3000/api"  # Default mock API
        self.production_api_url = "https://api.prod.whoop.com/developer"

    async def get_user_recovery(
        self,
        user_id: str,
        access_token: Optional[str] = None
    ) -> Optional[WHOOPData]:
        """
        Get latest recovery data for a user

        Args:
            user_id: User identifier
            access_token: WHOOP OAuth access token (not needed for mock)

        Returns:
            WHOOPData object or None if unavailable
        """
        if self.use_mock:
            return await self._get_mock_recovery(user_id)
        else:
            return await self._get_production_recovery(user_id, access_token)

    async def _get_mock_recovery(self, user_id: str) -> WHOOPData:
        """
        Get mock recovery data from the GitHub mock dataset

        Maps user_id to one of the 1000 mock users (10001-11000)
        """
        try:
            # Try to fetch from mock API server if running
            async with httpx.AsyncClient(timeout=5.0) as client:
                # Map string user_id to mock dataset user_id (10001-11000)
                mock_user_id = 10001 + (hash(user_id) % 1000)

                # Fetch latest recovery
                response = await client.get(
                    f"{self.mock_api_url}/recovery",
                    params={"user_id": mock_user_id, "limit": 1}
                )

                if response.status_code == 200:
                    data = response.json()
                    if data:
                        return self._parse_mock_recovery(data[0], user_id)

        except (httpx.RequestError, httpx.TimeoutException):
            # Fall back to generating realistic mock data
            pass

        # Generate realistic mock data inline
        return self._generate_realistic_mock(user_id)

    def _generate_realistic_mock(self, user_id: str) -> WHOOPData:
        """
        Generate realistic mock WHOOP data without external API

        Mimics the structure of the GitHub mock dataset
        """
        # Determine fitness profile based on user_id hash for consistency
        seed = hash(user_id) % 5
        profiles = [
            {"recovery": (75, 95), "strain": (14, 19), "sleep": (7, 9), "hrv": (75, 120), "rhr": (45, 55)},
            {"recovery": (30, 55), "strain": (16, 21), "sleep": (5, 6.5), "hrv": (40, 65), "rhr": (55, 70)},
            {"recovery": (55, 75), "strain": (10, 15), "sleep": (6.5, 8), "hrv": (50, 80), "rhr": (55, 65)},
            {"recovery": (40, 65), "strain": (5, 10), "sleep": (6, 7.5), "hrv": (35, 60), "rhr": (60, 75)},
            {"recovery": (20, 45), "strain": (17, 21), "sleep": (5, 6), "hrv": (30, 50), "rhr": (65, 80)},
        ]

        profile = profiles[seed]

        # Use seed for consistent random generation per user
        rng = random.Random(user_id)

        recovery_score = round(rng.uniform(*profile["recovery"]), 1)
        strain_score = round(rng.uniform(*profile["strain"]), 1)
        sleep_hours = round(rng.uniform(*profile["sleep"]), 1)
        hrv_ms = round(rng.uniform(*profile["hrv"]), 0)
        resting_heart_rate = int(rng.uniform(*profile["rhr"]))

        # Recent timestamp (last 12 hours)
        last_updated = datetime.now() - timedelta(
            hours=rng.randint(0, 12),
            minutes=rng.randint(0, 59)
        )

        return WHOOPData(
            user_id=user_id,
            recovery_score=recovery_score,
            strain_score=strain_score,
            sleep_hours=sleep_hours,
            hrv_ms=hrv_ms,
            resting_heart_rate=resting_heart_rate,
            last_updated=last_updated,
            has_data=True
        )

    def _parse_mock_recovery(self, data: Dict[str, Any], user_id: str) -> WHOOPData:
        """Parse recovery data from mock API response"""
        score = data.get("score", {})

        return WHOOPData(
            user_id=user_id,
            recovery_score=score.get("recovery_score"),
            strain_score=score.get("strain", 0.0),  # May need separate call
            sleep_hours=score.get("sleep_performance_percentage", 0) / 100 * 8,  # Estimate
            hrv_ms=score.get("hrv_rmssd_milli"),
            resting_heart_rate=score.get("resting_heart_rate"),
            last_updated=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat()).replace("Z", "+00:00")),
            has_data=True
        )

    async def _get_production_recovery(
        self,
        user_id: str,
        access_token: str
    ) -> Optional[WHOOPData]:
        """
        Get recovery data from production WHOOP API

        Args:
            user_id: WHOOP user ID
            access_token: Valid OAuth access token

        Returns:
            WHOOPData or None
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                headers = {"Authorization": f"Bearer {access_token}"}

                # Get latest recovery
                response = await client.get(
                    f"{self.production_api_url}/v1/recovery",
                    headers=headers,
                    params={"limit": 1}
                )

                if response.status_code == 200:
                    data = response.json()
                    records = data.get("records", [])

                    if records:
                        recovery = records[0]
                        score = recovery.get("score", {})

                        # Get sleep data separately
                        sleep_response = await client.get(
                            f"{self.production_api_url}/v1/activity/sleep",
                            headers=headers,
                            params={"limit": 1}
                        )

                        sleep_hours = None
                        if sleep_response.status_code == 200:
                            sleep_data = sleep_response.json()
                            sleep_records = sleep_data.get("records", [])
                            if sleep_records:
                                sleep_hours = sleep_records[0].get("score", {}).get("total_in_bed_time_milli", 0) / (1000 * 60 * 60)

                        return WHOOPData(
                            user_id=user_id,
                            recovery_score=score.get("recovery_score"),
                            strain_score=score.get("strain", 0.0),
                            sleep_hours=sleep_hours,
                            hrv_ms=score.get("hrv_rmssd_milli"),
                            resting_heart_rate=score.get("resting_heart_rate"),
                            last_updated=datetime.fromisoformat(recovery.get("created_at").replace("Z", "+00:00")),
                            has_data=True
                        )

        except Exception as e:
            # Log error and return None
            print(f"Error fetching WHOOP data: {e}")
            return None

        return None


# Global client instance
whoop_client = WHOOPClient(use_mock=True)


async def get_whoop_data(user_id: str, access_token: Optional[str] = None) -> Optional[WHOOPData]:
    """
    Convenience function to get WHOOP data

    Args:
        user_id: User identifier
        access_token: Optional OAuth token for production API

    Returns:
        WHOOPData or None
    """
    return await whoop_client.get_user_recovery(user_id, access_token)
