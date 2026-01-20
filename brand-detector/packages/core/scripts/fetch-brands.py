#!/usr/bin/env python3
"""
Brand Database Fetcher for Rankfor.AI
======================================

Fetches brand names from multiple sources to create a comprehensive brands.json database.

Sources:
1. Simple Icons (high-quality, curated tech/SaaS brands)
2. Wikidata (comprehensive global brands with logos)

Usage:
    python scripts/fetch-brands.py

Output:
    open-site/public/data/brands.json
"""

import requests
import json
import time
from pathlib import Path
from typing import Set, Dict, List, Any

# Ignored terms to prevent false positives (dictionary words that are also brand names)
IGNORED_TERMS = {
    # Common dictionary words
    'target', 'apple', 'amazon', 'oracle', 'slack', 'notion', 'monday',
    'buffer', 'stripe', 'square', 'uber', 'lyft', 'zoom', 'nest',
    'ring', 'hive', 'mint', 'plaid', 'segment', 'braze', 'amplitude',

    # Generic tech terms
    'api', 'cloud', 'data', 'analytics', 'platform', 'system', 'software',
    'service', 'solution', 'app', 'tech', 'digital', 'online', 'web',

    # Common company suffixes (we'll handle these separately)
    'inc', 'llc', 'ltd', 'corp', 'corporation', 'company', 'co',
    'group', 'holdings', 'enterprises', 'international', 'global',

    # Too short (1-2 letter brands often cause false positives)
    'hp', 'ge', 'lg', 'hp', 'ea', 'ibm', 'sap', 'aws', 'gcp',
}

def fetch_simple_icons() -> Set[str]:
    """
    Fetch brand names from Simple Icons (curated, high-quality tech brands)

    Returns:
        Set of brand names
    """
    print("🎯 Fetching brands from Simple Icons...")

    try:
        url = 'https://raw.githubusercontent.com/simple-icons/simple-icons/refs/heads/develop/data/simple-icons.json'
        headers = {'User-Agent': 'RankforBot/1.0'}

        r = requests.get(url, headers=headers, timeout=30)
        r.raise_for_status()

        data = r.json()
        brands: Set[str] = set()

        # Extract brand titles
        for icon in data:
            title = icon.get('title', '').strip()
            if title:
                brands.add(title)

                # Also add any aliases
                aliases = icon.get('aliases', {}).get('aka', [])
                for alias in aliases:
                    if alias:
                        brands.add(alias.strip())

        print(f"✅ Fetched {len(brands)} brands from Simple Icons")
        return brands

    except Exception as e:
        print(f"❌ Error fetching Simple Icons: {e}")
        return set()


def fetch_wikidata_brands() -> Set[str]:
    """
    Fetch brand names from Wikidata (comprehensive, requires filtering)

    Returns:
        Set of brand names
    """
    print("🌐 Fetching brands from Wikidata (this may take 30-60 seconds)...")

    url = 'https://query.wikidata.org/sparql'

    # Query: Select instances of 'business' that have a logo (proxy for significance)
    # Limit: 10,000 results (Wikidata SPARQL limit)
    query = """
    SELECT DISTINCT ?itemLabel ?alias WHERE {
      ?item wdt:P31/wdt:P279* wd:Q4830453 .
      ?item wdt:P154 ?logo .
      OPTIONAL { ?item skos:altLabel ?alias FILTER(LANG(?alias) = "en") }
      SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
    }
    LIMIT 10000
    """

    try:
        headers = {'User-Agent': 'RankforBot/1.0'}
        params = {'format': 'json', 'query': query}

        r = requests.get(url, params=params, headers=headers, timeout=90)
        r.raise_for_status()

        data = r.json()
        brands: Set[str] = set()

        for item in data.get('results', {}).get('bindings', []):
            # Add main label
            if 'itemLabel' in item:
                label = item['itemLabel']['value'].strip()
                if label:
                    brands.add(label)

            # Add aliases
            if 'alias' in item:
                alias_value = item['alias']['value'].strip()
                # Split comma-separated aliases
                aliases = [a.strip() for a in alias_value.split(',')]
                for alias in aliases:
                    if alias:
                        brands.add(alias)

        print(f"✅ Fetched {len(brands)} brands from Wikidata")
        return brands

    except Exception as e:
        print(f"❌ Error fetching Wikidata: {e}")
        return set()


