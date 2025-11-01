import requests
# Temporary test function
def test_url_access():
    test_url = "your-supabase-url-here"  # The URL that's failing
    try:
        response = requests.get(test_url)
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type')}")
        print(f"Content length: {len(response.content)}")
    except Exception as e:
        print(f"Error: {e}")


test_url_access("")