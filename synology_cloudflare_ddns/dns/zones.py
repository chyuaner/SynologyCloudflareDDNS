"""zone functions"""

from typing import Dict, List

from CloudFlare import CloudFlare
from CloudFlare.exceptions import CloudFlareAPIError
from synology_cloudflare_ddns.utils.logger import get_logger

logger = get_logger("dns.zones")


def get_zones(cf: CloudFlare, zone_name: str) -> List[Dict[str, str]]:
    """grab the zone identifier"""
    try:
        return cf.zones.get(params={"name": zone_name})
    except CloudFlareAPIError as err:
        logger.error(
            "bad authentication", method="zones.get", zone_name=zone_name, err=err
        )
    except Exception as err:
        logger.error(
            "api call failed", method="zones.get", zone_name=zone_name, err=err
        )
    return []


def parse_zone_name(dns_name: str) -> str:
    """parse zone name from dns string"""
    _, zone_name = dns_name.split(".", 1)
    if "." not in zone_name:
        return dns_name
    return zone_name
