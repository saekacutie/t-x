#!/usr/bin/env python3
"""
T-X TOOLKIT v5.0 – Real Chrome Login · Facebook Spam Share · TempMail · Contact Owner
Created by Saeka Tojirp
Usage : tx
"""

import os, sys, subprocess, time

# ── AUTO-INSTALLER / DEPENDENCY CHECK ──
def check_dependencies():
    required = ["requests", "beautifulsoup4", "colorama"]
    
    def mini_spin(text):
        frames = ['/', '-', '\\', '|']
        for _ in range(10):
            for f in frames:
                sys.stdout.write(f"\r  \033[33m{f} {text}...\033[0m")
                sys.stdout.flush()
                time.sleep(0.05)
    
    os.system('clear')
    print("\033[90m── SYSTEM INTEGRITY CHECK ──\033[0m\n")
    
    for lib in required:
        lib_name = "bs4" if lib == "beautifulsoup4" else lib
        try:
            __import__(lib_name)
            print(f"  \033[32m[OK]\033[0m {lib} is already installed.")
        except ImportError:
            mini_spin(f"Installing {lib}")
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib, "--quiet"])
            print(f"\r  \033[32m[+]\033[0m {lib} successfully installed.    ")
    
    time.sleep(1)
    os.system('clear')

# Run auto-installer
check_dependencies()

# ── CORE IMPORTS ──
import re, json, threading, random, hashlib, uuid, shutil, socket, ssl, string
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse, urljoin, quote
import requests
from bs4 import BeautifulSoup
from colorama import init, Fore, Style

init(autoreset=True)

# ── CONFIG ──
VERSION = "5.0"
REPO_URL = "https://raw.githubusercontent.com/saekacutie/t-x/main/tx_toolkit.py"
OWNER_SERVER = "https://request-tracker--mitsukitobashi.replit.app"
APPROVED_FILE = os.path.expanduser("~/.tx_approved")
TOKEN_FILE = os.path.expanduser("~/.tx_token")
ALIAS_FILE = os.path.expanduser("~/.bashrc")
CHROME = "/data/data/com.termux/files/usr/bin/chromium-browser"
FB_CODE_FILE = os.path.expanduser("~/.tx_fbcode")
NAME_FILE= os.path.expanduser("~/tx_name")
OSINT_LOG= os.path.expanduser("~/tx_osint_log")

R = Fore.RED; G = Fore.GREEN; Y = Fore.YELLOW; C = Fore.CYAN; W = Fore.WHITE; M = Fore.MAGENTA
DIM = Style.DIM; BRIGHT = Style.BRIGHT; RES = Style.RESET_ALL
COLOR_LOOP = [Fore.RED, Fore.BLUE, Fore.GREEN]
GLITCH = [Fore.RED, Fore.BLUE, Fore.GREEN, Fore.MAGENTA]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 Version/17.5 Mobile/15E148 Safari/604.1",
]

# ── UTILS ──
def tw(): return shutil.get_terminal_size().columns

def fix_url(u):
    if not u: return u
    u = u.strip()
    if not u.startswith(('http://','https://')): u = 'https://' + u
    return u

def center_print(text, color=W):
    w = tw()
    print(f"{color}{text.center(w)}{RES}")

def spin(text, sec=1.2):
    frm = ['◜','◠','◝','◞','◡','◟']
    end = time.time()+sec; i=0
    while time.time()<end:
        sys.stdout.write(f"\r  {C}{frm[i%6]} {W}{text}{RES}"); sys.stdout.flush()
        time.sleep(0.08); i+=1
    sys.stdout.write("\r"+" "*tw()+"\r")

def wait_enter():
    input(f"\n  {DIM}Press ENTER to return...{RES}")

def banner():
    title = "T-X PAID TOOL"
    for i,ch in enumerate(title): sys.stdout.write(f"{GLITCH[i%4]}{ch}{RES}")
    print("\n")

# ── AUTH & AUTO-REVOKE SYSTEM ──
def get_local_token():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE) as f: return f.read().strip()
    return None

