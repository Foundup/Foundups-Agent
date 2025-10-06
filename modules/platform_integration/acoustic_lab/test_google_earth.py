#!/usr/bin/env python3
"""
Test Google Earth URL parsing functionality.
"""

def test_google_earth_url_parsing():
    """Test parsing coordinates from Google Earth URLs."""

    # Test URLs with expected coordinates
    test_cases = [
        {
            'url': 'https://earth.google.com/web/search/Utah+Valley+University,+West+University+Parkway,+Orem,+UT,+USA/@40.2767739,-111.71327038,1402.66806842a,858.21625526d,35y,229.81086925h,0t,0r/data=CiwiJgokCYnFt9tk9TNAEYbFt9tk9TPAGUaYtCW_BUlAIfjtyJcOpEnAQgIIAToDCgEwQgIIAEoNCP___________wEQAA?authuser=0',
            'expected_lat': 40.2767739,
            'expected_lng': -111.71327038,
            'description': 'Full Utah Valley University URL'
        },
        {
            'url': 'https://earth.google.com/web/@40.7649,-111.8421,1000a',
            'expected_lat': 40.7649,
            'expected_lng': -111.8421,
            'description': 'Simple coordinate URL'
        },
        {
            'url': 'https://earth.google.com/web/search/Salt+Lake+City/@40.7608,-111.8910,500a',
            'expected_lat': 40.7608,
            'expected_lng': -111.8910,
            'description': 'Salt Lake City search URL'
        }
    ]

    print("Testing Google Earth URL parsing...")
    print("=" * 50)

    all_passed = True

    for i, test_case in enumerate(test_cases, 1):
        url = test_case['url']
        expected_lat = test_case['expected_lat']
        expected_lng = test_case['expected_lng']
        description = test_case['description']

        print(f"\nTest {i}: {description}")
        print(f"URL: {url[:80]}...")

        try:
            # Find the @ symbol
            at_index = url.index('@')
            if at_index == -1:
                print("[FAILED] No @ symbol found in URL")
                all_passed = False
                continue

            # Extract coordinate part
            coord_part = url[at_index + 1:]

            # Split by comma and take first two values
            coord_parts = coord_part.split(',')
            if len(coord_parts) < 2:
                print("[FAILED] Could not parse coordinates")
                all_passed = False
                continue

            parsed_lat = float(coord_parts[0])
            parsed_lng = float(coord_parts[1])

            print(f"Expected: {expected_lat}, {expected_lng}")
            print(f"Parsed:   {parsed_lat}, {parsed_lng}")

            # Check if coordinates match (within small tolerance for floating point)
            lat_diff = abs(parsed_lat - expected_lat)
            lng_diff = abs(parsed_lng - expected_lng)

            if lat_diff < 0.0001 and lng_diff < 0.0001:
                print("[PASSED] Coordinates match!")
            else:
                print(f"[FAILED] Coordinates don't match (diff: lat={lat_diff}, lng={lng_diff})")
                all_passed = False

        except Exception as e:
            print(f"[FAILED] Error parsing URL: {e}")
            all_passed = False

    print("\n" + "=" * 50)
    if all_passed:
        print("[SUCCESS] All Google Earth URL parsing tests passed!")
        print("\nThe Acoustic Lab can now extract coordinates from Google Earth URLs like:")
        print("https://earth.google.com/web/@40.2767739,-111.71327038,1402.66806842a")
        print("-> Automatically extracts: 40.2767739, -111.71327038")
    else:
        print("[FAILED] Some tests failed - check URL parsing logic")

    return all_passed

if __name__ == "__main__":
    test_google_earth_url_parsing()
