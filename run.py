import requests
import socket
import time
import os
from urllib.parse import urlparse, parse_qs

# ANSI Color UI Elements
G, Y, R, C, M, B, W = '\033[92m', '\033[93m', '\033[91m', '\033[96m', '\033[95m', '\033[1m', '\033[0m'
F_TXT = "voucher_history.txt"

# 🌟 သင်၏ Ruijie Portal URL အမှန်ကို ဤနေရာတွင် ထည့်သွင်းပါ
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

# ---------------------------------------------------------------------
# အဓိက အလုပ်လုပ်မည့် Function (လိုင်းကျလျှင် ပြန်ခေါ်မည်)
# ---------------------------------------------------------------------
def run_authentication_flow(ss, is_reauth=False):
    global init_url, F_TXT, gw
    
    # ---------------------------------------------------------------------
    # အဆင့် (၁) - Session ID ဖမ်းခြင်း
    # ---------------------------------------------------------------------
    if is_reauth:
        print(f"\n{R}[!] လိုင်းပြတ်သွားသဖြင့် Session သက်တမ်းတိုးရန် ပြန်လည်ကြိုးစားနေသည်...{W}")
    else:
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
    # အဆင့် (၂) - Voucher System (Auto-pilot if file exists)
    # ---------------------------------------------------------------------
    cookies_step2 = {'sensorsdata2015jssdkcross': '%7B%22distinct_id%22%3A%22267794%22%7D'}
    headers_step2 = {
        'content-type': 'application/json', 
        'referer': f'https://portal-as.ruijienetworks.com/download/static/maccauth/src/index.html?sessionId={sid}',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36'
    }

    old_v = open(F_TXT, "r").read().strip() if os.path.exists(F_TXT) else None

    while True:
        # Re-auth ဖြစ်ပါက Voucher အလိုအလျောက် ယူမည်၊ Input ထပ်မတောင်းပါ
        if is_reauth and old_v:
            v_in = old_v
            print(f"{G}[+] သိမ်းဆည်းထားသော Voucher Code [{v_in}] ဖြင့် အလိုအလျောက် သက်တမ်းတိုးနေသည်...{W}")
        else:
            print(f"\n{M}┏━━━━━━━ [ AUTHENTICATION CARD ] ━━━━━━━┓{W}")
            if old_v:
                v_in = input(f"{M}┃{Y} [❓] Voucher Code -> {W}(အဟောင်း [{G}{old_v}{W}] ကိုသုံးရန် Enter ခေါက်ပါ): ").strip() or old_v
            else:
                v_in = input(f"{M}┃{Y} [❓] Voucher Code ကို ထည့်သွင်းပါ -> {W}").strip()
                if not v_in: continue
            print(f"{M}┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛{W}")

        print(f"{Y}[*] အဆင့် (၂): Ruijie Cloud သို့ Voucher တင်သွင်းစစ်ဆေးနေသည်...{W}")
        data = {'accessCode': v_in, 'sessionId': sid, 'apiVersion': 1}
        
        try:
            res = ss.post('https://portal-as.ruijienetworks.com/api/auth/voucher/?lang=en_US', cookies=cookies_step2, headers=headers_step2, json=data, timeout=5).json()
            
            if res.get("success") is True:
                print(f"{G}[🎉] အောင်မြင်သည်: Voucher Cloud Session အသစ် ရရှိပါပြီ။{W}")
                open(F_TXT, "w").write(v_in)
                
                p_parsed = parse_qs(urlparse(res["result"]["logonUrl"]).query)
                token_val = p_parsed.get('token', [sid])[0]
                phone_val = p_parsed.get('phoneNumber', [v_in])[0]
                return token_val, phone_val
            else:
                print(f"{R}[❌] Voucher ကုဒ် မှားယွင်းနေသည် သို့မဟုတ် Cloud Session သက်တမ်းကုန်ဆုံးသွားပါပြီ။{W}")
                if is_reauth:
                    # Re-auth ကနေ မှားသွားရင် User ဆီက Input ပြန်တောင်းဖို့ Flow ကို ပြောင်းမယ်
                    is_reauth = False 
                if old_v == v_in and os.path.exists(F_TXT): 
                    os.remove(F_TXT)
                    old_v = None
        except Exception as e:
            print(f"{R}[!] Network Request Error: {e}{W}")
            if is_reauth:
                time.sleep(3) # ကွန်ရက်ခဏပြတ်သွားလျှင် ၃ စက္ကန့် စောင့်ပြီး ပြန်ကြိုးစားရန်
            else:
                return None, None