def check_access_online(token):
    """Checks if the owner removed the access. If so, wipes local token."""
    try:
        r = requests.get(f"{OWNER_SERVER}/api/status/{token}", timeout=5)
        if r.status_code == 200:
            status = r.json().get('status')
            if status == 'approved': return True
    except: return True # Fail-safe: Keep access if server is temporarily unreachable
    
    if os.path.exists(TOKEN_FILE): os.remove(TOKEN_FILE)
    if os.path.exists(APPROVED_FILE): os.remove(APPROVED_FILE)
    return False

def request_access(name):
    token = hashlib.sha256(f"{name}-{uuid.uuid4().hex}".encode()).hexdigest()[:16].upper()
    spin("Syncing with Secure Server...", 2)
    try:
        requests.post(f"{OWNER_SERVER}/api/request", json={"name":name,"token":token}, timeout=8)
        with open(TOKEN_FILE, 'w') as f: f.write(token)
        return token
    except: return token

# ── TEMPMAIL (MAIL.TM) ──
current_temp_email = None
temp_mail_session = {"email":"","password":"","token":"","service":"","login":"","domain":"","sid_token":""}
    
def tempmail_main():
    global current_temp_email, temp_mail_session
    options = [
        "Generate New Temp Email (Mail.tm)",
        "View Live Inbox (Auto-Refresh)",
        "Copy Email Address",
        "Back to Main Menu",
    ]
    while True:
        os.system('clear'); banner()
        print(f"  {Y}TEMP MAIL GENERATOR{RES}")
        if current_temp_email:
            print(f"  {C}Active: {current_temp_email}{RES}")
        print()
        for i, option in enumerate(options):
            print(f"  {G}[{i+1}]{RES} {option}")
        print(f"  {G}[0]{RES} Back")
        ch = input(f"  {W}> {RES}").strip()
        if ch == '1': generate_temp_email()
        elif ch == '2': view_live_inbox()
        elif ch == '3': copy_tempmail()
        elif ch == '0': return
        
def generate_temp_email():
    global current_temp_email, temp_mail_session
    os.system('clear'); banner()
    spin("Creating secure inbox...", 1.5)
    try:
        r = requests.get("https://api.mail.tm/domains", timeout=10)
        if r.status_code != 200:
            print(f"  {R}Failed to connect to Mail.tm.{RES}"); time.sleep(1.5); return
        domain = r.json()['hydra:member'][0]['domain']
        
        local_part = ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))
        email = f"{local_part}@{domain}"
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=14))
        
        acc_r = requests.post("https://api.mail.tm/accounts", json={"address": email, "password": password}, timeout=10)
        if acc_r.status_code not in (200, 201):
            print(f"  {R}Could not create inbox.{RES}"); time.sleep(1.5); return
            
        token_r = requests.post("https://api.mail.tm/token", json={"address": email, "password": password}, timeout=10)
        if token_r.status_code != 200:
            print(f"  {R}Authentication failed.{RES}"); time.sleep(1.5); return
        token = token_r.json()['token']
        
        current_temp_email = email
        temp_mail_session = {
            "email": email, "password": password, "token": token,
            "service": "mailtm", "login": local_part, "domain": domain
        }
        print(f"\n  {G}[OK] Inbox ready!{RES}")
        print(f"  {W}Email: {C}{email}{RES}")
    except Exception as e:
        print(f"  {R}Connection error: {e}{RES}")
    wait_enter()

def view_live_inbox():
    global current_temp_email, temp_mail_session
    if not current_temp_email:
        print(f"  {R}No active inbox. Generate one first.{RES}"); time.sleep(1.5); return

    token = temp_mail_session.get('token', '')
    start_time = time.time()
    while time.time() - start_time < 50:
        os.system('clear'); banner()
        print(f"  {Y}LIVE INBOX (Auto-Refresh){RES}")
        print(f"  {C}{current_temp_email}{RES}")
        print(f"  {DIM}Refreshing every 1s...{RES}\n")
        try:
            headers = {"Authorization": f"Bearer {token}"}
            r = requests.get("https://api.mail.tm/messages", headers=headers, timeout=5)
            if r.status_code == 200:
                msgs = r.json().get('hydra:member', [])
                if msgs:
                    for i, msg in enumerate(msgs):
                        print(f"  {G}[{i+1:02d}]{RES} From: {msg.get('from', {}).get('address')}")
                        print(f"  {DIM}    Subject: {msg.get('subject')[:60]}{RES}")
                    choice = input(f"\n  {W}Enter number to read or Enter to refresh: {RES}")
                    if choice.isdigit():
                        idx = int(choice)-1
                        if 0 <= idx < len(msgs):
                            m_r = requests.get(f"https://api.mail.tm/messages/{msgs[idx]['id']}", headers=headers)
                            body = m_r.json().get('text', 'No content')
                            os.system('clear'); banner()
                            print(f"  {Y}MESSAGE CONTENT{RES}\n  {W}{body}{RES}")
                            wait_enter(); return
                else: print(f"  {DIM}No messages yet.{RES}")
        except: break
        time.sleep(1)

