import requests
import socket
import time
import os
from urllib.parse import urlparse, parse_qs

# ANSI Color UI Elements
G, Y, R, C, M, B, W = '\033[92m', '\033[93m', '\033[91m', '\033[96m', '\033[95m', '\033[1m', '\033[0m'
F_TXT = "voucher_history.txt"

# 🌟 ဤနေရာတွင် သင်၏ Ruijie Portal URL အမှန်ကို တိုက်ရိုက်ပြောင်းလဲထည့်သွင်းပါ
init_url = (
    "https://portal-as.ruijienetworks.com/api/auth/wifidog"
    "?stage=portal&gw_id=c470ab7ea1d5&gw_sn=G1T044R00200B"
    "&gw_address=10.0.0.1&gw_port=2060&ip=10.0.0.3"
    "&mac=d8:ce:3a:dd:cd:1f&slot_num=06&nasip=192.168.1.143"
    "&ssid=VLAN233&ustate=06&mac_req=06"
    "&url=https%3A%2F%2Fipv4.icanhazip.com%2F"
    "&chap_id=%5C001&chap_challenge=%5C266%5C374%5C244%5C125%5C301%5C242%5C364%5C354%5C075%5C375%5C217%5C175%5C314%5C151%5C151%5C301"
)

def print_banner():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{C}{B}┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓{W}")
    print(f"{C}{B}┃      🌟 RUIJIE CAPTIVE PORTAL AUTO-BYPASS TOOL 🌟     ┃{W}")
    print(f"{C}{B}┃             ⚡ WiFiDog Protocol Powered ⚡             ┃{W}")
    print(f"{C}{B}┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛{W}")

def get_gw():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0].split('.')
        ip[-1] = '1'
        return '.'.join(ip)
    except: 
        return "192.168.60.1"

print_banner()
gw = get_gw()
print(f"{G}[+] စနစ်မှ ဖမ်းယူရရှိသည့် Wi-Fi Gateway IP: {B}{gw}{W}")

ss = requests.Session()
ss.headers.update({'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36', 'Connection': 'keep-alive'})

# ---------------------------------------------------------------------
# အဆင့် (၁) - Session ID ဖမ်းခြင်း
# ---------------------------------------------------------------------
print(f"\n{Y}[*] အဆင့် (၁): Redirect URL ထဲမှ Session Data များ စစ်ဆေးနေသည်...{W}")
try:
    resp = ss.get(init_url, allow_redirects=False, timeout=5)
    redirect_url = resp.headers.get('Location', resp.url)
    sid = parse_qs(urlparse(redirect_url).query).get('sessionId', [None])[0]
    
    if not sid:
        with ss.get(init_url, allow_redirects=True, stream=True, timeout=5) as r:
            sid = parse_qs(urlparse(r.url).query).get('sessionId', [None])[0]

    if not sid:
        raise ValueError("Session ID ကို Link ထဲမှ ရှာမတွေ့ပါ။")
        
    print(f"{G} ├── {B}Session ID:{W} {C}{sid}{W}")
    
except Exception as e:
    print(f"{R}[!] Connection Error (Default Token Used): {e}{W}")
    sid = '13ed4bb1e881482bab3de3a80514016a'

# ---------------------------------------------------------------------
# အဆင့် (၂) - Voucher Loop System
# ---------------------------------------------------------------------
cookies_step2 = {'sensorsdata2015jssdkcross': '%7B%22distinct_id%22%3A%22267794%22%7D'}
headers_step2 = {'content-type': 'application/json', 'referer': f'https://portal-as.ruijienetworks.com/download/static/maccauth/src/index.html?sessionId={sid}'}

old_v = open(F_TXT, "r").read().strip() if os.path.exists(F_TXT) else None

while True:
    print(f"\n{M}┏━━━━━━━ [ AUTHENTICATION CARD ] ━━━━━━━┓{W}")
    if old_v:
        v_in = input(f"{M}┃{Y} [❓] Voucher Code -> {W}(အဟောင်း [{G}{old_v}{W}] ကိုသုံးရန် Enter ခေါက်ပါ): ").strip() or old_v
    else:
        v_in = input(f"{M}┃{Y} [❓] Voucher Code ကို ထည့်သွင်းပါ -> {W}").strip()
        if not v_in: continue
    print(f"{M}┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛{W}")

    print(f"\n{Y}[*] အဆင့် (၂): Ruijie Cloud သို့ Voucher တင်သွင်းစစ်ဆေးနေသည်...{W}")
    data = {'accessCode': v_in, 'sessionId': sid, 'apiVersion': 1}
    
    try:
        res = ss.post('https://portal-as.ruijienetworks.com/api/auth/voucher/?lang=en_US', cookies=cookies_step2, headers=headers_step2, json=data, timeout=5).json()
        
        if res.get("success") is True:
            print(f"{G}[🎉] အောင်မြင်သည်: Voucher Code အမှန်ကန်ဖြစ်ပါသည်။{W}")
            open(F_TXT, "w").write(v_in)
            
            p_parsed = parse_qs(urlparse(res["result"]["logonUrl"]).query)
            token_val = p_parsed.get('token', [sid])[0]
            phone_val = p_parsed.get('phoneNumber', [v_in])[0]
            break
        else:
            print(f"{R}[❌] Voucher ကုဒ် မှားယွင်းနေသည် သို့မဟုတ် Session သက်တမ်းကုန်ဆုံးသွားပါပြီ။{W}")
            if old_v == v_in and os.path.exists(F_TXT): os.remove(F_TXT); old_v = None
    except Exception as e:
        print(f"{R}[!] Network Request Error: {e}{W}")

