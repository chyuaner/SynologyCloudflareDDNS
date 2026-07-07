A simple script to update CloudFlare DDNS for Synology NAS. This script can be
integrated into Synology NAS UI. It largely refers to
[official CloudFlare's API example for Python](https://raw.githubusercontent.com/cloudflare/python-cloudflare/master/examples/example_update_dynamic_dns.py)

# Installation

1.  Install python3 from synology package using the NAS web interface.
2.  Enable the SSH connection and ssh into your NAS
3.  Install pip for python3, then get python-cloudflare

```
sudo python3 -m ensurepip
sudo python3 -m pip install --upgrade pip setuptools
sudo python3 -m pip install "git+https://github.com/chyuaner/SynologyCloudflareDDNS.git"
```

# Usage

```
synology_cloudflare_ddns <email> <api_key> <hostname> <ip_address> [--log-level LEVEL] [--log-format kv|json]
```

- **email**: (Required for Synology UI compatibility, but not used by this
  script)
- **api_key**: Your Cloudflare API key. Find it in your Cloudflare dashboard
  under 'My Profile' > 'API Tokens'.
  [Where do I find my Cloudflare API key?](https://support.cloudflare.com/hc/en-us/articles/200167836-Where-do-I-find-my-Cloudflare-API-key-)
- **hostname**: The domain name to update (e.g., `example.com`).
- **ip_address**: The IP address to set for the DNS record.
- **--log-level**: Logging level (default: ERROR).
- **--log-format**: Log output format: `kv` (key-value, default) or `json`.

# Synology Integration

Integrate the script into Synology DDNS management interface by adding the
following text into `/etc.defaults/ddns_provider.conf`:

```
[Cloudflare]
        modulepath=/bin/synology_cloudflare_ddns
        queryurl=https://www.cloudflare.com/
```

Go to DDNS management page in your NAS web UI (control->external access->DDNS).
Click Add. And select Cloudflare from the drop-down menu. Fill the three
necessary fields which are hostname, username, and password (CloudFlare API
Key).

That's it. See if the DDNS' IP has been updated in your Cloudflare page.
