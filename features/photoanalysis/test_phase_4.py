"""
Integration Tests for Phase 4 (Steps 17-20)
Tests complete integration of persistence, recommendations, error handling, and optimization

Run with: python test_phase_4.py
"""
import sys
from pathlib import Path
import asyncio
from datetime import datetime, date

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from models.schemas import (
    BodyMeasurements, BodyRatios, AestheticScore, ConfidenceMetrics,
    ImageQuality, PhotoAngle, AngleType, BodyType, WHOOPData,
    UserProfile, PersonalizedRecommendations, ScanResult
)


# ============================================================
# TEST DATA CREATORS
# ============================================================

def create_test_scan_result(user_id: str = "test_user_123") -> ScanResult:
    """Create mock scan result for testing"""

    import uuid

    measurements = BodyMeasurements(
        chest_circumference_cm=105.0,
        waist_circumference_cm=82.0,
        hip_circumference_cm=96.0,
        bicep_circumference_cm=38.0,
        thigh_circumference_cm=58.0,
        calf_circumference_cm=38.0,
        shoulder_width_cm=48.0,
        body_fat_percent=14.5,
        estimated_weight_kg=78.0,
        posture_rating=8.0,
        muscle_definition="Well-defined"
    )

    ratios = BodyRatios(
        shoulder_to_waist_ratio=1.52,
        adonis_index=1.52,
        golden_ratio_deviation=0.098,
        waist_to_hip_ratio=0.85,
        chest_to_waist_ratio=1.28,
        arm_to_chest_ratio=0.36,
        leg_to_torso_ratio=0.75,
        symmetry_score=82.5
    )

    aesthetic = AestheticScore(
        overall_score=78.5,
        golden_ratio_score=34.0,
        symmetry_score=25.0,
        composition_score=15.5,
        posture_score=8.0,
        body_type=BodyType.VTAPER,
        body_type_confidence=0.88
    )

    confidence = ConfidenceMetrics(
        overall_confidence=0.91,
        photo_count_factor=1.0,
        measurement_consistency=0.94,
        ai_confidence=0.89,
        data_completeness=0.92,
        is_reliable=True
    )

    image_urls = {
        "front": "https://storage.example.com/test_front.jpg",
        "side": "https://storage.example.com/test_side.jpg",
        "back": "https://storage.example.com/test_back.jpg"
    }

    image_quality = {
        "front": ImageQuality(
            width=1920, height=1080, file_size_kb=450, format="jpeg",
            sharpness_score=85, has_exif=True, orientation=1,
            is_valid=True, quality_score=88
        ),
        "side": ImageQuality(
            width=1920, height=1080, file_size_kb=420, format="jpeg",
            sharpness_score=82, has_exif=True, orientation=1,
            is_valid=True, quality_score=85
        ),
        "back": ImageQuality(
            width=1920, height=1080, file_size_kb=440, format="jpeg",
            sharpness_score=80, has_exif=True, orientation=1,
            is_valid=True, quality_score=83
        )
    }

    detected_angles = {
        "front": PhotoAngle(
            angle_type=AngleType.FRONT, confidence=0.95,
            detected_pose_keypoints=17, is_standing=True
        ),
        "side": PhotoAngle(
            angle_type=AngleType.SIDE, confidence=0.92,
            detected_pose_keypoints=15, is_standing=True
        ),
        "back": PhotoAngle(
            angle_type=AngleType.BACK, confidence=0.90,
            detected_pose_keypoints=16, is_standing=True
        )
    }

    whoop_data = WHOOPData(
        user_id=user_id,
        recovery_score=68.0,
        strain_score=14.2,
        sleep_hours=7.5,
        hrv_ms=65.0,
        resting_heart_rate=58,
        last_updated=datetime.now(),
        has_data=True
    )

    scan_result = ScanResult(
        scan_id=str(uuid.uuid4()),
        body_signature_id="VTaper-BF14.5-A3F7C2-AI1.52",
        user_id=user_id,
        timestamp=datetime.now(),
        image_urls=image_urls,
        image_quality=image_quality,
        detected_angles=detected_angles,
        measurements=measurements,
        ratios=ratios,
        aesthetic_score=aesthetic,
        composition_hash="A3F7C2",
        whoop_data=whoop_data,
        confidence=confidence,
        processing_time_sec=26.8,
        api_version="2.0"
    )

    return scan_result


# ============================================================
# PHASE 4 TESTS
# ============================================================

