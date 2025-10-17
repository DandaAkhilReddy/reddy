# ⌚ WHOOP Integration - Fitness Wearable Data Intelligence

**Status**: ✅ Mock Data Ready
**Dataset**: [whoopmockdataset](https://github.com/DandaAkhilReddy/whoopmockdataset)

## Overview

Integrates WHOOP wearable data (recovery, strain, sleep, HRV) to provide personalized fitness recommendations based on real-time physiological status.

## Features

- ✅ **Mock Data Support**: 1,000 users × 30 days of realistic data
- ✅ **5 Fitness Profiles**: Athlete, overtrained, average, sedentary, low recovery
- ✅ **Production API Client**: Ready for real WHOOP API integration
- ✅ **Async Operations**: Non-blocking data fetching
- 🚧 **OAuth Flow**: Planned for user authorization

## Data Provided

### Recovery Metrics
- Recovery score (0-100)
- Recovery status (Green/Yellow/Red)
- HRV (ms)
- Resting heart rate (bpm)

### Strain Metrics
- Strain score (0-21)
- Strain status (Light/Moderate/Strenuous/All Out)

### Sleep Metrics
- Total sleep hours
- Sleep performance (Optimal/Good/Fair/Poor)
- Sleep efficiency
- Sleep stages (REM, deep, light)

## Usage

### Mock Data (Default)

```python
from whoop_integration.api_client import get_whoop_data

# Automatic mock data (consistent per user)
data = await get_whoop_data("user_123")

print(f"Recovery: {data.recovery_score}% ({data.recovery_status})")
print(f"Strain: {data.strain_score}")
print(f"Sleep: {data.sleep_hours}h")
print(f"HRV: {data.hrv_ms}ms")
```

### Specific Profile

```python
from whoop_integration.mock_data import get_mock_whoop_data

# Choose from: athlete_high_recovery, athlete_low_recovery,
#              average_fitness, sedentary, overtrained
data = get_mock_whoop_data("user_123", profile_type="athlete_high_recovery")
```

### Production API (When Ready)

```python
from whoop_integration.api_client import WHOOPClient

client = WHOOPClient(use_mock=False)
data = await client.get_user_recovery("user_id", access_token="oauth_token")
```

## Fitness Profiles

### Athlete - High Recovery
- Recovery: 75-95%
- Strain: 14-19
- Sleep: 7-9h
- HRV: 75-120ms
- RHR: 45-55bpm

### Athlete - Low Recovery
- Recovery: 30-55%
- Strain: 16-21 (overtraining)
- Sleep: 5-6.5h
- HRV: 40-65ms
- RHR: 55-70bpm

### Average Fitness
- Recovery: 55-75%
- Strain: 10-15
- Sleep: 6.5-8h
- HRV: 50-80ms
- RHR: 55-65bpm

### Sedentary
- Recovery: 40-65%
- Strain: 5-10
- Sleep: 6-7.5h
- HRV: 35-60ms
- RHR: 60-75bpm

### Overtrained
- Recovery: 20-45%
- Strain: 17-21
- Sleep: 5-6h
- HRV: 30-50ms
- RHR: 65-80bpm

## Integration with Photo Analysis

WHOOP data enhances body scan recommendations:

```python
# In Step 18: AI Recommendations
if whoop_data.recovery_score < 34:
    recommendation += "Your recovery is in the RED. Consider a rest day."
elif whoop_data.strain_score > 18 and whoop_data.sleep_hours < 7:
    recommendation += "High strain with insufficient sleep. Prioritize recovery."
```

## Mock Dataset Structure

Uses the [whoopmockdataset](https://github.com/DandaAkhilReddy/whoopmockdataset) repository:

```
- 1,000 users (IDs: 10001-11000)
- 30 days of data per user
- 30,000 physiological cycles
- 28,462 recovery records
- 28,462 sleep sessions
- 31,474 workouts
```

## Configuration

```env
# Optional: Production WHOOP API
WHOOP_CLIENT_ID=your_client_id
WHOOP_CLIENT_SECRET=your_secret
WHOOP_REDIRECT_URI=http://localhost:8000/auth/whoop/callback

# Default: Mock mode enabled
USE_MOCK_WHOOP_DATA=true
```

## Roadmap

- ✅ Mock data generator
- ✅ Async API client
- ✅ Profile-based generation
- 🚧 OAuth 2.0 flow
- 🚧 Webhook subscriptions
- 🚧 Historical data fetching
- 🚧 Real-time sync

## Resources

- [WHOOP Developer Docs](https://developer.whoop.com/)
- [Mock Dataset Repo](https://github.com/DandaAkhilReddy/whoopmockdataset)
- [API Integration Guide](https://tryterra.co/blog/whoop-integration-series-part-2-data-available-from-the-api-ec4337a9455b)

## License

MIT - see [LICENSE](../../LICENSE)
