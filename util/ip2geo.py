import geoip2.database

# Reader is a bit expensive to instantiate so create a singleton instance
# initialized once at import time.
reader = geoip2.database.Reader('./data/ip2geo/GeoLite2-Country.mmdb')


# Resolves country based on an IP address.
# Returns 2 letter ISO country code or None.
def get_country(ip):
    try:
        data = reader.country(ip)
    except:
        return None
    return data.country.iso_code