def clean_brand_name(name: str) -> str:
    """
    Clean and normalize a brand name

    Args:
        name: Raw brand name

    Returns:
        Cleaned brand name
    """
    # Remove common suffixes
    suffixes = [
        ' Inc.', ' Inc', ' LLC', ' Ltd.', ' Ltd', ' Corp.', ' Corp',
        ' Corporation', ' Company', ' Co.', ' Co', ' Group', ' Holdings',
        ' Enterprises', ' International', ' Global', ' AG', ' GmbH', ' SA',
    ]

    cleaned = name
    for suffix in suffixes:
        if cleaned.endswith(suffix):
            cleaned = cleaned[:-len(suffix)].strip()

    return cleaned


def filter_brands(brands: Set[str]) -> Set[str]:
    """
    Filter and clean brand names

    Args:
        brands: Raw brand names

    Returns:
        Filtered brand names
    """
    filtered: Set[str] = set()

    for brand in brands:
        # Skip empty
        if not brand:
            continue

        # Clean the brand name
        cleaned = clean_brand_name(brand)

        # Skip if in ignored terms
        if cleaned.lower() in IGNORED_TERMS:
            continue

        # Skip if too short (1-2 characters)
        if len(cleaned) <= 2:
            continue

        # Skip if all uppercase and > 5 chars (likely acronym)
        if cleaned.isupper() and len(cleaned) > 5:
            continue

        # Skip if contains only numbers
        if cleaned.replace('.', '').replace('-', '').isdigit():
            continue

        # Add both original and cleaned versions
        filtered.add(brand)
        if cleaned != brand:
            filtered.add(cleaned)

    return filtered


def create_brand_database() -> Dict[str, Any]:
    """
    Create a comprehensive brand database from multiple sources

    Returns:
        Brand database dictionary
    """
    print("🚀 Building comprehensive brand database...\n")

    # Fetch from both sources
    simple_icons_brands = fetch_simple_icons()
    wikidata_brands = fetch_wikidata_brands()

    print()

    # Combine and filter
    all_brands = simple_icons_brands | wikidata_brands
    filtered_brands = filter_brands(all_brands)

    # Sort for binary search efficiency
    sorted_brands = sorted(list(filtered_brands))

    # Create database structure
    database = {
        'meta': {
            'version': '1.0.0',
            'generated_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            'sources': [
                {
                    'name': 'Simple Icons',
                    'url': 'https://github.com/simple-icons/simple-icons',
                    'count': len(simple_icons_brands),
                    'license': 'CC0 1.0',
                },
                {
                    'name': 'Wikidata',
                    'url': 'https://www.wikidata.org',
                    'count': len(wikidata_brands),
                    'license': 'CC0 1.0',
                },
            ],
            'total_raw': len(all_brands),
            'total_filtered': len(filtered_brands),
            'ignored_terms': sorted(list(IGNORED_TERMS)),
        },
        'brands': sorted_brands,
        'high_confidence': sorted(list(simple_icons_brands & filtered_brands)),
    }

    return database


def main():
    """Main execution"""
    database = create_brand_database()

    # Determine output path
    script_dir = Path(__file__).parent
    output_dir = script_dir.parent / 'open-site' / 'public' / 'data'
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / 'brands.json'

    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(database, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Success!")
    print(f"📊 Statistics:")
    print(f"   - Total brands: {len(database['brands'])}")
    print(f"   - High confidence: {len(database['high_confidence'])}")
    print(f"   - Sources: {', '.join([s['name'] for s in database['meta']['sources']])}")
    print(f"\n💾 Saved to: {output_file}")
    print(f"\n💡 Usage in TypeScript:")
    print(f"   import brandsDb from '@/public/data/brands.json';")
    print(f"   const isBrand = brandsDb.brands.includes('Salesforce');")


if __name__ == "__main__":
    main()
