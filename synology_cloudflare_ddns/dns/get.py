"""lib for getting dns records"""

from typing import Dict, List

from CloudFlare import CloudFlare
from CloudFlare.exceptions import CloudFlareAPIError
from synology_cloudflare_ddns.utils.logger import get_logger

logger = get_logger("dns.get")


def get_dns_records(
    cf: CloudFlare, zone_id: str, ip_address_type: str
) -> List[Dict[str, str]]:
    """get dns record"""
    try:
        return cf.zones.dns_records.get(
            zone_id, params={"match": "all", "type": ip_address_type}
        )
    except CloudFlareAPIError as err:
        logger.error(
            "api call failed",
            err=err,
            method="zones.dns_records",
            ip_address_type=ip_address_type,
            zone_id=zone_id,
        )
        return []
