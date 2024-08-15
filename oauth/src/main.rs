use std::time::Duration;

use anyhow::Error;
use log::info;
use oauth2::basic::BasicClient;
use oauth2::reqwest::async_http_client;
use oauth2::url::Url;
use oauth2::{
    AuthUrl, AuthorizationCode, ClientId, ClientSecret, CsrfToken, PkceCodeChallenge, RedirectUrl,
    Scope, TokenResponse, TokenUrl,
};

use reqwest;

use tokio::io::{AsyncReadExt, AsyncWriteExt};
use tokio::net::TcpListener;
use tokio::time::sleep;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Create an OAuth2 client by specifying the client ID, client secret, authorization URL and
    // token URL.
    let client = BasicClient::new(
        ClientId::new("buW1km1Ig6BfWwh0S0S5phKWhmQSse8t".to_string()),
        Some(ClientSecret::new("NVFP7f9QiBkFKriT".to_string())),
        AuthUrl::new("https://sandbox-api.dexcom.com/v2/oauth2/login".to_string())?,
        Some(TokenUrl::new(
            " https://sandbox-api.dexcom.com/v2/oauth2/token".to_string(),
        )?),
    )
    // Set the URL the user will be redirected to after the authorization process.
    .set_redirect_uri(RedirectUrl::new(
        "http://172.28.244.153:3321/endpoints/dexcom".to_string(),
    )?);

    // Generate a PKCE challenge.
    let (pkce_challenge, pkce_verifier) = PkceCodeChallenge::new_random_sha256();

    // Generate the full authorization URL.
    let (auth_url, csrf_token) = client
        .authorize_url(CsrfToken::new_random)
        .use_implicit_flow()
        .url();

    // This is the URL you should redirect the user to, in order to trigger the authorization
    // process.
    println!("{}&token={}", auth_url, "".to_string());
    /*
    
    dbg!(csrf_token.secret());
    for x in 1..100 {
        let body = reqwest::get(format!(
            "http://172.28.244.153:3321/state?state={}",
            csrf_token.secret()
        ))
        .await?
        .text()
        .await?;

        if body == *csrf_token.secret() {
            println!("matched");

            break;
        }
        println!("No match yet.");

        ()
    } */

    Ok(())

    // Unwrapping token_result will either produce a Token or a RequestTokenError.
}
