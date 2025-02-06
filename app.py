from flask import Flask, jsonify
import requests
import os

app = Flask(__name__)

# Load environment variables
TENANT_ID = os.getenv("TENANT_ID")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
GRAPH_BASE_URL = "https://graph.microsoft.com/v1.0"
GLOBAL_ADMIN_ROLE_ID = os.getenv("GLOBAL_ADMIN_ROLE_ID")

def get_access_token():
    """Fetch access token from Microsoft Graph API"""
    token_url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope": "https://graph.microsoft.com/.default",
        "grant_type": "client_credentials"
    }
    response = requests.post(token_url, data=payload)
    response.raise_for_status()
    return response.json().get("access_token")

def get_global_admins(token):
    """Retrieve Global Administrators"""
    url = f"{GRAPH_BASE_URL}/directoryRoles/{GLOBAL_ADMIN_ROLE_ID}/members"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json().get("value", [])

@app.route("/get-global-admins", methods=["GET"])
def fetch_global_admins():
    try:
        token = get_access_token()
        admins = get_global_admins(token)
        formatted_admins = [
            {"name": admin.get("displayName"), "email": admin.get("userPrincipalName")}
            for admin in admins
        ]
        return jsonify({"status": "success", "admins": formatted_admins})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
