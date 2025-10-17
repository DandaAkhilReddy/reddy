"""
Test Runner for ReddyFit Photo Analysis
Properly sets up Python path for imports
"""
import sys
from pathlib import Path

# Add features/photoanalysis to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Now run the integration test
if __name__ == "__main__":
    import test_integration
    import asyncio

    asyncio.run(test_integration.main())