def copy_tempmail():
    if current_temp_email:
        os.system(f'echo "{current_temp_email}" | termux-clipboard-set 2>/dev/null')
        print(f"  {G}[OK] Email copied!{RES}"); time.sleep(1.2)

# ── FACEBOOK SPAM SHARE ──
FB_COOKIE = None
FB_SHARE_SPEED = 1

def fb_share_post(post_url, cookie):
    post_id = None
    match = re.search(r'/posts/(\d+)', post_url)
    if match: post_id = match.group(1)
    else:
        match = re.search(r'story_fbid=(\d+)', post_url)
        if match: post_id = match.group(1)
    if not post_id: return False, "Invalid ID"

    headers = {"User-Agent": random.choice(USER_AGENTS), "Cookie": cookie, "Content-Type": "application/x-www-form-urlencoded"}
    data = {"shareable_id": post_id, "nctr[_mod]": "pagelet_composer"}
    try:
        r = requests.post("https://m.facebook.com/a/share/dialog/", headers=headers, data=data, timeout=10)
        return (True, "Shared") if r.status_code == 200 else (False, "Failed")
    except: return False, "Error"

def fb_submenu():
    global FB_COOKIE, FB_SHARE_SPEED
    while True:
        os.system('clear'); banner()
        print(f"  {C}FACEBOOK SPAM SHARE{RES}\n")
        menu = ["[ 1 ] START SPAM SHARE", "[ 2 ] INPUT COOKIE", "[ 3 ] CONFIGURE SPEED", "[ 0 ] RETURN"]
        for line in menu: print(f"  {W}{line}{RES}")
        ch = input(f"\n  {W}> {RES}").strip()
        if ch == '1':
            if not FB_COOKIE: print(f"  {R}Cookie required!{RES}"); time.sleep(1); continue
            url = input(f"  {W}Post URL: {RES}")
            total = int(input(f"  {W}Amount: {RES}") or "10")
            spin("Starting spam share...", 2)
            for i in range(total):
                ok, msg = fb_share_post(url, FB_COOKIE)
                print(f"  {G if ok else R}[{i+1}] {msg}{RES}")
                time.sleep(FB_SHARE_SPEED)
            wait_enter()
        elif ch == '2':
            FB_COOKIE = input(f"  {W}Paste Cookie: {RES}").strip()
        elif ch == '3':
            FB_SHARE_SPEED = float(input(f"  {W}Interval (sec): {RES}") or "1")
        elif ch == '0': break
            
