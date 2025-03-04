from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://mail.google.com/']

flow = InstalledAppFlow.from_client_secrets_file(
    'client_secret.json', SCOPES,
    redirect_uri='http://localhost:8080/'
)
creds = flow.run_local_server(port=8080)

print("Access Token:", creds.token)
print("Refresh Token:", creds.refresh_token)
print("Client ID:", creds.client_id)
print("Client Secret:", creds.client_secret)
