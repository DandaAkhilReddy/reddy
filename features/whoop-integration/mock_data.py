"""
WHOOP Mock Data Generator
Provides realistic mock WHOOP data for development and testing
"""
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import random


class WHOOPMockData:
    """Generate realistic WHOOP data for testing"""

    def __init__(self):
        """Initialize mock data generator with seed profiles"""
        self.profiles = {
            "athlete_high_recovery": {
                "recovery_score": (75, 95),
                "strain_score": (14, 19),
                "sleep_hours": (7, 9),
                "hrv_ms": (75, 120),
                "resting_heart_rate": (45, 55),
            },
            "athlete_low_recovery": {
                "recovery_score": (30, 55),
                "strain_score": (16, 21),
                "sleep_hours": (5, 6.5),
                "hrv_ms": (40, 65),
                "resting_heart_rate": (55, 70),
            },
            "average_fitness": {
                "recovery_score": (55, 75),
                "strain_score": (10, 15),
                "sleep_hours": (6.5, 8),
                "hrv_ms": (50, 80),
                "resting_heart_rate": (55, 65),
            },
            "sedentary": {
                "recovery_score": (40, 65),
                "strain_score": (5, 10),
                "sleep_hours": (6, 7.5),
                "hrv_ms": (35, 60),
                "resting_heart_rate": (60, 75),
            },
            "overtrained": {
                "recovery_score": (20, 45),
                "strain_score": (17, 21),
                "sleep_hours": (5, 6),
                "hrv_ms": (30, 50),
                "resting_heart_rate": (65, 80),
            },
        }

    def get_mock_data(
        self,
        user_id: str,
        profile_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate mock WHOOP data for a user

        Args:
            user_id: User identifier
            profile_type: Type of fitness profile (or None for random)

        Returns:
            Dictionary with WHOOP-like data structure
        """
        # Select profile type
        if profile_type is None or profile_type not in self.profiles:
            profile_type = random.choice(list(self.profiles.keys()))

        profile = self.profiles[profile_type]

        # Generate random values within profile ranges
        recovery_score = round(random.uniform(*profile["recovery_score"]), 1)
        strain_score = round(random.uniform(*profile["strain_score"]), 1)
        sleep_hours = round(random.uniform(*profile["sleep_hours"]), 1)
        hrv_ms = round(random.uniform(*profile["hrv_ms"]), 0)
        resting_heart_rate = round(random.uniform(*profile["resting_heart_rate"]), 0)

        # Generate recent timestamp (within last 24 hours)
        last_updated = datetime.now() - timedelta(
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )

        return {
            "user_id": user_id,
            "profile_type": profile_type,
            "recovery_score": recovery_score,
            "strain_score": strain_score,
            "sleep_hours": sleep_hours,
            "hrv_ms": hrv_ms,
            "resting_heart_rate": int(resting_heart_rate),
            "last_updated": last_updated.isoformat(),
            "has_data": True,
            # Additional contextual data
            "sleep_performance": self._calculate_sleep_performance(sleep_hours),
            "recovery_status": self._get_recovery_status(recovery_score),
            "strain_status": self._get_strain_status(strain_score),
        }

    def _calculate_sleep_performance(self, hours: float) -> str:
        """Calculate sleep performance category"""
        if hours >= 8:
            return "Optimal"
        elif hours >= 7:
            return "Good"
        elif hours >= 6:
            return "Fair"
        else:
            return "Poor"

    def _get_recovery_status(self, score: float) -> str:
        """Get recovery status from score"""
        if score >= 67:
            return "Green"
        elif score >= 34:
            return "Yellow"
        else:
            return "Red"

    def _get_strain_status(self, score: float) -> str:
        """Get strain level description"""
        if score >= 18:
            return "All Out"
        elif score >= 14:
            return "Strenuous"
        elif score >= 10:
            return "Moderate"
        else:
            return "Light"

    def get_detailed_sleep_data(self, user_id: str) -> Dict[str, Any]:
        """Generate detailed sleep cycle data"""
        total_sleep_hours = round(random.uniform(5, 9), 1)

        # Sleep stages (should sum to ~total sleep time)
        rem_minutes = int(total_sleep_hours * 60 * random.uniform(0.20, 0.25))
        deep_minutes = int(total_sleep_hours * 60 * random.uniform(0.15, 0.20))
        light_minutes = int(total_sleep_hours * 60 * random.uniform(0.45, 0.55))
        awake_minutes = int(total_sleep_hours * 60 * 0.05)

        return {
            "user_id": user_id,
            "total_sleep_minutes": int(total_sleep_hours * 60),
            "sleep_stages": {
                "rem_minutes": rem_minutes,
                "deep_minutes": deep_minutes,
                "light_minutes": light_minutes,
                "awake_minutes": awake_minutes,
            },
            "sleep_efficiency": round(random.uniform(85, 98), 1),
            "disturbances": random.randint(0, 5),
            "latency_minutes": random.randint(5, 30),
        }

    def get_weekly_summary(self, user_id: str) -> Dict[str, Any]:
        """Generate weekly activity summary"""
        return {
            "user_id": user_id,
            "week_start": (datetime.now() - timedelta(days=7)).isoformat(),
            "week_end": datetime.now().isoformat(),
            "avg_recovery": round(random.uniform(50, 80), 1),
            "avg_strain": round(random.uniform(10, 16), 1),
            "avg_sleep_hours": round(random.uniform(6, 8), 1),
            "total_workouts": random.randint(3, 7),
            "max_hr_achieved": random.randint(165, 195),
            "avg_hrv": round(random.uniform(50, 90), 0),
        }


# Global instance
whoop_mock = WHOOPMockData()


def get_mock_whoop_data(user_id: str, profile_type: Optional[str] = None) -> Dict[str, Any]:
    """
    Convenience function to get mock WHOOP data

    Args:
        user_id: User identifier
        profile_type: Optional fitness profile type

    Returns:
        Mock WHOOP data dictionary
    """
    return whoop_mock.get_mock_data(user_id, profile_type)


if __name__ == "__main__":
    # Example usage
    print("=== Mock WHOOP Data Examples ===\n")

    for profile in whoop_mock.profiles.keys():
        print(f"\nProfile: {profile}")
        data = whoop_mock.get_mock_data("test_user_123", profile)
        print(f"  Recovery: {data['recovery_score']} ({data['recovery_status']})")
        print(f"  Strain: {data['strain_score']} ({data['strain_status']})")
        print(f"  Sleep: {data['sleep_hours']}h ({data['sleep_performance']})")
        print(f"  HRV: {data['hrv_ms']}ms")
        print(f"  RHR: {data['resting_heart_rate']}bpm")
