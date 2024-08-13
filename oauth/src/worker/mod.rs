pub mod worker {
    use std::env;
    use log::{error, info, logger, warn};

    use anyhow::Error;
    use oauth2::{
        AuthorizationCode,
        AuthUrl,
        ClientId,
        ClientSecret,
        CsrfToken,
        PkceCodeChallenge,
        RedirectUrl,
        Scope,
        TokenResponse,
        TokenUrl
    };
    use oauth2::basic::BasicClient;
    use oauth2::reqwest::async_http_client;
    use oauth2::url::Url;




    use tokio::net::TcpListener;
    use tokio::io::{AsyncReadExt, AsyncWriteExt};

    trait URL {
        fn get_url(self: &Self) -> String;
    }
    trait Endpoint {
        fn get_val(self: &Self) -> String;

    }
    pub enum DexcomMode {
        Sandbox,
        Production
    } 
    pub enum DexcomClient {
        ClientId,
        ClientSecret,
        AuthUrl,
        TokenUrl,
        RedirectUrl
    }


    impl URL for DexcomMode {
        fn get_url(self: &Self) -> String{
            match self {
                DexcomMode::Sandbox => "https://sandbox-api.dexcom.com",
                DexcomMode::Production => "https://api.dexcom.com"
            }.to_string()
        }
    }
    
    impl Endpoint for DexcomClient {
        fn get_val(self: &Self) -> String{
            match self {
                DexcomClient::ClientId => "buW1km1Ig6BfWwh0S0S5phKWhmQSse8t",
                DexcomClient::ClientSecret => "NVFP7f9QiBkFKriT",
                DexcomClient::AuthUrl => "/v2/oauth2/login",
                DexcomClient::TokenUrl => "/v2/oauth2/token",
                DexcomClient::RedirectUrl => "http://172.28.244.153:3321/dexcom"
                

            }.to_string()
        }
    }
    

    pub async fn get_auth<T>(mode: &T ) -> ()
    where 
    T: URL
    {
         // Create an OAuth2 client by specifying the client ID, client secret, authorization URL and
    // token URL.
    let client =
    BasicClient::new(
        ClientId::new(format!("{}{}", mode.get_url(), DexcomClient::ClientId.get_val())),
        Some(ClientSecret::new(format!("{}{}", mode.get_url(), DexcomClient::ClientSecret.get_val()))),
        AuthUrl::new(format!("{}{}", mode.get_url(), DexcomClient::AuthUrl.get_val())).unwrap(),
        Some(TokenUrl::new(DexcomClient::TokenUrl.get_val()).unwrap())
    )
    // Set the URL the user will be redirected to after the authorization process.
    .set_redirect_uri(RedirectUrl::new(DexcomClient::TokenUrl.get_val()).unwrap());

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

     
    }
}