# ---------------------------------------------------------------------
# ပရိုဂရမ် စတင်လည်ပတ်ရာနေရာ (Main Execution)
# ---------------------------------------------------------------------
print_banner()
gw = get_gw()
print(f"{G}[+] စနစ်မှ ဖမ်းယူရရှိသည့် Wi-Fi Gateway IP: {B}{gw}{W}")

ss = requests.Session()
ss.headers.update({'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36', 'Connection': 'keep-alive'})

# ပထမအကြိမ် Auth Token ယူခြင်း
token_val, phone_val = run_authentication_flow(ss, is_reauth=False)

if token_val and phone_val:
    TARGET_IP_2 = "10.44.77.250"
    r_url_1 = f"http://{gw}:2060/wifidog/auth"
    r_url_2 = f"http://{TARGET_IP_2}:2060/wifidog/auth"
    
    ping_count = 1
    status_color = G
    status_text = "CONNECTED"
    
    print(f"\n{C}{B}┌─────────────────── [ LIVE MONITOR ] ───────────────────┐{W}")
    print(f"{C}{B}│ {Y}GW 1:{W} {gw:<15} │ {Y}GW 2:{W} {TARGET_IP_2:<14} │{W}")
    print(f"{C}{B}└────────────────────────────────────────────────────────┘{W}")

    try:
        while True:
            # အဆင့် (၃) - Local Router Gateway များဆီသို့ လိုင်းဖွင့်ရန် တောင်းဆိုခြင်း
            params = {'token': token_val, 'phoneNumber': phone_val}
            
            status_1 = False
            status_2 = False
            
            # Session မပြတ်တောက်စေရန် Keep-Alive Header ဖြင့် အမြဲတမ်း Ping မည်
            ping_headers = {
                'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36',
                'Upgrade-Insecure-Requests': '1',
                'Connection': 'keep-alive'
            }
            
            try:
                r1 = ss.get(r_url_1, params=params, headers=ping_headers, timeout=4)
                if r1.status_code == 200 and ("Auth: 1" in r1.text or "<html" in r1.text.lower()):
                    status_1 = True
            except: pass
            
            try:
                r2 = ss.get(r_url_2, params=params, headers=ping_headers, timeout=4)
                if r2.status_code == 200 and ("Auth: 1" in r2.text or "<html" in r2.text.lower()):
                    status_2 = True
            except: pass
            
            # အခြေအနေပေါ်မူတည်ပြီး ကာလာပြောင်းလဲခြင်း
            if status_1 and status_2:
                status_color = G
                status_text = "BOTH ACTIVE "
            elif status_1 or status_2:
                status_color = Y
                status_text = "1 LINE ACTIVE"
            else:
                status_color = R
                status_text = "LINE DROPPED"
                print(f"\n{R}[!] Token သက်တမ်းကုန်သွားခြင်း သို့မဟုတ် Gateway လိုင်းပြတ်တောက်သွားသည်။{W}")
                
                # 🔄 ဤနေရာတွင် အဓိက ပြင်ဆင်ချက်ဖြစ်သော Auto Re-auth ကို လုပ်ဆောင်ပါသည်
                token_val, phone_val = run_authentication_flow(ss, is_reauth=True)
                if not token_val:
                    # အကြောင်းအမျိုးမျိုးကြောင့် Re-auth မအောင်မြင်ပါက ၅ စက္ကန့်နားပြီး အစကနေ ပြန်ပတ်မည်
                    time.sleep(5)
                continue

            ping_count += 1
            
            # ၃၀ စက္ကန့် Heartbeat Countdown ပတ်လမ်း
            for remaining in range(30, 0, -1):
                current_time = time.strftime('%H:%M:%S')
                print(f"\r{C} [{current_time}] {status_color}● {status_text}{W} | {B}Count:{W} {ping_count:<3} | {Y}Next Ping in: {remaining:02d}s{W} ", end="", flush=True)
                time.sleep(1)
                
            print(f"\r{C} [{time.strftime('%H:%M:%S')}] {Y}🔄 PINGING BOTH ROUTER GATEWAYS...               {W}", end="", flush=True)

    except KeyboardInterrupt:
        print(f"\n\n{R}[-] Heartbeat Loop အား အသုံးပြုသူမှ ရပ်တန့်လိုက်ပါပြီ။{W}\n")
    except Exception as e:
        print(f"{R}[!] Router Error: {e}{W}")
else:
    print(f"{R}[!] ပထမအကြိမ် ကနဦးချိတ်ဆက်မှု မအောင်မြင်ပါ။ သင့် URL သို့မဟုတ် ကွန်ရက် ချိတ်ဆက်မှုကို စစ်ဆေးပါ။{W}")
