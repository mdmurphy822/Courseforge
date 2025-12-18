#!/usr/bin/env python3
"""
Test script for new callout and stats_grid slide methods.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from pptx_generator import PPTXGenerator

def test_callout_slide():
    """Test the callout slide method."""
    print("Testing add_callout_slide...")

    gen = PPTXGenerator()

    # Test callout slide with multiple callouts
    callouts = [
        {
            "callout_type": "info",
            "heading": "Key Information",
            "text": "This is an important piece of information that should be highlighted."
        },
        {
            "callout_type": "warning",
            "heading": "Important Warning",
            "text": "Please be aware of this critical warning before proceeding."
        },
        {
            "callout_type": "success",
            "heading": "Success Tip",
            "text": "Follow this tip to ensure successful completion."
        },
        {
            "callout_type": "tip",
            "heading": "Pro Tip",
            "text": "Expert advice to help you excel."
        }
    ]

    gen.add_callout_slide(
        title="Important Information",
        callouts=callouts,
        notes="This slide highlights four key pieces of information."
    )

    print("  ✓ Callout slide created successfully")
    return gen

def test_stats_grid_slide():
    """Test the stats grid slide method."""
    print("Testing add_stats_grid_slide...")

    gen = PPTXGenerator()

    # Test stats grid with various stats
    stats = [
        {
            "value": "85%",
            "label": "Completion Rate",
            "trend": "up",
            "highlight": True
        },
        {
            "value": "1,234",
            "label": "Active Users",
            "trend": "up",
            "highlight": False
        },
        {
            "value": "$45K",
            "label": "Revenue",
            "trend": "down",
            "highlight": False
        },
        {
            "value": "4.8",
            "label": "Rating",
            "trend": None,
            "highlight": True
        },
        {
            "value": "99.9%",
            "label": "Uptime",
            "trend": None,
            "highlight": False
        },
        {
            "value": "3.2s",
            "label": "Load Time",
            "trend": "down",
            "highlight": False
        }
    ]

    gen.add_stats_grid_slide(
        title="Key Metrics Dashboard",
        stats=stats,
        layout="auto",
        notes="Overview of key performance metrics."
    )

    print("  ✓ Stats grid slide created successfully")
    return gen

def test_from_structure():
    """Test using the methods via create_from_structure."""
    print("Testing via create_from_structure...")

    gen = PPTXGenerator()

    content = {
        "metadata": {
            "title": "Test Presentation",
            "author": "Test Author"
        },
        "sections": [
            {
                "slides": [
                    {
                        "type": "title",
                        "title": "New Slide Methods Test",
                        "content": {
                            "subtitle": "Testing callout and stats_grid"
                        }
                    },
                    {
                        "type": "callout",
                        "title": "Callout Example",
                        "content": {
                            "callouts": [
                                {
                                    "callout_type": "info",
                                    "heading": "Information",
                                    "text": "This is important information."
                                },
                                {
                                    "callout_type": "warning",
                                    "heading": "Warning",
                                    "text": "Please note this warning."
                                }
                            ]
                        }
                    },
                    {
                        "type": "stats_grid",
                        "title": "Statistics Overview",
                        "content": {
                            "stats": [
                                {"value": "100+", "label": "Users", "trend": "up"},
                                {"value": "95%", "label": "Satisfaction", "highlight": True},
                                {"value": "$50K", "label": "Revenue", "trend": "up"}
                            ],
                            "layout": "3col"
                        }
                    }
                ]
            }
        ]
    }

    gen.create_from_structure(content)

    print("  ✓ Structure-based creation successful")
    return gen

def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("Testing new PPTX Generator methods")
    print("="*60 + "\n")

    try:
        # Test individual methods
        gen1 = test_callout_slide()
        output1 = "/tmp/test_callout.pptx"
        gen1.save(output1)
        print(f"  → Saved to {output1}\n")

        gen2 = test_stats_grid_slide()
        output2 = "/tmp/test_stats_grid.pptx"
        gen2.save(output2)
        print(f"  → Saved to {output2}\n")

        # Test via structure
        gen3 = test_from_structure()
        output3 = "/tmp/test_combined.pptx"
        gen3.save(output3)
        print(f"  → Saved to {output3}\n")

        print("="*60)
        print("✓ All tests passed successfully!")
        print("="*60)

        return 0

    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
