import unittest
import sys
import os
import time

# Ensure backend directory is in sys.path
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

def main():
    print("=" * 70)
    print("      WEBISCRAP BACKEND COMPREHENSIVE VERIFICATION SUITE")
    print("=" * 70)
    start_time = time.time()

    loader = unittest.TestLoader()
    suite = loader.discover(start_dir=os.path.dirname(__file__), pattern="test_*.py")

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    elapsed = time.time() - start_time
    print("=" * 70)
    print(f"Total Tests Run: {result.testsRun}")
    print(f"Errors: {len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Elapsed Time: {elapsed:.2f}s")
    print("=" * 70)

    if result.wasSuccessful():
        print(">>> ALL BACKEND TESTS PASSED! <<<")
        sys.exit(0)
    else:
        print(">>> SOME TESTS FAILED! <<<")
        sys.exit(1)

if __name__ == "__main__":
    main()
