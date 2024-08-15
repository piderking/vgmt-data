# VGMT Data Collection
> A Collection of OAuth and data storage / viewing tools for VGMT ecosystem

## OAuth
- Rust OAuth Based Client 
    - Results are sent to [Data / OAuthServer](#data--oauth-server)
- [Code](/oauth/src/lib.rs)

## Data / OAuth Server
- [Code](/server/__main__.py)

## Enviorment Variables
- `TOML_FILE_PATH={default=auth.toml}`
    - [Code](/server/env.py)
    - *(optional)*

## TOML Settings File
System Config Settings, don't manipulate, leave default. 
```toml 
[oauth]
redirect_url = "/"

[server]
port = 3321
debug = true
host = "0.0.0.0"
```
### Client Configs

```toml
[dexcom] # Service Name
client_id = "############################se8t" # OAuth Client ID
client_secret = "##########riT" # OAuth Clilent Secret
auth_url = "/v2/oauth2/login" # Endpoint to start auth
token_url = "/v2/oauth2/token" # Endpoint to exchange authorization code with access token
sandbox = true # Enable / Disable Sandbox
sandbox_url="https://sandbox-api.dexcom.com" # Sandbox API
production_url="https://api.dexcom.com" # Production API
```
