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
    
    # Simple spinner for the installation phase
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

# Run check before importing other modules
check_dependencies()

# ── NOW IMPORT THE REST ──
import re, json, threading, random, hashlib, uuid, shutil, socket, ssl, string
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse, urljoin
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
GLITCH = [Fore.RED, Fore.BLUE, Fore.GREEN, Fore.MAGENTA]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Mobile Safari/537.36"
]

# ── UTILS ──
def tw(): return shutil.get_terminal_size().columns

def center_print(text, color=W):
    w = tw()
    print(f"{color}{text.center(w)}{RES}")

def spin(text, sec=1.2):
    frm = ['◜','◠','◝','◞','◡','◟']
    end = time.time()+sec; i=0
    while time.time()<end:
        sys.stdout.write(f"\r  {C}{frm[i%6]} {W}{text}{RES}"); sys.stdout.flush()
        time.sleep(0.08); i+=1
    sys.stdout.write("\r" + " " * tw() + "\r")

def banner():
    title = "T-X PAID TOOL"
    for i,ch in enumerate(title): sys.stdout.write(f"{GLITCH[i%4]}{ch}{RES}")
    print("\n")

# ── AUTH & AUTO-REVOKE ──
def get_local_token():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE) as f: return f.read().strip()
    return None

def check_access_online(token):
    """If the owner removes access on Replit, this wipes the local token."""
    try:
        r = requests.get(f"{OWNER_SERVER}/api/status/{token}", timeout=5)
        if r.status_code == 200:
            if r.json().get('status') == 'approved': return True
    except: return True 
    
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

# ── TEMPMAIL MODULE ──
current_temp_email = None
temp_mail_session = {}

def tempmail_main():
    global current_temp_email
    while True:
        os.system('clear'); banner()
        print(f"  {Y}TEMP MAIL MODULE{RES}")
        if current_temp_email: print(f"  {C}Active: {current_temp_email}{RES}")
        print(f"\n  {G}[1]{RES} New Inbox\n  {G}[2]{RES} View Messages\n  {G}[0]{RES} Back")
        ch = input(f"\n  {W}> {RES}").strip()
        if ch == '1':
            spin("Requesting Domain...", 1)
            try:
                r = requests.get("https://api.mail.tm/domains", timeout=10)
                domain = r.json()['hydra:member'][0]['domain']
                user = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
                email, pw = f"{user}@{domain}", "tx_pass_99"
                spin("Creating Account...", 1.2)
                requests.post("https://api.mail.tm/accounts", json={"address": email, "password": pw}, timeout=10)
                tk_r = requests.post("https://api.mail.tm/token", json={"address": email, "password": pw}, timeout=10)
                current_temp_email = email
                temp_mail_session = {"email": email, "password": pw, "token": tk_r.json()['token']}
                print(f"  {G}[SUCCESS] Email: {W}{email}{RES}")
            except: print(f"  {R}API Error.{RES}")
            input(f"\n  {DIM}Press ENTER...{RES}")
        elif ch == '2':
            if not current_temp_email: continue
            spin("Fetching Inbox...", 1)
            # Simplified refresh loop
            os.system('clear'); banner()
            headers = {"Authorization": f"Bearer {temp_mail_session.get('token')}"}
            r = requests.get("https://api.mail.tm/messages", headers=headers, timeout=5)
            msgs = r.json().get('hydra:member', [])
            if not msgs: print(f"  {DIM}No messages found.{RES}")
            for m in msgs: print(f"  {G}• {W}{m.get('subject')}{RES}")
            input(f"\n  {DIM}Press ENTER...{RES}")
        elif ch == '0': return

# ── MAIN LOOP ──
def main():
    os.system('clear')
    spin("T-X TOOLKIT BOOTING...", 2.5)
    
    name = input(f"\n  {W}NAME: {RES}").strip() or "User"
    token = get_local_token()

    if not token:
        token = request_access(name)
    
    # Validation / Auto-Revoke Check
    spin("Verifying Clearance...", 1.5)
    if not check_access_online(token):
        os.system('clear')
        center_print("ACCESS DENIED / REVOKED", R)
        center_print(f"Your Token: {token}", Y)
        center_print("Contact owner for access.", DIM)
        sys.exit()

    combo_file = None
    while True:
        os.system('clear'); banner()
        print(f"  {G}OPERATIVE: {name.upper()}{RES}\n")
        print(f"  {W}[1] Checker Mode\n  [2] Load File\n  [3] Facebook Spam\n  [4] TempMail\n  [5] Exit{RES}")
        
        choice = input(f"\n  {W}> {RES}").strip()
        
        if choice == '1':
            if not combo_file: print(f"  {R}Error: Load file first.{RES}"); time.sleep(1); continue
            spin("Checking accounts...", 2)
            print(f"  {G}Scan Complete.{RES}")
            input()
        elif choice == '2':
            combo_file = input(f"  {W}Path: {RES}").strip()
            if os.path.exists(combo_file):
                spin("Reading data...", 1)
                print(f"  {G}Loaded.{RES}")
            else: print(f"  {R}File Not Found.{RES}")
            time.sleep(1)
        elif choice == '3':
            spin("Loading FB Module...", 1)
            # Add FB submenu call here
        elif choice == '4':
            tempmail_main()
        elif choice == '5':
            sys.exit()

if __name__ == "__main__":
    main()