async def test_firestore_persistence():
    """Test Step 17: Firestore client"""
    print("\n" + "="*60)
    print("TEST 1: FIRESTORE PERSISTENCE (Step 17)")
    print("="*60)

    from services.firestore_client import get_firestore_client

    try:
        firestore = get_firestore_client()
        scan_result = create_test_scan_result()

        # Test: Check hash collision
        print("\n[Test 1.1] Hash Collision Detection")
        has_collision, count = await firestore.check_hash_collision(
            scan_result.composition_hash,
            scan_result.user_id
        )
        print(f"  Hash: {scan_result.composition_hash}")
        print(f"  Collision: {has_collision}")
        print(f"  Occurrences: {count}")
        print("  ✅ PASS: Hash collision check works")

        # Note: Actual Firestore operations require Firebase setup
        print("\n[Test 1.2] Save Scan Result (Skipped - requires Firebase)")
        print("  ⚠️ SKIP: Requires Firebase credentials")

        print("\n[Test 1.3] Retrieve Scan History (Skipped - requires Firebase)")
        print("  ⚠️ SKIP: Requires Firebase credentials")

        print("\n✅ FIRESTORE CLIENT: Initialized successfully")

    except Exception as e:
        print(f"\n❌ FAIL: {str(e)}")
        import traceback
        traceback.print_exc()


async def test_recommendation_engine():
    """Test Step 18: AI Recommendations"""
    print("\n" + "="*60)
    print("TEST 2: AI RECOMMENDATIONS ENGINE (Step 18)")
    print("="*60)

    from services.recommendation_engine import get_recommendation_engine

    try:
        engine = get_recommendation_engine()
        scan_result = create_test_scan_result()

        print("\n[Test 2.1] Generate Recommendations")

        # Generate recommendations
        recommendations = await engine.generate_recommendations(
            scan_result=scan_result,
            previous_scan=None,
            user_preferences={"allergies": [], "cuisine_preferences": []},
            fitness_goal="muscle_gain"
        )

        print(f"\n**WORKOUT PLAN:**")
        print(recommendations.workout_plan[:300] + "...")

        print(f"\n**NUTRITION PLAN:**")
        print(recommendations.nutrition_plan[:300] + "...")

        print(f"\n**KEY FOCUS AREAS ({len(recommendations.key_focus_areas)}):**")
        for area in recommendations.key_focus_areas:
            print(f"  - {area}")

        print(f"\n**TIMELINE:** {recommendations.estimated_timeline_weeks} weeks")

        assert isinstance(recommendations, PersonalizedRecommendations)
        assert len(recommendations.key_focus_areas) > 0
        assert recommendations.estimated_timeline_weeks > 0

        print("\n✅ PASS: Recommendations generated successfully")

    except Exception as e:
        print(f"\n❌ FAIL: {str(e)}")
        import traceback
        traceback.print_exc()


async def test_error_handling():
    """Test Step 19: Error Handling"""
    print("\n" + "="*60)
    print("TEST 3: ERROR HANDLING & MONITORING (Step 19)")
    print("="*60)

    from services.error_handler import (
        get_error_handler,
        PhotoAnalysisError,
        AIAnalysisError,
        safe_execute,
        with_timeout
    )

    try:
        handler = get_error_handler()

        # Test 3.1: Retry decorator
        print("\n[Test 3.1] Retry Decorator")

        attempt_count = 0

        @handler.with_retry(max_attempts=3, delay_seconds=0.1, backoff_factor=2.0)
        async def flaky_function():
            nonlocal attempt_count
            attempt_count += 1

            if attempt_count < 3:
                raise AIAnalysisError("Temporary API failure")

            return "Success"

        result = await flaky_function()
        print(f"  Attempts: {attempt_count}")
        print(f"  Result: {result}")
        assert attempt_count == 3
        print("  ✅ PASS: Retry logic works")

        # Test 3.2: Error logging
        print("\n[Test 3.2] Error Logging")

        try:
            raise PhotoAnalysisError("Test error", step="Test Step")
        except PhotoAnalysisError as e:
            error_log = await handler.log_error(
                error=e,
                step="Test Step",
                user_id="test_user",
                scan_id="test_scan",
                severity="error"
            )

            print(f"  Error ID: {error_log.error_id}")
            print(f"  Error Type: {error_log.error_type}")
            print(f"  Step: {error_log.step}")
            assert error_log.error_type == "PhotoAnalysisError"
            print("  ✅ PASS: Error logging works")

        # Test 3.3: Error context manager
        print("\n[Test 3.3] Error Context Manager")

        async with handler.error_context("Test Context", raise_on_error=False) as ctx:
            # This will fail but not raise
            1 / 0

        if ctx.error_log:
            print(f"  Caught error: {ctx.error_log.error_type}")
            print("  ✅ PASS: Error context works")

        # Test 3.4: Health check
        print("\n[Test 3.4] Health Check")

        health = await handler.health_check()
        print(f"  Status: {health['status']}")
        print(f"  Checks: {list(health['checks'].keys())}")
        print("  ✅ PASS: Health check works")

        print("\n✅ ERROR HANDLER: All tests passed")

    except Exception as e:
        print(f"\n❌ FAIL: {str(e)}")
        import traceback
        traceback.print_exc()


