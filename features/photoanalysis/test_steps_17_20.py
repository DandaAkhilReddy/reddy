"""
Integration Tests for Phase 4 (Steps 17-20)
Tests Firestore persistence, AI recommendations, error handling, and performance optimization

Run with: python test_steps_17_20.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import asyncio
from datetime import datetime
from typing import Dict, Any

from models.schemas import (
    BodyMeasurements, BodyRatios, AestheticScore, ConfidenceMetrics,
    ImageQuality, PhotoAngle, AngleType, ScanResult, BodyType
)

# Import services from Phase 4
from services.firestore_client import get_firestore_client
from services.recommendation_engine import get_recommendation_engine
from services.error_handler import (
    get_error_handler, ErrorHandler, PipelineStep,
    safe_execute, with_timeout, PhotoAnalysisError
)
from services.performance_optimizer import (
    get_performance_optimizer, get_cache_manager,
    parallel_execute, parallel_execute_dict
)


# ============================================================
# MOCK DATA GENERATION
# ============================================================

def create_mock_scan_result(user_id: str = "test_user_123") -> ScanResult:
    """Create mock scan result for testing"""

    measurements = BodyMeasurements(
        chest_circumference_cm=105.0,
        waist_circumference_cm=80.0,
        hip_circumference_cm=95.0,
        bicep_circumference_cm=38.0,
        thigh_circumference_cm=58.0,
        calf_circumference_cm=38.0,
        shoulder_width_cm=48.0,
        body_fat_percent=12.5,
        estimated_weight_kg=80.0,
        posture_rating=8.5,
        muscle_definition="Well-defined"
    )

    ratios = BodyRatios(
        adonis_index=1.56,
        golden_ratio_score=38.0,
        waist_to_hip_ratio=0.84,
        chest_to_waist_ratio=1.31,
        arm_to_chest_ratio=0.36,
        leg_to_height_ratio=0.52,
        symmetry_score=85.0,
        shoulder_to_waist_ratio=1.56
    )

    aesthetic = AestheticScore(
        overall_score=85.0,
        body_type=BodyType.VTAPER,
        body_type_confidence=0.92,
        golden_ratio_score=38.0,
        symmetry_score=27.0,
        composition_score=18.0,
        posture_score=8.5
    )

    confidence = ConfidenceMetrics(
        overall_confidence=0.92,
        photo_count_factor=1.0,
        measurement_consistency=0.95,
        ai_confidence=0.90,
        data_completeness=0.88,
        is_reliable=True
    )

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

    image_urls = {
        "front": f"https://storage.test.com/{user_id}/front.jpg",
        "side": f"https://storage.test.com/{user_id}/side.jpg",
        "back": f"https://storage.test.com/{user_id}/back.jpg"
    }

    scan_result = ScanResult(
        scan_id=f"scan_{datetime.now().timestamp()}",
        body_signature_id="VTaper-BF12.5-A3F7C2-AI1.56",
        user_id=user_id,
        timestamp=datetime.now(),
        image_urls=image_urls,
        image_quality=image_quality,
        detected_angles=detected_angles,
        measurements=measurements,
        ratios=ratios,
        aesthetic_score=aesthetic,
        composition_hash="A3F7C2",
        whoop_data=None,
        confidence=confidence,
        processing_time_sec=28.5,
        api_version="2.0"
    )

    return scan_result


# ============================================================
# TEST FUNCTIONS
# ============================================================

async def test_step_17_firestore_persistence():
    """Test Step 17: Firestore persistence client"""
    print("\n[Step 17] Testing Firestore Persistence Client...")

    try:
        # Note: This test requires Firebase credentials to actually save
        # For now, we'll just test that the client initializes

        firestore_client = get_firestore_client()
        print("  [PASS] Firestore client initialized")

        # Create mock scan
        scan = create_mock_scan_result("test_user_firestore")
        print(f"  [INFO] Created mock scan: {scan.body_signature_id}")

        # Test data conversion
        scan_dict = firestore_client._scan_to_firestore_dict(scan)
        assert isinstance(scan_dict, dict), "Scan conversion to dict failed"
        print(f"  [PASS] Scan converted to Firestore dict ({len(scan_dict)} keys)")

        # Test dict back to scan
        reconstructed = firestore_client._firestore_dict_to_scan(scan_dict)
        assert reconstructed is not None, "Failed to reconstruct scan from dict"
        assert reconstructed.body_signature_id == scan.body_signature_id
        print(f"  [PASS] Scan reconstructed from dict")

        # Test hash collision check
        has_collision, count = await firestore_client.check_hash_collision(
            scan.composition_hash,
            scan.user_id
        )
        print(f"  [INFO] Hash collision check: collision={has_collision}, count={count}")

        print("  [SUCCESS] Step 17 tests passed")
        return True

    except Exception as e:
        print(f"  [FAIL] Step 17 test failed: {str(e)}")
        return False


async def test_step_18_ai_recommendations():
    """Test Step 18: AI recommendations engine"""
    print("\n[Step 18] Testing AI Recommendations Engine...")

    try:
        recommendation_engine = get_recommendation_engine()
        print("  [PASS] Recommendation engine initialized")

        # Create mock scan
        scan = create_mock_scan_result("test_user_recommendations")

        # Generate recommendations
        recommendations = await recommendation_engine.generate_recommendations(
            scan_result=scan,
            fitness_goal="muscle_gain"
        )

        assert recommendations is not None, "Recommendations not generated"
        assert len(recommendations.workout_plan) > 0, "Workout plan is empty"
        assert len(recommendations.nutrition_plan) > 0, "Nutrition plan is empty"

        print(f"  [PASS] Recommendations generated")
        print(f"  [INFO] Workout plan length: {len(recommendations.workout_plan)} chars")
        print(f"  [INFO] Nutrition plan length: {len(recommendations.nutrition_plan)} chars")
        print(f"  [INFO] Focus areas: {len(recommendations.key_focus_areas)}")
        print(f"  [INFO] Estimated timeline: {recommendations.estimated_timeline_weeks} weeks")

        # Test workout intensity determination
        intensity = recommendation_engine._determine_workout_intensity(None)
        assert "Moderate" in intensity
        print(f"  [PASS] Workout intensity: {intensity}")

        # Test training split recommendation
        split = recommendation_engine._recommend_training_split(BodyType.VTAPER, "muscle_gain")
        assert len(split) > 0
        print(f"  [PASS] Training split: {split}")

        print("  [SUCCESS] Step 18 tests passed")
        return True

    except Exception as e:
        print(f"  [FAIL] Step 18 test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_step_19_error_handling():
    """Test Step 19: Error handling & monitoring"""
    print("\n[Step 19] Testing Error Handling & Monitoring...")

    try:
        error_handler = get_error_handler()
        print("  [PASS] Error handler initialized")

        # Test custom exceptions
        try:
            raise PhotoAnalysisError(
                "Test error",
                step="Test Step",
                recoverable=True
            )
        except PhotoAnalysisError as e:
            assert e.step == "Test Step"
            assert e.recoverable == True
            print("  [PASS] PhotoAnalysisError working correctly")

        # Test error logging
        test_error = Exception("Test exception for logging")
        error_log = await error_handler.log_error(
            error=test_error,
            step="Test Step",
            user_id="test_user",
            scan_id="test_scan",
            severity="warning"
        )

        assert error_log.error_id is not None
        assert error_log.step == "Test Step"
        print(f"  [PASS] Error logged with ID: {error_log.error_id}")

        # Test retry decorator
        attempt_count = {"value": 0}

        @error_handler.with_retry(max_attempts=3, delay_seconds=0.1)
        async def flaky_function():
            attempt_count["value"] += 1
            if attempt_count["value"] < 3:
                raise Exception("Simulated failure")
            return "Success"

        result = await flaky_function()
        assert result == "Success"
        assert attempt_count["value"] == 3
        print(f"  [PASS] Retry logic worked ({attempt_count['value']} attempts)")

        # Test timeout decorator
        @with_timeout(1.0)
        async def fast_function():
            await asyncio.sleep(0.1)
            return "Completed"

        result = await fast_function()
        assert result == "Completed"
        print("  [PASS] Timeout decorator working")

        # Test health check
        health = await error_handler.health_check()
        assert health["status"] in ["healthy", "degraded"]
        print(f"  [PASS] Health check: {health['status']}")

        print("  [SUCCESS] Step 19 tests passed")
        return True

    except Exception as e:
        print(f"  [FAIL] Step 19 test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_step_20_performance_optimization():
    """Test Step 20: Performance optimization"""
    print("\n[Step 20] Testing Performance Optimization...")

    try:
        optimizer = get_performance_optimizer()
        cache = get_cache_manager()
        print("  [PASS] Performance optimizer initialized")
        print("  [PASS] Cache manager initialized")

        # Test caching
        test_key = "test_key_123"
        test_value = {"data": "test_value", "timestamp": datetime.now().isoformat()}

        await cache.set(test_key, test_value, ttl=60)
        cached_value = await cache.get(test_key)

        assert cached_value is not None
        assert cached_value["data"] == test_value["data"]
        print("  [PASS] Cache set/get working")

        # Test cache key generation
        key = cache.generate_cache_key("user123", "scan456", param1="value1")
        assert len(key) == 16  # SHA-256 truncated to 16 chars
        print(f"  [PASS] Cache key generated: {key}")

        # Test performance metrics
        optimizer.metrics.start_timer("test_operation")
        await asyncio.sleep(0.1)
        duration = optimizer.metrics.stop_timer("test_operation")

        assert duration >= 0.1
        avg = optimizer.metrics.get_average("test_operation")
        assert avg >= 0.1
        print(f"  [PASS] Performance metrics: {duration*1000:.0f}ms recorded")

        # Test profiling context
        async with optimizer.profile("test_profile_operation"):
            await asyncio.sleep(0.05)

        summary = optimizer.metrics.get_summary()
        assert "test_profile_operation" in summary
        print("  [PASS] Profiling context working")

        # Test parallel execution
        async def task1():
            await asyncio.sleep(0.1)
            return "result1"

        async def task2():
            await asyncio.sleep(0.1)
            return "result2"

        async def task3():
            await asyncio.sleep(0.1)
            return "result3"

        results = await parallel_execute([task1, task2, task3], max_concurrent=3)
        assert results == ["result1", "result2", "result3"]
        print("  [PASS] Parallel execution working")

        # Test parallel execution with dict
        task_dict = {
            "task_a": task1,
            "task_b": task2,
            "task_c": task3
        }
        results_dict = await parallel_execute_dict(task_dict, max_concurrent=3)
        assert results_dict["task_a"] == "result1"
        assert results_dict["task_b"] == "result2"
        assert results_dict["task_c"] == "result3"
        print("  [PASS] Parallel dict execution working")

        # Test image optimizer
        from services.performance_optimizer import ImageOptimizer

        should_resize = ImageOptimizer.should_resize(2048, 1536, max_size=1024)
        assert should_resize == True
        print("  [PASS] Image resize check working")

        new_w, new_h = ImageOptimizer.calculate_resize_dimensions(2048, 1536, max_size=1024)
        assert new_w == 1024
        assert new_h == 768
        print(f"  [PASS] Resize dimensions: {new_w}x{new_h}")

        # Test processing time estimation
        estimated_time = ImageOptimizer.estimate_processing_time(3, 1.5)
        assert estimated_time > 0
        print(f"  [PASS] Estimated processing time: {estimated_time:.1f}s")

        # Test performance report
        report = await optimizer.get_performance_report()
        assert "operation_metrics" in report
        assert "cache_stats" in report
        print(f"  [PASS] Performance report generated")

        # Clean up
        await cache.delete(test_key)
        print("  [PASS] Cache cleanup successful")

        print("  [SUCCESS] Step 20 tests passed")
        return True

    except Exception as e:
        print(f"  [FAIL] Step 20 test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_integration_all_steps():
    """Integration test combining all Phase 4 steps"""
    print("\n[INTEGRATION] Testing Complete Phase 4 Workflow...")

    try:
        # Initialize all services
        firestore = get_firestore_client()
        recommender = get_recommendation_engine()
        error_handler = get_error_handler()
        optimizer = get_performance_optimizer()

        print("  [INFO] All services initialized")

        # Create mock scan
        scan = create_mock_scan_result("integration_test_user")

        # Profile the complete workflow
        async with optimizer.profile("complete_workflow"):

            # Step 17: Convert to Firestore format
            async with optimizer.profile("firestore_conversion"):
                scan_dict = firestore._scan_to_firestore_dict(scan)

            # Step 18: Generate recommendations
            async with optimizer.profile("recommendations_generation"):
                async with error_handler.error_context("Step 18", raise_on_error=True):
                    recommendations = await recommender.generate_recommendations(
                        scan_result=scan,
                        fitness_goal="muscle_gain"
                    )

            # Step 19: Log successful completion
            print("  [INFO] Workflow completed successfully")

        # Step 20: Get performance report
        report = await optimizer.get_performance_report()

        print("\n  [PERFORMANCE REPORT]")
        for operation, metrics in report["operation_metrics"].items():
            print(f"    {operation}: {metrics['avg_ms']:.0f}ms (count: {metrics['count']})")

        print("\n  [SUCCESS] Integration test passed")
        return True

    except Exception as e:
        print(f"  [FAIL] Integration test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


# ============================================================
# MAIN TEST RUNNER
# ============================================================

async def run_all_tests():
    """Run all Phase 4 integration tests"""

    print("=" * 70)
    print("  PHASE 4 INTEGRATION TESTS (Steps 17-20)")
    print("  Testing: Persistence, Recommendations, Error Handling, Performance")
    print("=" * 70)

    results = {}

    # Run individual tests
    results["Step 17"] = await test_step_17_firestore_persistence()
    results["Step 18"] = await test_step_18_ai_recommendations()
    results["Step 19"] = await test_step_19_error_handling()
    results["Step 20"] = await test_step_20_performance_optimization()
    results["Integration"] = await test_integration_all_steps()

    # Print summary
    print("\n" + "=" * 70)
    print("  TEST SUMMARY")
    print("=" * 70)

    passed = sum(1 for result in results.values() if result)
    failed = len(results) - passed

    for test_name, result in results.items():
        status = "[PASS]" if result else "[FAIL]"
        print(f"  {status} {test_name}")

    print(f"\n  Total: {len(results)} tests")
    print(f"  Passed: {passed}")
    print(f"  Failed: {failed}")

    if failed == 0:
        print("\n  [SUCCESS] ALL PHASE 4 TESTS PASSED!")
        print("  Steps 17-20 are working correctly.")
    else:
        print(f"\n  [WARNING] {failed} test(s) failed")

    print("=" * 70 + "\n")

    return failed == 0


if __name__ == "__main__":
    # Run tests
    success = asyncio.run(run_all_tests())

    # Exit with appropriate code
    sys.exit(0 if success else 1)
