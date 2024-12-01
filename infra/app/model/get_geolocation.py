import requests


IPINFO_TOKEN = 'b534c3e4cc0345'

def get_geolocation(ip):
    """Fetch geolocation data using IPinfo API."""
    url = f"https://ipinfo.io/{ip}?token={IPINFO_TOKEN}"
    try:
        response = requests.get(url)
        data = response.json()
        country = data.get('country', 'UNKNOWN')
        city = data.get('city', 'UNKNOWN')
        return country, city
    except Exception as e:
        return 'UNKNOWN', 'UNKNOWN'