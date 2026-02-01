#!/usr/bin/env python3
"""Direct test runner for mcp-code-indexer."""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def run_test_module(module_name):
    """Run a test module directly."""
    print(f"\n{'=' * 60}")
    print(f"Running tests for: {module_name}")
    print("=" * 60)

    try:
        # Import and run the test module
        module = __import__(f"tests.unit.{module_name}", fromlist=["*"])

        # Get all test classes from the module
        test_classes = []
        for name in dir(module):
            obj = getattr(module, name)
            if isinstance(obj, type) and name.startswith("Test"):
                test_classes.append(obj)

        total_tests = 0
        passed_tests = 0
        failed_tests = []

        for test_class in test_classes:
            print(f"\nTesting class: {test_class.__name__}")

            # Get all test methods
            test_methods = [
                name
                for name in dir(test_class)
                if name.startswith("test_") and callable(getattr(test_class, name))
            ]

            for method_name in test_methods:
                total_tests += 1
                test_instance = test_class()
                test_method = getattr(test_instance, method_name)

                try:
                    # Run setup if it exists
                    if hasattr(test_instance, "setUp"):
                        test_instance.setUp()

                    # Run the test
                    test_method()
                    print(f"  ✓ {method_name}")
                    passed_tests += 1

                    # Run teardown if it exists
                    if hasattr(test_instance, "tearDown"):
                        test_instance.tearDown()

                except Exception as e:
                    print(f"  ✗ {method_name}: {e}")
                    failed_tests.append((test_class.__name__, method_name, str(e)))

                    # Run teardown even if test failed
                    if hasattr(test_instance, "tearDown"):
                        try:
                            test_instance.tearDown()
                        except:
                            pass

        # Print summary
        print(f"\nSummary for {module_name}:")
        print(f"  Total tests: {total_tests}")
        print(f"  Passed: {passed_tests}")
        print(f"  Failed: {len(failed_tests)}")

        if failed_tests:
            print("\nFailed tests:")
            for class_name, method_name, error in failed_tests:
                print(f"  {class_name}.{method_name}: {error}")

        return len(failed_tests) == 0

    except Exception as e:
        print(f"Error running tests for {module_name}: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run all test modules."""
    test_modules = [
        "test_config",
        "test_security",
        "test_hashing",
        "test_chunkers",
        "test_db",
    ]

    all_passed = True
    for module_name in test_modules:
        if not run_test_module(module_name):
            all_passed = False

    print(f"\n{'=' * 60}")
    print("OVERALL SUMMARY")
    print("=" * 60)

    if all_passed:
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