# ---------------------------------------------------------------------
# အဆင့် (၃ & ၄) - Local Router Auth နှင့် Live Heartbeat Dashboard
# ---------------------------------------------------------------------
print(f"\n{Y}[*] အဆင့် (၃): Local Router Gateway များဆီသို့ လိုင်းဖွင့်ရန် တောင်းဆိုနေသည်...{W}")

TARGET_IP_2 = "10.44.77.250"
r_url_1 = f"http://{gw}:2060/wifidog/auth"
r_url_2 = f"http://{TARGET_IP_2}:2060/wifidog/auth"

params = {'token': token_val, 'phoneNumber': phone_val}

try:
    print(f"{Y} ├── Target 1 ({gw}) သို့ ချိတ်ဆက်နေသည်...{W}")
    try:
        router_res1 = ss.get(r_url_1, params=params, headers={'Upgrade-Insecure-Requests': '1'}, timeout=5)
        success_1 = (router_res1.status_code == 200 and ("Auth: 1" in router_res1.text or "<html" in router_res1.text.lower()))
    except Exception as e:
        print(f"{R} [!] Target 1 သို့ ချိတ်ဆက်မှု မအောင်မြင်ပါ- {e}{W}")
        success_1 = False
        
    print(f"{Y} ├── Target 2 ({TARGET_IP_2}) သို့ ချိတ်ဆက်နေသည်...{W}")
    try:
        router_res2 = ss.get(r_url_2, params=params, headers={'Upgrade-Insecure-Requests': '1'}, timeout=5)
        success_2 = (router_res2.status_code == 200 and ("Auth: 1" in router_res2.text or "<html" in router_res2.text.lower()))
    except Exception as e:
        print(f"{R} [!] Target 2 သို့ ချိတ်ဆက်မှု မအောင်မြင်ပါ- {e}{W}")
        success_2 = False

    if success_1 or success_2:
        print(f"\n{G}{B}┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓{W}")
        print(f"{G}{B}┃               🚀 BYPASS SUCCESSFUL !! 🚀               ┃{W}")
        print(f"{G}{B}┃         ဝိုင်ဖိုင် Firewall အား ကျော်ဖြတ်ပြီးပါပြီ        ┃{W}")
        print(f"{G}{B}┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛{W}")
        
        print(f"\n{C}{B}┌─────────────────── [ LIVE MONITOR ] ───────────────────┐{W}")
        print(f"{C}{B}│ {Y}GW 1:{W} {gw:<15} │ {Y}GW 2:{W} {TARGET_IP_2:<14} │{W}")
        print(f"{C}{B}└────────────────────────────────────────────────────────┘{W}")
        
        ping_count = 1
        status_color = G
        status_text = "CONNECTED"
        
        while True:
            for remaining in range(30, 0, -1):
                current_time = time.strftime('%H:%M:%S')
                print(f"\r{C} [{current_time}] {status_color}● {status_text}{W} | {B}Count:{W} {ping_count:<3} | {Y}Next Ping in: {remaining:02d}s{W} ", end="", flush=True)
                time.sleep(1)
            
            print(f"\r{C} [{time.strftime('%H:%M:%S')}] {Y}🔄 PINGING BOTH ROUTER GATEWAYS...               {W}", end="", flush=True)
            
            status_1 = False
            status_2 = False
            
            try:
                if ss.get(r_url_1, params=params, timeout=4).status_code == 200:
                    status_1 = True
            except: pass
            
            try:
                if ss.get(r_url_2, params=params, timeout=4).status_code == 200:
                    status_2 = True
            except: pass
            
            if status_1 and status_2:
                status_color = G
                status_text = "BOTH ACTIVE "
            elif status_1 or status_2:
                status_color = Y
                status_text = "1 LINE ACTIVE"
            else:
                status_color = R
                status_text = "LINE DROPPED"
                
            ping_count += 1
    else:
        print(f"{R}[!] Router နှစ်ခုစလုံးဆီမှ တုံ့ပြန်မှု မရရှိပါ။ လိုင်းဖွင့်ခြင်း မအောင်မြင်ပါ။{W}")
            
except KeyboardInterrupt:
    print(f"\n\n{R}[-] Heartbeat Loop အား အသုံးပြုသူမှ ရပ်တန့်လိုက်ပါပြီ။{W}\n")
except Exception as e:
    print(f"{R}[!] Router Error: {e}{W}")
