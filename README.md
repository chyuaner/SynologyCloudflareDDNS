## chyuaner版本的SynologyCloudflareDDNS
### 安裝步驟
1. 在 Synology NAS 的網頁介面中，從套件中心安裝 `Python 3`。
2. 啟用 SSH 連線並登入您的 NAS。
3. 為 Python 3 安裝 `pip`，接著安裝此套件：

```
sudo python3 -m ensurepip
sudo python3 -m pip install --upgrade pip setuptools
sudo python3 -m pip install "git+https://github.com/chyuaner/SynologyCloudflareDDNS.git"
```

### 設定到 Synology DSM
請透過編輯 `/etc.defaults/ddns_provider.conf` 將此腳本整合到 Synology 的 DDNS 管理介面中，並在檔案末端加上以下文字：

```
[Cloudflare]
        modulepath=/bin/synology_cloudflare_ddns
        queryurl=https://www.cloudflare.com/
```

接著前往 NAS 網頁介面的 DDNS 管理頁面（控制台 -> 外部存取 -> DDNS）。
點選「新增」，在「服務供應商」下拉選單中選擇「Cloudflare」，並填寫三個必要欄位：
- 主機名稱：就是你要設置的完整域名（子域名包含後綴域名）
- 使用者名稱：填 Email
- 密碼：填 Cloudflare API 金鑰或權限足夠的 API Token。

設定完成！接著即可測試您的 DDNS IP 是否已成功在您的 Cloudflare 頁面上更新。

注意！本專案有處理IPv6，但受限於原生DSM DDNS介面設計，不會顯示IPv6相關，但是實際套用時，會自動以。

### 本專案有特別修改處理的部份
本分支版本特別針對原版在 Synology DSM 7+ 環境下使用時的相容性問題及重大安全漏洞進行了修復與優化：

#### 主要功能修改
1. **支援 IPv6 自動偵測與雙棧聯動更新 (Dual-Stack)**：
   * Synology 的自訂 DDNS UI 本身有系統限制，**只會顯示 IPv4 的欄位，不提供 IPv6 設定**。
   * 本專案在執行時會**自動偵測**本機實體網卡（包括 PPPoE）或透過外網 API（`api6.ipify.org` 等）取得您 NAS 目前的公網 IPv6 位址。
   * 當 DSM 觸發更新傳入 IPv4 時，本腳本會在同一次執行中**同時更新 A 紀錄 (IPv4) 與 AAAA 紀錄 (IPv6)**。您完全不需等待 DSM UI 出現 IPv6 欄位，即可享用雙棧更新。

2. **尊重並保留 Cloudflare 原有的橘雲（Proxied，代理狀態）**：
   * 原版腳本會將更新的紀錄強制開啟橘雲代理。由於 NAS 上常運行非標準 HTTP 埠的服務（如 VPN、SSH、DSM 管理埠），這會導致連線被阻擋。
   * 本專案修改為：**更新時會主動查詢並沿用您在 Cloudflare 後台手動設定的雲朵顏色**。如果您在 Cloudflare 後台關閉橘雲（灰雲），本腳本在更新 IP時便會保持灰雲；若為全新建立的紀錄，則預設建立為灰雲（DNS Only），且可透過 `--proxy` 參數在手動執行時強制開啟。

3. **修復子網域 (Subdomain) 被覆蓋與誤更新整個 Zone 的安全 Bug**：
   * 原版腳本會將輸入的 Hostname 直接覆蓋為主域名 (Zone name)，並在查詢 DNS 紀錄時漏掉 name 過濾條件。這會導致它更新該網域下**所有**同類期的紀錄，甚至意外覆蓋其他子網域。
   * 本專案修正了這個重大 bug，確保只查詢與修改指定的子網域，且不會影響主網域名稱及其他紀錄。

#### 其他技術修改

1. **修正狀態回傳代碼以解決 DSM 介面顯示「失敗」的問題**：
   * 原版腳本沒有向 `stdout` 輸出任何 Synology DDNS 引擎預期的狀態代碼（如 `good`, `nochg`, `badauth` 等），導致 DSM UI 始終顯示「失敗」或「未知錯誤」。
   * 本專案修正了此問題，讓腳本在成功或失敗時輸出正確的狀態碼，使 DSM UI 能正常顯示「正常」綠色狀態。

2. **自動判定並支援 Global API Key 與 Scoped API Token**：
   * 原版腳本強制使用 Scoped API Token 進行初始化，當使用者填入 Global API Key 時會因格式不符導致驗證失敗。
   * 本專案新增判定：當使用者名稱填入 Email 且密碼欄位符合 32 字元的 Hex 時，會自動使用 `Email + Global API Key` 方式認證；否則會退回使用 API Token，完美相容兩種認證方式。

3. **修復 python-json-logger 依賴錯誤引起的執行崩潰**：
   * 修正了 `pyproject.toml` 中的 `python-cloudflare` 依賴名稱為官方發行的 `cloudflare`，並升級到 2.19.4。
   * 修改了 json 紀錄器 formatter，不再強制依賴額外的 `orjson` 套件，避免新版 `python-json-logger` 因為找不到 `orjson` 而導致執行崩潰。


## butlerx/SynologyCloudflareDDNS 原專案說明
A simple script to update CloudFlare DDNS for Synology NAS. This script can be
integrated into Synology NAS UI. It largely refers to
[official CloudFlare's API example for Python](https://raw.githubusercontent.com/cloudflare/python-cloudflare/master/examples/example_update_dynamic_dns.py)

### Installation

1.  Install python3 from synology package using the NAS web interface.
2.  Enable the SSH connection and ssh into your NAS
3.  Install pip for python3, then get python-cloudflare

```
sudo python3 -m ensurepip
sudo python3 -m pip install --upgrade pip setuptools
sudo python3 -m pip install "git+https://github.com/chyuaner/SynologyCloudflareDDNS.git"
```

### Usage

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

### Synology Integration

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
