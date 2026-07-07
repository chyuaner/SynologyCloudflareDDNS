"""cli args"""

from argparse import ArgumentParser


def get_args():
    """get command line args"""
    parser = ArgumentParser(
        description="automatically update cloudflare dns on ip change"
    )
    parser.add_argument("email", type=str, help="This is not used.")
    parser.add_argument(
        "api_key",
        type=str,
        help="Cloudflare API key. Find it in your Cloudflare dashboard under 'My Profile' > 'API Tokens'. See: https://support.cloudflare.com/hc/en-us/articles/200167836-Where-do-I-find-my-Cloudflare-API-key-",
    )
    parser.add_argument("hostname", type=str, help="domain name to update")
    parser.add_argument(
        "ip_address", type=str, help="current IP address to set domain to"
    )
    parser.add_argument("--log-level", default="ERROR", help="logging level")
    parser.add_argument(
        "--log-format",
        choices=["kv", "json"],
        default="kv",
        help="log format: kv (default) or json",
    )
    parser.add_argument(
        "--proxy",
        action="store_true",
        help="Enable Cloudflare proxy (orange cloud) for new records. Existing records preserve their status.",
    )
    return parser.parse_args()