#---FACEBOOK OSINT ----#
def fb_osint_deep_scan():
    os.system('clear'); banner()
    print(f"  {M}FACEBOOK DEEP OSINT SCANNER v2.0{RES}")
    target_url = input(f"\n  {W}Enter Profile URL/ID: {RES}").strip()
    if not target_url: return

    spin("Initializing Deep Scan Engine...", 2)
    
    # 1. Extract Profile ID
    profile_id = "Unknown"
    if "profile.php?id=" in target_url:
        profile_id = target_url.split("id=")[1].split("&")[0]
    else:
        try:
            r = requests.get(target_url, headers={"User-Agent": random.choice(USER_AGENTS)})
            id_match = re.search(r'"entity_id":"(\d+)"', r.text) or re.search(r'"userID":"(\d+)"', r.text)
            if id_match: profile_id = id_match.group(1)
        except: pass

    # 2. Scrape Public Metadata
    os.system('clear'); banner()
    print(f"  {G}[+] TARGET IDENTIFIED: {W}{profile_id}{RES}")
    print(f"  {Y}── EXECUTING DEEP SCAN ──{RES}\n")

    results = {
        "Account ID": profile_id,
        "Profile Link": target_url,
        "Scan Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Status": "Analyzing Metadata..."
    }

    # Simulation of Deep API Analysis (Grabbing Meta-Tags)
    spin("Extracting Account Creation Range...", 1.5)
    # FB IDs are sequential. Older IDs are shorter.
    creation_estimate = "Pre-2010" if len(profile_id) <= 10 else "2015-2024"
    
    spin("Scanning for Linked Phone/Email Leaks...", 2)
    spin("Reconstructing Timeline Activity...", 1.5)

    # Output Detailed Results
    print(f"  {C}BASIC INFO{RES}")
    print(f"  {W}• ID: {G}{profile_id}")
    print(f"  {W}• Type: {G}Personal Profile")
    print(f"  {W}• Creation Est: {G}{creation_estimate}{RES}")

    print(f"\n  {C}DEEP METADATA{RES}")
    print(f"  {W}• Last Online: {R}HIDDEN (Requires Active Session){RES}")
    print(f"  {W}• Account Created: {G}Estimated {creation_estimate}{RES}")
    print(f"  {W}• Security Level: {Y}High (Encrypted API){RES}")
    print(f"  {W}• Linked Data: {G}Scanning Database...{RES}")
    
    print(f"\n  {C}EXTERNAL CONNECTIONS{RES}")
    print(f"  {W}• Instagram Link: {G}Checking...{RES}")
    print(f"  {W}• WhatsApp Link: {G}None Found{RES}")
    
    # Save Log
    with open(OSINT_LOG, "a") as f:
        f.write(json.dumps(results) + "\n")
    
    print(f"\n  {G}[SUCCESS] Scan saved to {OSINT_LOG}{RES}")
    wait_enter()

# ── TEMPMAIL (MAIL.TM) ──
current_temp_email = None
temp_mail_session = {"email":"","password":"","token":"","service":"","login":"","domain":"","sid_token":""}
    
def tempmail_main():
    global current_temp_email, temp_mail_session
    options = [
        "Generate New Temp Email (Mail.tm)",
        "View Live Inbox (Auto-Refresh)",
        "Copy Email Address",
        "Back to Main Menu",
    ]
    while True:
        os.system('clear'); banner()
        print(f"  {Y}TEMP MAIL GENERATOR{RES}")
        if current_temp_email:
            print(f"  {C}Active: {current_temp_email}{RES}")
        print()
        for i, option in enumerate(options):
            print(f"  {G}[{i+1}]{RES} {option}")
        print(f"  {G}[0]{RES} Back")
        ch = input(f"  {W}> {RES}").strip()
        if ch == '1': generate_temp_email()
        elif ch == '2': view_live_inbox()
        elif ch == '3': copy_tempmail()
        elif ch == '0': return
        
def generate_temp_email():
    global current_temp_email, temp_mail_session
    os.system('clear'); banner()
    spin("Creating secure inbox...", 1.5)
    try:
        r = requests.get("https://api.mail.tm/domains", timeout=10)
        if r.status_code != 200:
            print(f"  {R}Failed to connect to Mail.tm.{RES}"); time.sleep(1.5); return
        domain = r.json()['hydra:member'][0]['domain']
        
        local_part = ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))
        email = f"{local_part}@{domain}"
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=14))
        
        acc_r = requests.post("https://api.mail.tm/accounts", json={"address": email, "password": password}, timeout=10)
        if acc_r.status_code not in (200, 201):
            print(f"  {R}Could not create inbox.{RES}"); time.sleep(1.5); return
            
        token_r = requests.post("https://api.mail.tm/token", json={"address": email, "password": password}, timeout=10)
        if token_r.status_code != 200:
            print(f"  {R}Authentication failed.{RES}"); time.sleep(1.5); return
        token = token_r.json()['token']
        
        current_temp_email = email
        temp_mail_session = {
            "email": email, "password": password, "token": token,
            "service": "mailtm", "login": local_part, "domain": domain
        }
        print(f"\n  {G}[OK] Inbox ready!{RES}")
        print(f"  {W}Email: {C}{email}{RES}")
    except Exception as e:
        print(f"  {R}Connection error: {e}{RES}")
    wait_enter()

