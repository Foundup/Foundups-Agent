#!/usr/bin/env python3
"""
Extract authorization code from redirect URL
"""

import sys
from urllib.parse import urlparse, parse_qs

def extract_code(url):
    """Extract authorization code from LinkedIn redirect URL"""
    
    print("="*60)
    print("LinkedIn Authorization Code Extractor")
    print("="*60)
    
    # Parse the URL
    if not url.startswith('http'):
        url = 'http://' + url
    
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    
    if 'code' in params:
        code = params['code'][0]
        print(f"\n✅ Found authorization code!")
        print(f"Code: {code}")
        print(f"\n📋 Now run this command:")
        print(f"python post_with_code.py {code}")
        return code
    else:
        print("\n❌ No authorization code found in URL")
        print("Make sure you copied the entire URL from the browser")
        return None


if __name__ == "__main__":
    print("\n💡 After authorizing LinkedIn, your browser shows an error page.")
    print("   That's OK! Just copy the ENTIRE URL from your browser's address bar.")
    print("\nPaste the redirect URL here:")
    
    url = input("> ").strip()
    
    if url:
        code = extract_code(url)
        
        if code:
            print("\n🚀 Ready to post to LinkedIn!")
            print("Run the command shown above.")
    else:
        print("No URL provided")