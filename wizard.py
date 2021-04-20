import urllib.request, urllib.parse, webbrowser, json
from http.server import BaseHTTPRequestHandler, HTTPServer

CLIENT_ID = ""
CLIENT_SECRET = ""
REFRESH_TOKEN = ""
ACCESS_TOKEN = ""
LABELS = []
SCOPE = "https://www.googleapis.com/auth/gmail.modify"
PORT = 8000
OAUTH2_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
LABELS_ENDPOINT = "https://gmail.googleapis.com/gmail/v1/users/me/labels"

def get_refresh_token(code):
    url = TOKEN_ENDPOINT
    data = { "code": code, \
            "client_id": CLIENT_ID, \
            "client_secret": CLIENT_SECRET, \
            "grant_type": "authorization_code", \
            "redirect_uri": "http://localhost:" + str(PORT) }
    headers={"content-type": "application/x-www-form-urlencoded"}
    data = urllib.parse.urlencode(data)
    data = data.encode("ascii")
    req = urllib.request.Request(url, data, headers)
    with urllib.request.urlopen(req) as response:
        result = response.read()
        result = json.loads(result)
        global REFRESH_TOKEN, ACCESS_TOKEN
        REFRESH_TOKEN = result["refresh_token"]
        ACCESS_TOKEN = result["access_token"]

def get_labels():
    url = LABELS_ENDPOINT
    headers = { "Accept": "application/json", \
            "Content-Type": "application/json", \
            "Authorization": "Bearer " + ACCESS_TOKEN }
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as response:
        result = response.read()
        result = json.loads(result)
        global LABELS
        for label in result["labels"]:
            if label["type"] != "system":
                LABELS.append({"name": label["name"], "label_id": label["id"]})

def get_interface():
    return f'client_id: {CLIENT_ID}\nclient_secret: {CLIENT_SECRET}\nrefresh_token: {REFRESH_TOKEN}\n\n\nlabels:\n\n{json.dumps(LABELS, indent=4)}'

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/favicon.ico":
            return
        code = ((self.path).split("code=")[1]).split("&")[0]
        try:
            get_refresh_token(code)
        except Exception as e:
            print("Error trying to get Refresh Token from google account:")
            print(e)
        try:
            get_labels()
        except Exception as e:
            print("Error trying to get labels from gmail:")
            print(e)
        self.send_response(200)
        self.send_header("Content-type","text")
        self.end_headers()
        message = get_interface()
        self.wfile.write(bytes(message, "utf8"))
    def log_message(self, format, *args):
        return

if __name__ == "__main__":
    print("Enter the client id (it ends with ...apps.googleusercontent.com):")
    CLIENT_ID = input()
    print("\nEnter the client secret:")
    CLIENT_SECRET = input()

    print("\n" + "-"*32 + "\n")
    print("You should be redirected to the web interface now")
    print("If not, copy and paste the following URL in your browser:\n")
    oauth_url = ( OAUTH2_ENDPOINT + "?" +  
        "scope=" + urllib.parse.quote(SCOPE) + "&" + 
        "access_type=offline&" + 
        "response_type=code&" + 
        "prompt=consent&include_granted_scopes=true&" + 
        "state=quack3bot&" + 
        "redirect_uri=" + "http://localhost:" + str(PORT) + "&" + 
        "client_id=" + CLIENT_ID )
    print(oauth_url)
    print("\n" + "-"*32 + "\n")


    webbrowser.open(oauth_url)
    with HTTPServer(("", PORT), handler) as server:
        server.serve_forever()
