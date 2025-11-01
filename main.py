"""
Main entry point for the web scraping collection.
Lists available scrapers organized by category.
"""

import os
from pathlib import Path


def list_scrapers():
    """List all available scrapers organized by category."""
    scrapers_dir = Path(__file__).parent / "scrapers"
    
    categories = {
        "ecommerce": "E-commerce Websites",
        "job_boards": "Job Boards",
        "educational": "Educational Platforms",
        "social_media": "Social Media & Developer Platforms",
        "content": "Content & Media",
        "misc": "Miscellaneous"
    }
    
    print("=" * 60)
    print("Web Scraping Collection - Available Scrapers")
    print("=" * 60)
    print()
    
    for category_dir, category_name in categories.items():
        category_path = scrapers_dir / category_dir
        if category_path.exists():
            py_files = sorted(category_path.glob("*.py"))
            if py_files:
                print(f"\n📁 {category_name}")
                print("-" * 60)
                for py_file in py_files:
                    if py_file.name != "__init__.py":
                        print(f"  • {category_dir}/{py_file.name}")
    
    print("\n" + "=" * 60)
    print("\nUsage:")
    print("  python scrapers/<category>/<scraper_name>.py")
    print("\nExample:")
    print("  python scrapers/ecommerce/flipkart.py")
    print("=" * 60)


def main():
    """Main entry point."""
    list_scrapers()


if __name__ == "__main__":
    main()
