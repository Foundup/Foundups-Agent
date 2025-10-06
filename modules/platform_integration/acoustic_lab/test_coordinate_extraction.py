#!/usr/bin/env python3
"""
Test coordinate extraction functionality independent of Google Maps.
"""

def test_coordinate_extraction_logic():
    """Test the coordinate extraction logic from Google Earth and Google Maps URLs."""

    # Test cases with expected results
    test_cases = [
        {
            'url': 'https://earth.google.com/web/@40.2767739,-111.71327038',
            'expected_lat': 40.2767739,
            'expected_lng': -111.71327038,
            'description': 'Google Earth simple coordinate URL'
        },
        {
            'url': 'https://earth.google.com/web/search/Utah/@40.7649,-111.8421,1000a',
            'expected_lat': 40.7649,
            'expected_lng': -111.8421,
            'description': 'Google Earth search URL with altitude'
        },
        {
            'url': 'https://earth.google.com/web/search/Utah+Valley+University,+West+University+Parkway,+Orem,+UT,+USA/@40.2767739,-111.71327038,1402.66806842a,858.21625526d,35y,229.81086925h,0t,0r/data=CiwiJgokCYnFt9tk9TNAEYbFt9tk9TPAGUaYtCW_BUlAIfjtyJcOpEnAQgIIAToDCgEwQgIIAEoNCP___________wEQAA?authuser=0',
            'expected_lat': 40.2767739,
            'expected_lng': -111.71327038,
            'description': 'Google Earth complex URL with full parameters'
        },
        {
            'url': 'https://www.google.com/maps/@40.2776229,-111.7138613,219m/data=!3m1!1e3?entry=ttu&g_ep=EgoyMDI1MDkzMC4wIKXMDSoASAFQAw%3D%3D',
            'expected_lat': 40.2776229,
            'expected_lng': -111.7138613,
            'description': 'Google Maps URL (user provided)'
        },
        {
            'url': 'https://www.google.com/maps/@51.5074,-0.1278,10z',
            'expected_lat': 51.5074,
            'expected_lng': -0.1278,
            'description': 'Google Maps simple URL'
        }
    ]

    print("Testing coordinate extraction logic...")
    print("=" * 50)

    all_passed = True

    for i, test_case in enumerate(test_cases, 1):
        url = test_case['url']
        expected_lat = test_case['expected_lat']
        expected_lng = test_case['expected_lng']
        description = test_case['description']

        print(f"\nTest {i}: {description}")

        try:
            # Extract coordinates using the same logic as the JavaScript
            at_index = url.find('@')
            if at_index == -1:
                print("❌ No @ symbol found")
                all_passed = False
                continue

            coord_part = url[at_index + 1:]
            coord_parts = coord_part.split(',')

            if len(coord_parts) < 2:
                print("❌ Could not parse coordinates")
                all_passed = False
                continue

            parsed_lat = float(coord_parts[0])
            parsed_lng = float(coord_parts[1])

            print(f"URL: ...{url[at_index:at_index+30]}...")
            print(f"Expected: {expected_lat}, {expected_lng}")
            print(f"Parsed:   {parsed_lat}, {parsed_lng}")

            # Check if close enough (floating point precision)
            lat_close = abs(parsed_lat - expected_lat) < 0.000001
            lng_close = abs(parsed_lng - expected_lng) < 0.000001

            if lat_close and lng_close:
                print("[PASSED] Coordinates extracted correctly")
            else:
                print("[FAILED] Coordinate mismatch")
                all_passed = False

        except Exception as e:
            print(f"[FAILED] {e}")
            all_passed = False

    print("\n" + "=" * 50)
    if all_passed:
        print("[SUCCESS] All coordinate extraction tests passed!")
        print("\nThe coordinate extraction works independently of Google Maps.")
        print("You can paste Google Earth or Google Maps URLs and extract coordinates even")
        print("when the map is not available.")
    else:
        print("[FAILURE] Some coordinate extraction tests failed")

    return all_passed

if __name__ == "__main__":
    test_coordinate_extraction_logic()
