import webview
import subprocess
import socket
import time
import threading
import os
import sys

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def find_n8n_command():
    # Try finding n8n in PATH
    try:
        subprocess.check_output(['n8n', '--version'], shell=True, stderr=subprocess.STDOUT)
        return ['n8n', 'start']
    except:
        try:
            subprocess.check_output(['npx', '--version'], shell=True, stderr=subprocess.STDOUT)
            return ['npx', 'n8n', 'start']
        except:
            return None

def start_n8n_process(window):
    if is_port_in_use(5678):
        print(\"n8n is already running.\")
        window.load_url(\"http://localhost:5678\")
        return

    cmd = find_n8n_command()
    if not cmd:
        window.evaluate_js(\"document.body.innerHTML = '<h2 style=\\\"color:white; font-family:sans-serif; text-align:center; padding-top:20%;\\\">Erreur : n8n n\\'est pas installé.<br><br><small style=\\\"font-size:14px; color:#aaa;\\\">Assurez-vous que NodeJS et n8n sont installés.</small></h2>';\")
        return

    # Start n8n in background
    startupinfo = None
    if os.name == 'nt':
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = 0 # SW_HIDE

    try:
        subprocess.Popen(cmd, startupinfo=startupinfo, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
        
        # Wait for n8n to be ready
        attempts = 0
        while not is_port_in_use(5678) and attempts < 60:
            time.sleep(1)
            attempts += 1
            # Update a simple progress indicator in JS if needed
        
        if is_port_in_use(5678):
            window.load_url(\"http://localhost:5678\")
        else:
            window.evaluate_js(\"document.body.innerHTML = '<h2 style=\\\"color:white;\\\">Délai d\\'attente dépassé : n8n ne semble pas démarrer.</h2>';\")
    except Exception as e:
        window.evaluate_js(f\"document.body.innerHTML = '<h2 style=\\\"color:white;\\\">Erreur au lancement : {str(e)}</h2>';\")

loading_html = \"\"\"
<!DOCTYPE html>
<html>
<head>
    <style>
        body { 
            background-color: #1a1a1a; 
            color: white; 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            margin: 0;
            overflow: hidden;
        }
        .loader {
            border: 4px solid #333;
            border-top: 4px solid #ff6d5a;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin-bottom: 20px;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .progress-container {
            width: 300px;
            background-color: #333;
            border-radius: 10px;
            padding: 3px;
        }
        .progress-bar {
            width: 10%;
            height: 10px;
            background-color: #ff6d5a;
            border-radius: 10px;
            transition: width 0.5s ease;
        }
    </style>
</head>
<body>
    <div class=\"loader\"></div>
    <h2>Initialisation de n8n...</h2>
    <p>Vérification du service</p>
    <div class=\"progress-container\">
        <div class=\"progress-bar\" id=\"pb\"></div>
    </div>
    <script>
        let w = 10;
        setInterval(() => {
            if (w < 90) {
                w += 2;
                document.getElementById('pb').style.width = w + '%';
            }
        }, 500);
    </script>
</body>
</html>
\"\"\"

if __name__ == '__main__':
    window = webview.create_window('n8n Desktop Launcher', html=loading_html, width=1280, height=800, background_color='#1a1a1a')
    threading.Thread(target=start_n8n_process, args=(window,), daemon=True).start()
    webview.start()