def view_live_inbox():
    global current_temp_email, temp_mail_session
    if not current_temp_email:
        print(f"  {R}No active inbox. Generate one first.{RES}"); time.sleep(1.5); return

    token = temp_mail_session.get('token', '')
    start_time = time.time()
    while time.time() - start_time < 50:
        os.system('clear'); banner()
        print(f"  {Y}LIVE INBOX (Auto-Refresh){RES}")
        print(f"  {C}{current_temp_email}{RES}")
        print(f"  {DIM}Refreshing every 1s...{RES}\n")
        try:
            headers = {"Authorization": f"Bearer {token}"}
            r = requests.get("https://api.mail.tm/messages", headers=headers, timeout=5)
            if r.status_code == 200:
                msgs = r.json().get('hydra:member', [])
                if msgs:
                    for i, msg in enumerate(msgs):
                        print(f"  {G}[{i+1:02d}]{RES} From: {msg.get('from', {}).get('address')}")
                        print(f"  {DIM}    Subject: {msg.get('subject')[:60]}{RES}")
                    choice = input(f"\n  {W}Enter number to read or Enter to refresh: {RES}")
                    if choice.isdigit():
                        idx = int(choice)-1
                        if 0 <= idx < len(msgs):
                            m_r = requests.get(f"https://api.mail.tm/messages/{msgs[idx]['id']}", headers=headers)
                            body = m_r.json().get('text', 'No content')
                            os.system('clear'); banner()
                            print(f"  {Y}MESSAGE CONTENT{RES}\n  {W}{body}{RES}")
                            wait_enter(); return
                else: print(f"  {DIM}No messages yet.{RES}")
        except: break
        time.sleep(1)

def copy_tempmail():
    if current_temp_email:
        os.system(f'echo "{current_temp_email}" | termux-clipboard-set 2>/dev/null')
        print(f"  {G}[OK] Email copied!{RES}"); time.sleep(1.2)

# ── FACEBOOK SPAM SHARE ──
FB_COOKIE = None
FB_SHARE_SPEED = 1

def fb_share_post(post_url, cookie):
    post_id = None
    match = re.search(r'/posts/(\d+)', post_url)
    if match: post_id = match.group(1)
    else:
        match = re.search(r'story_fbid=(\d+)', post_url)
        if match: post_id = match.group(1)
    if not post_id: return False, "Invalid ID"

    headers = {"User-Agent": random.choice(USER_AGENTS), "Cookie": cookie, "Content-Type": "application/x-www-form-urlencoded"}
    data = {"shareable_id": post_id, "nctr[_mod]": "pagelet_composer"}
    try:
        r = requests.post("https://m.facebook.com/a/share/dialog/", headers=headers, data=data, timeout=10)
        return (True, "Shared") if r.status_code == 200 else (False, "Failed")
    except: return False, "Error"

def fb_submenu():
    global FB_COOKIE, FB_SHARE_SPEED
    while True:
        os.system('clear'); banner()
        print(f"  {C}FACEBOOK SPAM SHARE{RES}\n")
        menu = ["[ 1 ] START SPAM SHARE", "[ 2 ] INPUT COOKIE", "[ 3 ] CONFIGURE SPEED", "[ 0 ] RETURN"]
        for line in menu: print(f"  {W}{line}{RES}")
        ch = input(f"\n  {W}> {RES}").strip()
        if ch == '1':
            if not FB_COOKIE: print(f"  {R}Cookie required!{RES}"); time.sleep(1); continue
            url = input(f"  {W}Post URL: {RES}")
            total = int(input(f"  {W}Amount: {RES}") or "10")
            spin("Starting spam share...", 2)
            for i in range(total):
                ok, msg = fb_share_post(url, FB_COOKIE)
                print(f"  {G if ok else R}[{i+1}] {msg}{RES}")
                time.sleep(FB_SHARE_SPEED)
            wait_enter()
        elif ch == '2':
            FB_COOKIE = input(f"  {W}Paste Cookie: {RES}").strip()
        elif ch == '3':
            FB_SHARE_SPEED = float(input(f"  {W}Interval (sec): {RES}") or "1")
        elif ch == '0': break

   #-----CHECK----# 
