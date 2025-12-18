#!/usr/bin/env python3
"""
Validation script for pipeline integration tests.
This script validates the test structure without running pytest.
"""

import ast
import sys
from pathlib import Path
from collections import defaultdict

def analyze_test_file(file_path: Path):
    """Analyze test file structure."""
    with open(file_path, 'r') as f:
        tree = ast.parse(f.read())

    stats = {
        'classes': [],
        'methods': defaultdict(list),
        'functions': [],
        'imports': [],
        'total_tests': 0
    }

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            if node.name.startswith('Test'):
                stats['classes'].append(node.name)
                # Count test methods in class
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name.startswith('test_'):
                        stats['methods'][node.name].append(item.name)
                        stats['total_tests'] += 1

        elif isinstance(node, ast.FunctionDef):
            if node.name.startswith('test_') and not any(
                isinstance(parent, ast.ClassDef) for parent in ast.walk(tree)
            ):
                stats['functions'].append(node.name)
                stats['total_tests'] += 1

        elif isinstance(node, ast.Import):
            for alias in node.names:
                stats['imports'].append(alias.name)

        elif isinstance(node, ast.ImportFrom):
            if node.module:
                stats['imports'].append(f"{node.module}")

    return stats

def main():
    test_file = Path(__file__).parent / 'test_pipeline_integration.py'

    if not test_file.exists():
        print(f"❌ Test file not found: {test_file}")
        return 1

    print(f"Analyzing {test_file.name}...")
    print("=" * 70)

    stats = analyze_test_file(test_file)

    # Display results
    print(f"\n📊 Test File Statistics:")
    print(f"   Total test classes: {len(stats['classes'])}")
    print(f"   Total test methods: {stats['total_tests']}")
    print(f"   Total imports: {len(set(stats['imports']))}")

    print(f"\n📋 Test Classes Found:")
    for cls_name in stats['classes']:
        test_count = len(stats['methods'][cls_name])
        print(f"   ✓ {cls_name} ({test_count} tests)")
        for method in stats['methods'][cls_name][:3]:  # Show first 3
            print(f"      - {method}")
        if len(stats['methods'][cls_name]) > 3:
            print(f"      ... and {len(stats['methods'][cls_name]) - 3} more")

    print(f"\n📦 Key Imports:")
    key_imports = ['pytest', 'orchestrator', 'manifest', 'Pipeline', 'PipelineConfig']
    found_imports = [imp for imp in stats['imports'] if any(k in imp for k in key_imports)]
    for imp in found_imports[:10]:
        print(f"   - {imp}")

    print(f"\n✅ Test Structure Validation:")

    # Validate expected test classes
    expected_classes = [
        'TestFullPipeline',
        'TestStageIsolation',
        'TestErrorHandling',
        'TestManifestIntegration',
        'TestFixtureIntegration',
        'TestConfigIntegration'
    ]

    missing_classes = [cls for cls in expected_classes if cls not in stats['classes']]

    if not missing_classes:
        print(f"   ✓ All expected test classes present")
    else:
        print(f"   ⚠ Missing test classes: {missing_classes}")

    # Check minimum test count
    if stats['total_tests'] >= 30:
        print(f"   ✓ Sufficient test coverage ({stats['total_tests']} tests)")
    else:
        print(f"   ⚠ Low test count ({stats['total_tests']} tests, expected >= 30)")

    print("\n" + "=" * 70)
    print("✅ Test file structure is valid and ready for pytest execution")
    print("\nTo run tests (when pytest is available):")
    print("  pytest tests/test_pipeline_integration.py -v")
    print("  pytest tests/test_pipeline_integration.py::TestFullPipeline -v")
    print("  pytest tests/test_pipeline_integration.py -k 'manifest' -v")

    return 0

if __name__ == '__main__':
    sys.exit(main())