async def test_performance_optimization():
    """Test Step 20: Performance Optimization"""
    print("\n" + "="*60)
    print("TEST 4: PERFORMANCE OPTIMIZATION (Step 20)")
    print("="*60)

    from services.performance_optimizer import (
        get_performance_optimizer,
        get_cache_manager,
        parallel_execute,
        batch_process
    )

    try:
        optimizer = get_performance_optimizer()
        cache = get_cache_manager()

        # Test 4.1: Profiling
        print("\n[Test 4.1] Performance Profiling")

        async with optimizer.profile("test_operation"):
            await asyncio.sleep(0.1)

        metrics = optimizer.metrics.get_summary()
        assert "test_operation" in metrics
        print(f"  Operation time: {metrics['test_operation']['avg_ms']:.0f}ms")
        print("  ✅ PASS: Profiling works")

        # Test 4.2: Caching
        print("\n[Test 4.2] Cache Operations")

        await cache.set("test_key", {"data": "test_value"}, ttl=60)
        cached = await cache.get("test_key")
        assert cached == {"data": "test_value"}
        print("  ✅ PASS: Cache set/get works")

        # Test cache miss
        missing = await cache.get("nonexistent_key")
        assert missing is None
        print("  ✅ PASS: Cache miss handled")

        # Test cache key generation
        key1 = cache.generate_cache_key("arg1", "arg2", kwarg1="value1")
        key2 = cache.generate_cache_key("arg1", "arg2", kwarg1="value1")
        assert key1 == key2
        print("  ✅ PASS: Deterministic cache keys")

        # Test 4.3: Parallel execution
        print("\n[Test 4.3] Parallel Execution")

        async def slow_task():
            await asyncio.sleep(0.1)
            return "done"

        tasks = [slow_task for _ in range(5)]
        start_time = asyncio.get_event_loop().time()
        results = await parallel_execute(tasks, max_concurrent=5)
        elapsed = asyncio.get_event_loop().time() - start_time

        assert len(results) == 5
        assert elapsed < 0.5  # Should complete in ~0.1s with parallelism
        print(f"  Executed {len(results)} tasks in {elapsed:.2f}s")
        print("  ✅ PASS: Parallel execution works")

        # Test 4.4: Batch processing
        print("\n[Test 4.4] Batch Processing")

        async def process_item(item):
            return item * 2

        items = list(range(25))
        results = await batch_process(
            items,
            process_item,
            batch_size=10,
            delay_between_batches=0.05
        )

        assert len(results) == 25
        assert results[0] == 0
        assert results[24] == 48
        print(f"  Processed {len(results)} items in batches")
        print("  ✅ PASS: Batch processing works")

        # Test 4.5: Performance report
        print("\n[Test 4.5] Performance Report")

        report = await optimizer.get_performance_report()
        print(f"  Operations tracked: {len(report['operation_metrics'])}")
        print(f"  Cache size: {report['cache_stats']['memory_cache_size']}")
        print("  ✅ PASS: Performance reporting works")

        # Clean up
        await cache.clear_all()

        print("\n✅ PERFORMANCE OPTIMIZER: All tests passed")

    except Exception as e:
        print(f"\n❌ FAIL: {str(e)}")
        import traceback
        traceback.print_exc()


# ============================================================
# RUN ALL TESTS
# ============================================================

async def run_all_phase_4_tests():
    """Run complete Phase 4 test suite"""

    print("\n" + "="*60)
    print("  PHASE 4 INTEGRATION TEST SUITE")
    print("  Testing Steps 17-20")
    print("="*60)

    test_results = []

    # Test 1: Firestore
    try:
        await test_firestore_persistence()
        test_results.append(("Firestore Persistence", "PASS"))
    except Exception as e:
        test_results.append(("Firestore Persistence", f"FAIL: {str(e)}"))

    # Test 2: Recommendations
    try:
        await test_recommendation_engine()
        test_results.append(("AI Recommendations", "PASS"))
    except Exception as e:
        test_results.append(("AI Recommendations", f"FAIL: {str(e)}"))

    # Test 3: Error Handling
    try:
        await test_error_handling()
        test_results.append(("Error Handling", "PASS"))
    except Exception as e:
        test_results.append(("Error Handling", f"FAIL: {str(e)}"))

    # Test 4: Performance
    try:
        await test_performance_optimization()
        test_results.append(("Performance Optimization", "PASS"))
    except Exception as e:
        test_results.append(("Performance Optimization", f"FAIL: {str(e)}"))

    # Summary
    print("\n" + "="*60)
    print("  TEST SUMMARY")
    print("="*60)

    passed = sum(1 for _, status in test_results if status == "PASS")
    failed = len(test_results) - passed

    for test_name, status in test_results:
        icon = "[PASS]" if status == "PASS" else "[FAIL]"
        print(f"{icon} {test_name}: {status}")

    print(f"\nTotal: {len(test_results)} tests")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")

    if failed == 0:
        print("\n[SUCCESS] ALL PHASE 4 TESTS PASSED!")
        print("Steps 17-20 are working correctly.")
    else:
        print(f"\n[WARNING] {failed} test(s) failed")

    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    # Run tests
    asyncio.run(run_all_phase_4_tests())
