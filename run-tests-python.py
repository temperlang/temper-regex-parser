#!/usr/bin/env python3
import sys
import os
import logging
import unittest

# REQUIRED: Configure logging to see console.log() output
# Without this, console.log() produces NO OUTPUT!
logging.basicConfig(level=logging.INFO, format='%(message)s')

# Add temper-core and libraries to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(project_root, 'temper.out/py/temper-core'))
sys.path.insert(0, os.path.join(project_root, 'temper.out/py/std'))
sys.path.insert(0, os.path.join(project_root, 'temper.out/py/temper-regex-parser'))

# Discover and run all tests
loader = unittest.TestLoader()
start_dir = os.path.join(project_root, 'temper.out/py/temper-regex-parser/tests')
suite = loader.discover(start_dir, pattern='test_*.py')

runner = unittest.TextTestRunner(verbosity=2)
result = runner.run(suite)

# Exit with appropriate code
sys.exit(0 if result.wasSuccessful() else 1)