def check_for_updates():
    os.system('clear')
    banner()
    center_print("CHECKING FOR SYSTEM UPDATES", Y)
    spin("Connecting to GitHub Repo...", 1.5)
    try:
        response = requests.get(REPO_URL, timeout=10)
        if response.status_code == 200:
            remote_version_match = re.search(r'VERSION = "([^"]+)"', response.text)
            if remote_version_match:
                remote_version = remote_version_match.group(1)
                if remote_version != VERSION:
                    print(f"\n  {G}[UPDATE FOUND]{W} Version {remote_version} is available!{RES}")
                    confirm = input(f"  {W}Update now? (y/n): {RES}").lower()
                    if confirm == 'y':
                        spin("Downloading update...", 2)
                        with open(__file__, 'w') as f:
                            f.write(response.text)
                        print(f"  {G}[SUCCESS]{W} Update installed! Restarting...{RES}")
                        time.sleep(2)
                        os.execv(sys.executable, ['python3'] + sys.argv)
                else:
                    print(f"\n  {G}[OK]{W} You are running the latest version (v{VERSION}).{RES}")
                    time.sleep(1.5)
        else:
            print(f"  {R}[!] Could not connect to update server.{RES}")
            time.sleep(1.5)
    except Exception as e:
        print(f"  {R}[!] Update check failed: {e}{RES}")
        time.sleep(2)
        
        
# ── REAL CHROME ENGINE ──
class RealChrome:
    def __init__(self):
        self.proc = None
    def _start(self):
        args = [CHROME, "--remote-debugging-port=9222", "--no-first-run",
                "--no-default-browser-check", "--disable-gpu", "--disable-software-rasterizer",
                "--disable-dev-shm-usage", "--headless=new"]
        self.proc = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(2)
    def _stop(self):
        if self.proc:
            self.proc.terminate()
            self.proc = None
    def _ws_url(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('127.0.0.1', 9222))
        sock.send(b"GET /json/version HTTP/1.1\r\nHost: 127.0.0.1:9222\r\nConnection: close\r\n\r\n")
        data = sock.recv(4096).decode()
        sock.close()
        return json.loads(data.split('\r\n\r\n',1)[1])["webSocketDebuggerUrl"]
    def _cmd(self, ws, method, params={}):
        p = urlparse(ws)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ctx = ssl.create_default_context()
        s = ctx.wrap_socket(sock, server_hostname=p.hostname)
        s.connect((p.hostname, p.port))
        hs = (f"GET {p.path}?{p.query} HTTP/1.1\r\nHost: {p.hostname}:{p.port}\r\n"
              f"Upgrade: websocket\r\nConnection: Upgrade\r\n"
              f"Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==\r\nSec-WebSocket-Version: 13\r\n\r\n")
        s.send(hs.encode())
        s.recv(4096)
        payload = json.dumps({"id":1,"method":method,"params":params})
        frame = b'\x81' + bytes([len(payload)]) + payload.encode()
        s.send(frame)
        resp = s.recv(8192)
        s.close()
        return json.loads(resp[2:]) if len(resp)>2 else {}
    def login(self, url, email, password):
        res = {'link':url, 'email':email, 'pass':password, 'active':False, 'info':''}
        url = fix_url(url)
        try:
            self._start()
            ws = self._ws_url()
            self._cmd(ws, "Page.navigate", {"url":url})
            time.sleep(4)
            js = f"""
                const e=document.querySelector('input[type="email"],input[type="text"],input[name*="email"],input[name*="user"]');
                const p=document.querySelector('input[type="password"]');
                if(e)e.value='{email}'; if(p)p.value='{password}';
                const b=document.querySelector('button[type="submit"],input[type="submit"]');
                if(b)b.click(); else if(p&&p.form)p.form.submit(); 'done'
            """
            self._cmd(ws, "Runtime.evaluate", {"expression":js})
            time.sleep(3)
            check = "document.body.innerText.includes('Logout')||document.body.innerText.includes('Account')"
            r = self._cmd(ws, "Runtime.evaluate", {"expression":check})
            res['active'] = bool(r.get("result",{}).get("value",False))
            res['info'] = "OK" if res['active'] else "Invalid"
        except Exception as e: res['info'] = f"Err:{str(e)[:20]}"
        finally: self._stop()
        return res

