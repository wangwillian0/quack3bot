import urllib.request, urllib.parse, webbrowser, json
from http.server import BaseHTTPRequestHandler, HTTPServer

CLIENT_ID = ""
CLIENT_SECRET = ""
REFRESH_TOKEN = ""
ACCESS_TOKEN = ""
SCRIPT = ""
LABELS = []
PORT = 8000
SCOPE = "https://www.googleapis.com/auth/gmail.modify"
OAUTH2_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
LABELS_ENDPOINT = "https://gmail.googleapis.com/gmail/v1/users/me/labels"
SCRIPT_ENDPOINT = "https://raw.githubusercontent.com/wilwxk/quack3bot/main/quack3bot.js"

def get_refresh_token(code):
    url = TOKEN_ENDPOINT
    data = { "code": code, \
            "client_id": CLIENT_ID, \
            "client_secret": CLIENT_SECRET, \
            "grant_type": "authorization_code", \
            "redirect_uri": "http://localhost:" + str(PORT) }
    headers = {"content-type": "application/x-www-form-urlencoded"}
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

def get_script():
    url = SCRIPT_ENDPOINT
    headers = { "Accept": "text/plain" }
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as response:
        global SCRIPT
        SCRIPT = str(response.read())[2:-1]
        SCRIPT = SCRIPT.replace('GCLIENT_ID_HERE', CLIENT_ID)
        SCRIPT = SCRIPT.replace('GCLIENT_SECRET_HERE', CLIENT_SECRET)
        SCRIPT = SCRIPT.replace('GCLIENT_REFRESH_HERE', REFRESH_TOKEN)


def get_interface():
    return f'''
    <!DOCTYPE HTML>
    <HTML>
    <script>
        const GCLIENT_ID = '{CLIENT_ID}';
        const GCLIENT_SECRET = '{CLIENT_SECRET}';
        const GCLIENT_REFRESH = '{REFRESH_TOKEN}';
        const LABEL_LIST = {LABELS};
        const SCRIPT = '{SCRIPT}';
        let LABELS = {{}};
        function copy_code () {{
            document.getElementById('codespace').select();
            document.execCommand('copy');
        }}
        function update (e) {{
            console.log("updating...");
            LABELS = {{}};
            try {{
                for (label of LABEL_LIST) {{
                    let checkbox = document.getElementById(label['label_id']+"_checkbox");
                    let forms = document.getElementById(label['label_id']);
                    if (checkbox.checked) {{ forms.type = ""; }}
                    else {{ forms.value = ""; forms.type = "hidden"; }}
                    const chat_ids = forms.value.replaceAll(' ', '').split(',');
                    if (chat_ids == [] || "" in chat_ids) {{ throw "fail"; }} 
                    LABELS[label['label_id']] = chat_ids;
                }}
                let final_script = SCRIPT;
                const admin_ids = document.getElementById('admins').value.replaceAll(' ', '').split(',');
                const telegram_secret = document.getElementById('telegram_secret').value;
                final_script = final_script.replace('LABELS_HERE', JSON.stringify(LABELS, null, 2));
                final_script = final_script.replace('TELEGRAM_SECRET_HERE', telegram_secret);
                final_script = final_script.replace('ADMINS_HERE', JSON.stringify(admin_ids));
                document.getElementById('codespace').value = final_script;
            }}
            catch(e) {{}}
            
            
        }}
        window.onload = function () {{
            console.log("carregou");
            for (label of LABEL_LIST) {{
                let checkbox = document.createElement("input");
                let input = document.createElement("input");
                let section = document.getElementById('choices');
                checkbox.type = "checkbox";
                checkbox.id = label['label_id']+"_checkbox";
                checkbox.oninput = update;
                input.id = label['label_id'];
                input.placeholder = "@channel, 9999999999";
                input.type = "hidden";
                input.oninput = update
                section.appendChild(checkbox);
                section.appendChild(document.createTextNode(label['name']+" \\u2003"))
                section.appendChild(input);
                section.appendChild(document.createElement('br'));
            }}
        }}
    </script>
    <head>
        <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🦆</text></svg>">
    </head>
    <body>
        Enter the telegram bot api key: &emsp;
        <input oninput="update(this)" id=telegram_secret placeholder="9999999999:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx">
        <br><br><br>
        Enter all the admins that will receive debug messages: &emsp;
        <input oninput="update(this)" id=admins placeholder="1234567890, 9999999999">
        <br><br><br>
        <p> Select the labels and enter the users/channels to
            read the email and send to you by telegram. </p>
        <br>
        <div id=choices></div>
        <br>
        <button onclick="copy_code()">click to copy to clipboard</button>
        <br>
        <textarea id="codespace" style="width:100%;height:2200px" readonly></textarea>
    </body>
    </HTML>
    '''

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
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
        try:
            get_script()
        except Exception as e:
            print("Error trying to get quack3bot.js from repository:")
            print(e)
        self.send_response(200)
        self.send_header("Content-type","text/html;charset=UTF-8")
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
