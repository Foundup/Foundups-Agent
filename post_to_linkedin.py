"""Quick script to manually post to LinkedIn for detected stream"""
from modules.platform_integration.linkedin_agent.src.anti_detection_poster import AntiDetectionLinkedIn

# Create poster
poster = AntiDetectionLinkedIn()
poster.company_id = '165749317'  # UnDaoDu LinkedIn page

# Post content
content = """LIVE NOW on YouTube!

UnDaoDu is streaming live. Join us here:
https://www.youtube.com/watch?v=Nbdnevaq8SQ

#LiveStream #YouTube"""

print(f"[INFO] Opening LinkedIn browser for company ID: {poster.company_id}")
print(f"[INFO] Company name: UnDaoDu")
print(f"[INFO] Stream URL: https://www.youtube.com/watch?v=Nbdnevaq8SQ")
print()

success = poster.post_to_company_page(content)

if success:
    print(f"✅ LinkedIn browser opened successfully!")
    print(f"   Browser should be open for manual posting")
else:
    print(f"❌ Failed to open LinkedIn browser")
