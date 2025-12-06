#!/usr/bin/env python3
"""
This code is largely from
https://raw.githubusercontent.com/cloudflare/python-cloudflare/master/examples/example_update_dynamic_dns.py
"""

import logging

from CloudFlare import CloudFlare
from synology_cloudflare_ddns.utils.logger import get_logger

from . import dns
from .utils import get_args, setup_logger

logger = get_logger("synology_cloudflare_ddns")


def update_records(api_key: str, dns_name: str, ip_address: str):
    """main function"""
    zone_name = dns.parse_zone_name(dns_name)
    ip_address_type = "AAAA" if ":" in ip_address else "A"
    cloudflare = CloudFlare(token=api_key)
    zones = dns.get_zones(cloudflare, zone_name)

    if not zones:
        logger.info("no zone specified", zones=zones, zone_name=zone_name)
        return 0

    if len(zones) != 1:
        logger.error(
            "api call returned multiple items",
            zone_name=zone_name,
            num_zones=len(zones),
            method="zones.get",
        )
        return 2

    dns_records = dns.get_dns_records(cloudflare, zones[0]["id"], ip_address_type)
    if not dns_records:
        return 2

    zone_id = zones[0]["id"]
    dns_name = zones[0]["name"]
    updated = False
    unchanged = True

    # update the record - unless it's already correct
    for dns_record in dns_records:
        if ip_address_type != dns_record["type"]:
            continue

        if ip_address == dns_record["content"]:
            updated = True
            continue
        dns.update_record(
            cloudflare,
            zone_id,
            dns_record["id"],
            dns_record["name"],
            ip_address_type,
            ip_address,
        )
        unchanged = False
        updated = True

    if updated:
        if unchanged:
            logger.info(
                "No Change required",
                name=dns_name,
                type=ip_address_type,
                address=ip_address,
            )
        return 0

    dns.add_record(cloudflare, zone_id, dns_name, ip_address_type, ip_address)
    return 0


def main():
    args = get_args()
    setup_logger(getattr(logging, args.log_level), log_format=args.log_format)
    exit(update_records(args.api_key, args.hostname, args.ip_address))


if __name__ == "__main__":
    main()