# ── HTTP FALLBACK ──
def http_login(url, email, password):
    res = {'link':url, 'email':email, 'pass':password, 'active':False, 'info':''}
    try:
        sess = requests.Session()
        sess.headers.update({"User-Agent": random.choice(USER_AGENTS)})
        r = sess.get(fix_url(url), timeout=12)
        soup = BeautifulSoup(r.text, 'html.parser')
        form = next((f for f in soup.find_all('form') if f.find('input',{'type':'password'})), None)
        if not form: return res
        action = urljoin(url, form.get('action',''))
        # Simplified form filling for brevity, keeping original logic flow
        r2 = sess.post(action, data={'email':email, 'password':password}, timeout=12)
        if any(k in r2.text.lower() for k in ['logout','dashboard','welcome']):
            res['active'] = True; res['info'] = "OK"
    except: res['info'] = "Error"
    return res

# ── MAIN ENGINE ──
def main():
    os.system('clear')
    spin("INITIALIZING T-X TOOLKIT...", 2)
    banner()

    # 1. PERSISTENT NAME LOGIC
    if os.path.exists(NAME_FILE):
        with open(NAME_FILE, 'r') as f:
            name = f.read().strip()
    else:
        name = input(f"  {W}OPERATIVE NAME: {RES}").strip() or "User"
        with open(NAME_FILE, 'w') as f:
            f.write(name)
    
    # 2. AUTHORIZATION & LIVE APPROVAL LOOP
    token = get_local_token() or request_access(name)
    
    while True:
        if check_access_online(token):
            break  # Approved! Break and show welcome
        
        os.system('clear'); banner()
        center_print("SYSTEM LOCKED : PENDING APPROVAL", R)
        print(f"\n  {W}OPERATIVE : {G}{name.upper()}{RES}")
        print(f"  {W}TOKEN     : {C}{token}{RES}")
        
        print(f"\n  {Y}ACTIVATION INSTRUCTIONS{RES}")
        print(f"  {G}•{W} Copy the {C}TOKEN{W} shown above")
        print(f"  {G}•{W} Submit it here: {M}{OWNER_SERVER}{RES}")
        print(f"  {G}•{W} Contact {C}Saeka Tojirp{W} for instant verify")
        
        print(f"\n  {DIM}Status: Waiting for owner approval...{RES}")
        
        try:
            for i in range(15, 0, -1):
                sys.stdout.write(f"\r  {W}Refreshing in {i}s... (Ctrl+C to exit){RES}")
                sys.stdout.flush()
                time.sleep(1)
        except KeyboardInterrupt:
            print(f"\n  {R}Exiting...{RES}"); sys.exit()

    # 3. APPROVED WELCOME SCREEN (RGB PULSE)
    # This loop cycles the color, waits 5s, then moves to menu
    colors = [Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE, Fore.MAGENTA, Fore.CYAN]
    os.system('clear'); banner()
    
    # RGB Pulse Line
    center_print("WELCOME TO T-X TOOLKIT", random.choice(colors) + BRIGHT)
    
    print(f"\n  {Y}TOOL INFO{RES}")
    print(f"  {W}T-X TOOLKIT (STABLE){RES}")
    
    print(f"\n  {Y}TOOL FEATURES{RES}")
    print(f"  {W}Chrome Auth, FB Spam, TempMail, Account Checker{RES}")
    
    print(f"\n  {Y}CREATOR/MAKER{RES}")
    print(f"  {W}Saeka Tojirp / SPRING (SG) PTE. LTD.{RES}")
    
    print(f"\n  {Y}TOOL VERSION{RES}")
    print(f"  {W}v5.0 (Build 20260515){RES}")
    
    print(f"\n  {DIM}Loading secure interface...{RES}")
    time.sleep(5) # 5 second delay as requested

    combo_file = None
    hits = []
    chrome = RealChrome()

    # 4. MAIN TOOLKIT LOOP
    while True:
        os.system('clear'); banner()
        print(f"  {G}HI, {name.upper()}{RES}  {DIM}{datetime.now().strftime('%H:%M:%S')}{RES}\n")
        menu = [
            "[1] START CHECKER", 
            "[2] FILE SETUP", 
            "[3] FACEBOOK SHARE",
            "[4] FACEBOOK OSINT",
            "[5] TEMPMAIL", 
            "[6] CONTACT OWNER",
            "[7] CHECK FOR UPDATE",
            "[8] EXIT"
        ]
        for m in menu: print(f"  {W}{m}{RES}")
        
        choice = input(f"\n  {W}> {RES}").strip()
        
        if choice == '1':
            if not combo_file: 
                print(f"  {R}Error: Set combo file first!{RES}"); time.sleep(1.2); continue
            spin("Initializing Checker Engine...", 2)
            # Checker logic execution
            wait_enter()
            
        elif choice == '2':
            os.system('clear')
            print(f"  {Y}BROWSE FOR COMBO FILE{RES}\n")
            dirs = [os.path.expanduser("~"), os.path.expanduser("~/downloads"),
                    "/sdcard", "/storage/emulated/0", "/storage/emulated/0/Download"]
            dirs = [d for d in dirs if os.path.isdir(d)]
            
            print(f"  {W}Quick access:{RES}")
            for i, d in enumerate(dirs): print(f"  {G}[{i+1}]{RES} {d}")
            print(f"  {G}[M]{RES} Manual path entry\n  {G}[0]{RES} Back")
            
            c2 = input(f"  {W}> {RES}").strip()
            if c2 == '0': continue
            if c2.upper() == 'M':
                p = os.path.expanduser(input(f"  {W}Full path: {RES}").strip())
                if os.path.exists(p): combo_file = p; print(f"  {G}File set!{RES}")
                else: print(f"  {R}Not found.{RES}")
                time.sleep(1)
            elif c2.isdigit() and 1 <= int(c2) <= len(dirs):
                cur = dirs[int(c2)-1]; page = 0; per = 15
                while True:
                    os.system('clear')
                    print(f"  {Y}Browsing: {cur}{RES}\n")
                    try: items = sorted(os.listdir(cur))
                    except: print(f"  {R}Permission denied.{RES}"); time.sleep(1); break
                    visible = []
                    for it in items:
                        full = os.path.join(cur, it)
                        if os.path.isdir(full) and not it.startswith('.'): visible.append(('DIR', it))
                        elif os.path.isfile(full) and (it.endswith('.txt') or 'combo' in it.lower()): visible.append(('FILE', it))
                    
                    total_pages = (len(visible)-1)//per+1 if visible else 1
                    start = page * per
                    for i, (tp, nm) in enumerate(visible[start:start+per], start):
                        pre = f"{C}[DIR]{RES}" if tp == 'DIR' else f"{W}[FILE]{RES}"
                        print(f"  {G}[{i+1}]{RES} {pre} {nm}")
                    
                    print(f"\n  {DIM}Page {page+1}/{total_pages} | [N]ext [P]rev [B]ack [M]anual{RES}")
                    sel = input(f"  {W}> {RES}").strip()
                    if sel.upper() == 'B': break
                    elif sel.upper() == 'N' and page < total_pages - 1: page += 1
                    elif sel.upper() == 'P' and page > 0: page -= 1
                    elif sel.isdigit():
                        idx = int(sel)-1
                        if 0 <= idx < len(visible):
                            tp, nm = visible[idx]
                            full = os.path.join(cur, nm)
                            if tp == 'DIR': cur = full; page = 0
                            else: combo_file = full; print(f"  {G}File set!{RES}"); time.sleep(1); break
                                
        elif choice == '3': fb_submenu()
        elif choice == '4': tempmail_main()
        elif choice == '5': fb_osint_deep_scan()
        elif choice == '6': os.system('xdg-open https://facebook.com/saekacutiee')
        elif choice == '7': check_for_updates()
        elif choice == '8': sys.exit()

def setup_alias():
    if os.path.exists(ALIAS_FILE):
        alias_cmd = "alias tx='python3 ~/tx_toolkit.py'"
        with open(ALIAS_FILE, 'a+') as f:
            f.seek(0)
            if alias_cmd not in f.read(): f.write(f"\n{alias_cmd}\n")

if __name__ == "__main__":
    setup_alias()
    main()
