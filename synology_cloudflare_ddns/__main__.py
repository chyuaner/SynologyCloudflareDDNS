#!/usr/bin/env python3
"""
This code is largely from
https://raw.githubusercontent.com/cloudflare/python-cloudflare/master/examples/example_update_dynamic_dns.py
"""

import logging

from CloudFlare import CloudFlare
from CloudFlare.exceptions import CloudFlareAPIError
from synology_cloudflare_ddns.utils.logger import get_logger

from . import dns
from .utils import get_args, setup_logger

logger = get_logger("synology_cloudflare_ddns")


def detect_ipv6() -> str:
    import urllib.request
    import socket
    import ipaddress
    
    # Try external API first
    for url in ["https://api6.ipify.org", "https://v6.ident.me"]:
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=3) as response:
                ip = response.read().decode("utf-8").strip()
                ip_obj = ipaddress.IPv6Address(ip)
                if not ip_obj.is_loopback and not ip_obj.is_link_local:
                    return str(ip_obj)
        except Exception:
            continue
            
    # Fallback to local /proc/net/if_inet6
    try:
        with open("/proc/net/if_inet6", "r") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 6:
                    addr_hex = parts[0]
                    scope = int(parts[3], 16)
                    # scope == 0 means Global Unicast
                    if scope == 0:
                        blocks = [addr_hex[i:i+4] for i in range(0, 32, 4)]
                        addr = ":".join(blocks)
                        ip_obj = ipaddress.IPv6Address(addr)
                        if not ip_obj.is_loopback and not ip_obj.is_link_local:
                            return str(ip_obj)
    except Exception:
        pass
    return None


def update_records(api_key: str, dns_name: str, ip_address: str, email: str = None):
    """main function"""
    original_dns_name = dns_name
    try:
        zone_name = dns.parse_zone_name(dns_name)

        # Determine authentication method
        import re
        is_hex_32 = bool(re.match(r"^[0-9a-fA-F]{32}$", api_key))
        if email and "@" in email and is_hex_32:
            logger.info("Using Email + Global API Key authentication")
            cloudflare = CloudFlare(email=email, key=api_key)
        else:
            logger.info("Using Scoped API Token authentication")
            cloudflare = CloudFlare(token=api_key)

        zones = dns.get_zones(cloudflare, zone_name)

        if not zones:
            logger.error("no zone specified", zone_name=zone_name)
            print("nohost")
            return 2

        if len(zones) != 1:
            logger.error(
                "api call returned multiple items",
                zone_name=zone_name,
                num_zones=len(zones),
                method="zones.get",
            )
            print("nohost")
            return 2

        zone_id = zones[0]["id"]

        # Prepare list of updates to perform
        # Each update is a tuple: (ip_type, ip_val)
        updates = []

        if ":" in ip_address:
            # The passed IP is IPv6. Update AAAA record.
            updates.append(("AAAA", ip_address))
        else:
            # The passed IP is IPv4. Update A record.
            updates.append(("A", ip_address))
            # Also try to auto-detect IPv6 to update AAAA record.
            ipv6_addr = detect_ipv6()
            if ipv6_addr:
                logger.info("Auto-detected IPv6 address", ip=ipv6_addr)
                updates.append(("AAAA", ipv6_addr))

        any_changed = False
        any_success = False

        for ip_address_type, target_ip in updates:
            # Fetch records matching this specific subdomain/domain name
            dns_records = dns.get_dns_records(cloudflare, zone_id, original_dns_name, ip_address_type)

            updated = False
            unchanged = True

            # update the record - unless it's already correct
            for dns_record in dns_records:
                if ip_address_type != dns_record["type"]:
                    continue

                if target_ip == dns_record["content"]:
                    updated = True
                    continue
                dns.update_record(
                    cloudflare,
                    zone_id,
                    dns_record["id"],
                    dns_record["name"],
                    ip_address_type,
                    target_ip,
                )
                unchanged = False
                updated = True

            if updated:
                if not unchanged:
                    any_changed = True
                any_success = True
            else:
                # No record was updated, so add a new record
                dns.add_record(cloudflare, zone_id, original_dns_name, ip_address_type, target_ip)
                any_changed = True
                any_success = True

        if any_success:
            if any_changed:
                print("good")
            else:
                print("nochg")
            return 0
        else:
            print("system")
            return 2

    except CloudFlareAPIError as err:
        try:
            code = int(err)
        except Exception:
            code = 0
        
        # Authentication error codes:
        # 6003: Invalid request headers (usually bad token format/invalid token)
        # 9103: Unknown API key or email (usually bad global API key/email combination)
        # 9109: Invalid API Token
        if code in [6003, 9103, 9109]:
            logger.error("Authentication failed", err=err)
            print("badauth")
        else:
            logger.error("Cloudflare API error", err=err)
            print("system")
        return 2
    except Exception as err:
        err_msg = str(err).lower()
        if "connect" in err_msg or "timeout" in err_msg or "resolv" in err_msg:
            logger.error("Connection failure", err=err)
            print("connfail")
        else:
            logger.error("Unexpected error", err=err)
            print("system")
        return 2


def main():
    args = get_args()
    setup_logger(getattr(logging, args.log_level), log_format=args.log_format)
    exit(update_records(args.api_key, args.hostname, args.ip_address, args.email))


if __name__ == "__main__":
    main()
