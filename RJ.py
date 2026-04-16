import speech_recognition as sr
import pyttsx3
import datetime
import wikipedia
import webbrowser
import os
import requests
import json
import random
import threading
import time
import math
import logging
import smtplib
import psutil
import pyautogui
import winreg
import keyboard
import asyncio
import edge_tts
import pygame
import urllib.parse
import ctypes
import tkinter as tk
from tkinter import font as tkfont
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from PIL import ImageGrab
from vosk import Model, KaldiRecognizer

os.environ["VOSK_LOG_LEVEL"] = "-1"
logging.getLogger("vosk").setLevel(logging.ERROR)

# ── KEYS & PATHS ──
WEATHER_API_KEY = "c05f1f9e7f6547c8b923554133c1d3e6"
GROQ_API_KEY    = "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"
NEWS_API_KEY    = "74534ddba243474686bed0c5aa7a1930"
EMAIL_ID        = "shivassistant@gmail.com"
EMAIL_PASS      = "bsmq diaq fcza mwny"
MODEL_PATH      = r"D:\python_projects\vosk-model-small-en-us-0.15\vosk-model-small-en-us-0.15"
MEMORY_FILE     = r"D:\python_projects\rj_memory.json"
CONTACTS_FILE   = r"D:\python_projects\rj_contacts.json"
SCREENSHOT_DIR  = r"D:\python_projects\screenshots"
VOICE_FILE      = r"D:\python_projects\rj_voice.mp3"

# ── YOUNG FEMALE VOICES ──
VOICE_EN = "en-US-AnaNeural"       # Young female English (youngest sounding)
VOICE_HI = "hi-IN-SwaraNeural"    # Young female Hindi

# ══════════════════════════════════════════════════
# HEART SYSTEM
# H - Human-like Interaction
# E - Emotional Intelligence
# A - Adaptive Behavior
# R - Real-time Response
# T - Thoughtful Execution
# ══════════════════════════════════════════════════

# ── E: Emotional Intelligence - Mood Detection ──
user_emotion = ["neutral"]  # happy, sad, angry, neutral, tired, excited

def detect_emotion(query):
    """Detect user's emotional state from their words"""
    q = query.lower()
    if any(w in q for w in ["bahut achha","amazing","zabardast","awesome","great","wah","mast","khush","happy","excited","yay"]):
        user_emotion[0] = "happy"
    elif any(w in q for w in ["bura lag raha","sad","dukhi","tension","pareshan","upset","disappointed","bore"]):
        user_emotion[0] = "sad"
    elif any(w in q for w in ["gussa","angry","irritating","bakwaas","bekar","stupid","useless","kuch nahi kar sakti"]):
        user_emotion[0] = "angry"
    elif any(w in q for w in ["neend","thaka","tired","so raha","uth nahi","bore","pagal"]):
        user_emotion[0] = "tired"
    elif any(w in q for w in ["kal","meeting","kaam","project","jaldi","deadline","urgent"]):
        user_emotion[0] = "busy"

def empathetic_response():
    """E: Respond based on detected user emotion"""
    if user_emotion[0] == "sad":
        return random.choice(["Koi baat nahi Boss, sab theek ho jaayega!","Arey mat ghabrao boss, main hoon na!","Chill karo Boss, sab set ho jaayega!"])
    elif user_emotion[0] == "angry":
        return random.choice(["Sorry Boss, main samajh rahi hoon!","Shant ho jao Boss, bata do kya hua!","Ok ok Boss, main fix karti hoon!"])
    elif user_emotion[0] == "tired":
        return random.choice(["Aram karo Boss, main kaam sambhal leti hoon!","Thodi chai pi lo Boss!","Aap rest karo, main hoon na!"])
    elif user_emotion[0] == "happy":
        return random.choice(["Wah Boss mast mood hai aaj!","Bahut achha Boss!","Ekdum mast!"])
    return None

# ── A: Adaptive Behavior - Learning preferences ──
interaction_count = [0]
user_preferences  = {
    "prefers_short": False,
    "common_commands": {},
    "last_topics": []
}

def track_command(cmd):
    """A: Track what user asks most"""
    user_preferences["common_commands"][cmd] = user_preferences["common_commands"].get(cmd,0) + 1
    interaction_count[0] += 1

def get_adaptive_greeting():
    """A: Greet based on usage patterns"""
    top = sorted(user_preferences["common_commands"].items(), key=lambda x: x[1], reverse=True)
    if top:
        cmd = top[0][0]
        return f"Waise Boss, aap aksar {cmd} maangte ho, kya aaj bhi wahi chahiye?"
    return None

# ── H: Human-like Interaction ──
CASUAL_RESPONSES_HI = {
    "theek hai": ["Haan haan!", "Bilkul!", "Done Boss!"],
    "ok": ["Ji Boss!", "Theek hai!"],
    "haan": ["Bolo Boss!", "Haan ji?"],
    "nahi": ["Accha theek hai Boss!", "Ok ok!"],
    "thanks": ["Arey Boss isme kya thanks!", "Koi baat nahi Boss!", "Ye toh mera kaam hai!"],
    "shukriya": ["Arey Boss isme kya shukriya!", "Apna kaam toh karna hi tha!"],
    "good morning": ["Good morning Boss! Kaise hain aap?","Morning morning! Chai pi li?"],
    "good night": ["Good night Boss! Sweet dreams!","Aram karo Boss, kal phir milenge!"],
    "hello": ["Hello Boss! Kya haal hai?","Haan Boss bolo!","Arrey Boss aa gaye!"],
    "hi": ["Hi Boss! Kya chal raha hai?","Hi hi! Bolo Boss!"],
    "bye": ["Bye Boss! Take care!","Chalo bye! Kuch kaam ho toh bulana!"],
}

SMALL_TALK_HI = [
    "Aaj ka din kaisa ja raha hai Boss?",
    "Kuch interesting chal raha hai kya life mein?",
    "Waise Boss aaj kuch naya seekha?",
    "Achha Boss, aap bahut hardworking ho!",
]

def check_casual(query):
    """H: Handle casual human-like conversations"""
    q = query.lower().strip()
    for key, responses in CASUAL_RESPONSES_HI.items():
        if key in q and len(q) < 20:
            return random.choice(responses)
    return None

# ── MOOD SYSTEM ──
current_mood = ["happy"]

def get_mood_ack():
    hi = ["Theek hai Boss!", "Ji bilkul!", "Abhi karti hoon!",
          "Ho jaayega!", "Sure Boss!", "Haan haan!", "Done Boss!",
          "Abhi kiya!", "Chill Boss, main hoon!"]
    en = ["Sure thing Boss!", "On it!", "Right away!", "Got it Boss!",
          "Done Boss!", "Consider it done!"]
    return random.choice(hi if current_lang[0]=="hi" else en)

def set_mood(mood):
    current_mood[0] = mood
    memory["preferences"]["mood"] = mood
    save_memory(memory)
    speak("Happy mode on Boss! Chal party karte hain!" if mood=="happy" else "Serious mode on Boss.")

# ── MEMORY ──
def load_memory():
    try:
        if os.path.exists(MEMORY_FILE):
            with open(MEMORY_FILE,"r") as f: return json.load(f)
    except: pass
    return {"name":"Shiva","preferences":{},"notes":[],"last_seen":"","lang":"hi"}

def save_memory(m):
    try:
        with open(MEMORY_FILE,"w") as f: json.dump(m,f,indent=2)
    except: pass

memory = load_memory()
memory["last_seen"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
save_memory(memory)
current_lang = [memory.get("lang","hi")]
current_mood[0] = memory.get("preferences",{}).get("mood","happy")

def load_contacts():
    try:
        if os.path.exists(CONTACTS_FILE):
            with open(CONTACTS_FILE,"r") as f: return json.load(f)
    except: pass
    return {}

contacts = load_contacts()

print("Loading voice model...")
vosk_model = Model(MODEL_PATH)
print("Model loaded!")

def setup_auto_startup():
    try:
        script_path = os.path.abspath(__file__)
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r"Software\Microsoft\Windows\CurrentVersion\Run",
                             0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key,"RJ_Assistant",0,winreg.REG_SZ,f'pythonw "{script_path}"')
        winreg.CloseKey(key)
        print("Auto startup enabled!")
    except Exception as e: print(f"Startup error: {e}")

setup_auto_startup()

BG="#000810"; CYAN="#00E5FF"; CYAN2="#00BFFF"; CYAN3="#0077AA"
GOLD="#FFB300"; WHITE="#E8F8FF"; DIM="#0A2030"; TDIM="#2A6A8A"

root = tk.Tk()
root.title("RJ")
root.overrideredirect(True)
root.attributes("-topmost",True)
root.attributes("-transparentcolor",BG)
root.configure(bg=BG)

W,H = 300,300
sw=root.winfo_screenwidth(); sh=root.winfo_screenheight()
root.geometry(f"{W}x{H}+{sw-W-10}+{sh-H-50}")

try:
    FONT_TINY  = tkfont.Font(family="Segoe UI",size=7)
    FONT_TITLE = tkfont.Font(family="Segoe UI",size=12,weight="bold")
    FONT_BTN   = tkfont.Font(family="Segoe UI",size=7,weight="bold")
    FONT_LANG  = tkfont.Font(family="Segoe UI",size=7,weight="bold")
except:
    FONT_TINY=tkfont.Font(size=7); FONT_TITLE=tkfont.Font(size=12,weight="bold")
    FONT_BTN=tkfont.Font(size=7,weight="bold"); FONT_LANG=tkfont.Font(size=7,weight="bold")

_drag={"x":0,"y":0}
def on_ds(e): _drag["x"]=e.x; _drag["y"]=e.y
def on_d(e): root.geometry(f"+{root.winfo_x()+e.x-_drag['x']}+{root.winfo_y()+e.y-_drag['y']}")
root.bind("<ButtonPress-1>",on_ds); root.bind("<B1-Motion>",on_d)

cx,cy=W//2,H//2
hud=tk.Canvas(root,width=W,height=H,bg=BG,highlightthickness=0)
hud.pack()
phase=[0.0]; pulse=[0.0]; state=["idle"]; anim_on=[True]

def draw_hud():
    if not anim_on[0]: return
    hud.delete("all")
    ph=phase[0]; pu=pulse[0]; st=state[0]
    TR=138
    for i in range(120):
        a=math.radians(i*3)
        if i%10==0: r1,r2,w,col=TR-7,TR,2,CYAN2
        elif i%5==0: r1,r2,w,col=TR-4,TR,1,CYAN3
        else: r1,r2,w,col=TR-2,TR,1,DIM
        hud.create_line(cx+r1*math.cos(a),cy+r1*math.sin(a),cx+r2*math.cos(a),cy+r2*math.sin(a),fill=col,width=w)
    hud.create_oval(cx-128,cy-128,cx+128,cy+128,outline=CYAN3,width=1)
    R1=118; rot1=(ph*22)%360
    for ext,col,w in [(65,CYAN,3),(18,BG,0),(48,CYAN2,2),(28,BG,0),(85,CYAN,3),(12,BG,0),(104,CYAN3,2)]:
        if w: hud.create_arc(cx-R1,cy-R1,cx+R1,cy+R1,start=rot1,extent=ext,outline=col,width=w,style="arc")
        rot1+=ext
    R2=106; rot2=-(ph*16)%360
    for ext,col,w in [(38,GOLD,3),(14,BG,0),(22,GOLD,2),(88,BG,0),(28,GOLD,3),(170,BG,0)]:
        if w: hud.create_arc(cx-R2,cy-R2,cx+R2,cy+R2,start=rot2,extent=ext,outline=col,width=w,style="arc")
        rot2+=ext
    hud.create_oval(cx-94,cy-94,cx+94,cy+94,outline=CYAN3,width=1,dash=(4,6))
    R4=86; rot3=(ph*48)%360
    for ext,col,w in [(18,CYAN,2),(55,BG,0),(12,CYAN2,2),(95,BG,0),(22,CYAN,2),(158,BG,0)]:
        if w: hud.create_arc(cx-R4,cy-R4,cx+R4,cy+R4,start=rot3,extent=ext,outline=col,width=w,style="arc")
        rot3+=ext
    if st=="speaking":
        for i in range(5):
            pr=68+i*6+math.sin(pu*3+i*0.7)*6; t=max(0,1-i*0.2)*(0.6+0.4*math.sin(pu*4)); v=min(255,int(80+t*175))
            hud.create_oval(cx-pr,cy-pr,cx+pr,cy+pr,outline=f"#00{v:02X}{v:02X}",width=max(1,3-i//2))
    elif st=="listening":
        for i in range(4):
            pr=65+i*5+math.sin(pu*2+i*0.9)*4; t=max(0,1-i*0.25)*(0.5+0.5*math.sin(pu*2.5))*0.7; v=min(255,int(80+t*175))
            hud.create_oval(cx-pr,cy-pr,cx+pr,cy+pr,outline=f"#00{v:02X}{v:02X}",width=max(1,2-i//2))
    else:
        pr=62+math.sin(pu*0.8)*3
        hud.create_oval(cx-pr,cy-pr,cx+pr,cy+pr,outline=CYAN3,width=1)
    for i in range(4):
        gr=54+i*4; t=(0.3-i*0.07)*(1+0.3*math.sin(pu*2)); v=min(255,int(80+t*175))
        hud.create_oval(cx-gr,cy-gr,cx+gr,cy+gr,outline=f"#00{v:02X}{v:02X}",width=1)
    hud.create_oval(cx-48,cy-48,cx+48,cy+48,fill="#020D1A",outline=CYAN,width=2)
    sr2=16+math.sin(pu*2)*3
    spot="#00EEFF" if st=="speaking" else ("#00FFCC" if st=="listening" else "#004466")
    hud.create_oval(cx-sr2,cy-sr2,cx+sr2,cy+sr2,fill=spot,outline="")
    mr=7+math.sin(pu*3)*2
    hud.create_oval(cx-mr,cy-mr,cx+mr,cy+mr,fill=WHITE,outline="")
    hud.create_text(cx,cy-8,text="RJ",fill=WHITE,font=FONT_TITLE)
    if st=="speaking": sub,sc="SPEAKING",CYAN
    elif st=="listening": sub,sc="LISTENING","#00FFCC"
    else: sub,sc="READY",TDIM
    hud.create_text(cx,cy+9,text=sub,fill=sc,font=FONT_TINY)
    hud.create_text(cx,cy+20,text=datetime.datetime.now().strftime("%H:%M:%S"),fill=TDIM,font=FONT_TINY)
    hud.create_text(cx,cy+31,text=status_var.get(),fill=TDIM,font=FONT_TINY)
    mood_col=GOLD if current_mood[0]=="happy" else CYAN
    hud.create_text(12,10,text="😄" if current_mood[0]=="happy" else "🎯",fill=mood_col,font=FONT_TINY)
    lang_col=GOLD if current_lang[0]=="hi" else CYAN3
    hud.create_text(W-12,H-16,text="HI" if current_lang[0]=="hi" else "EN",fill=lang_col,font=FONT_LANG)
    hud.create_text(W-8,8,text="✕",fill=TDIM,font=FONT_BTN)
    hud.create_rectangle(cx-36,H-24,cx+36,H-7,outline=CYAN,fill=DIM,width=1)
    hud.create_text(cx,H-15,text="⏹ STOP",fill=CYAN,font=FONT_BTN)
    wk_col=CYAN if wake_var.get() else TDIM
    hud.create_text(14,H-15,text="RJ",fill=wk_col,font=FONT_TINY)
    phase[0]+=0.018; pulse[0]+=0.07
    root.after(33,draw_hud)

def on_click(e):
    if W-18<e.x<W-2 and 2<e.y<18: anim_on[0]=False; root.destroy(); return
    if cx-36<e.x<cx+36 and H-26<e.y<H-5: stop_assistant(); return
    if 2<e.x<28 and H-24<e.y<H-6: toggle_wake(); return

hud.bind("<Button-1>",on_click)
status_var=tk.StringVar(value="STARTING...")
wake_var=tk.BooleanVar(value=False)
is_running=[True]

def set_state(s): state[0]=s
def set_status(t): status_var.set(t); root.update_idletasks()
def toggle_wake(): wake_var.set(not wake_var.get())
def stop_assistant(): is_running[0]=False; set_status("STOPPED"); set_state("idle")

def toggle_language():
    if current_lang[0]=="en":
        current_lang[0]="hi"; memory["lang"]="hi"; save_memory(memory)
        speak("Hindi mode on Boss!")
    else:
        current_lang[0]="en"; memory["lang"]="en"; save_memory(memory)
        speak("English mode on Boss!")

def toggle_mood_hotkey():
    set_mood("serious" if current_mood[0]=="happy" else "happy")

def setup_hotkeys():
    try:
        keyboard.add_hotkey("ctrl+l",lambda:root.after(0,toggle_language))
        keyboard.add_hotkey("ctrl+m",lambda:root.after(0,toggle_mood_hotkey))
        keyboard.add_hotkey("ctrl+shift+s",lambda:threading.Thread(target=take_screenshot,daemon=True).start())
        print("Hotkeys: Ctrl+L=Language, Ctrl+M=Mood, Ctrl+Shift+S=Screenshot")
    except Exception as e: print(f"Hotkey error: {e}")

# ── R: Real-time Response - Fast TTS ──
async def _tts(text, voice, rate="+10%"):
    communicate = edge_tts.Communicate(text, voice, rate=rate)
    await communicate.save(VOICE_FILE)

def speak(text):
    print(f"RJ: {text}")
    root.after(0,lambda:set_state("speaking"))
    root.after(0,lambda:set_status("SPEAKING"))
    try:
        voice = VOICE_HI if current_lang[0]=="hi" else VOICE_EN
        rate  = "+10%" if current_lang[0]=="hi" else "+10%"  # slightly energetic
        asyncio.run(_tts(text,voice,rate))
        pygame.mixer.init()
        pygame.mixer.music.load(VOICE_FILE)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy(): time.sleep(0.05)
        pygame.mixer.music.stop()
        pygame.mixer.quit()
    except Exception as ex:
        print(f"TTS error: {ex}")
        try:
            e=pyttsx3.init(); e.setProperty('rate',170); e.setProperty('volume',1.0)
            v=e.getProperty('voices')
            for voice in v:
                if "zira" in voice.name.lower() or "hazel" in voice.name.lower() or "female" in voice.name.lower():
                    e.setProperty('voice',voice.id); break
            e.say(text); e.runAndWait(); e.stop()
        except: pass
    root.after(0,lambda:set_state("idle"))
    root.after(0,lambda:set_status("READY"))

def listen_once(timeout=6,phrase_limit=8):
    r=sr.Recognizer(); r.energy_threshold=300; r.dynamic_energy_threshold=True; r.pause_threshold=0.6
    mic=sr.Microphone(sample_rate=16000)
    with mic as src:
        root.after(0,lambda:set_state("listening")); root.after(0,lambda:set_status("LISTENING"))
        print("\n🎙️ Listening...")
        try: audio=r.listen(src,timeout=timeout,phrase_time_limit=phrase_limit)
        except sr.WaitTimeoutError:
            root.after(0,lambda:set_state("idle")); root.after(0,lambda:set_status("READY")); return ""
        except: root.after(0,lambda:set_state("idle")); return ""
    root.after(0,lambda:set_status("PROCESSING"))
    try:
        lang_code="hi-IN" if current_lang[0]=="hi" else "en-US"
        q=r.recognize_google(audio,language=lang_code)
        print(f"You: {q}"); root.after(0,lambda:set_state("idle")); return q.lower()
    except: pass
    try:
        rec=KaldiRecognizer(vosk_model,16000); ad=audio.get_raw_data(convert_rate=16000,convert_width=2)
        accepted=rec.AcceptWaveform(ad)
        q=json.loads(rec.Result() if accepted else rec.PartialResult()).get("text" if accepted else "partial","").strip()
        if q: print(f"You (Vosk): {q}"); root.after(0,lambda:set_state("idle")); return q.lower()
    except Exception as ex: print(f"Vosk error: {ex}")
    root.after(0,lambda:set_state("idle")); root.after(0,lambda:set_status("READY")); return ""

def listen_for_wake_word():
    r=sr.Recognizer(); r.energy_threshold=300; r.pause_threshold=0.5
    mic=sr.Microphone(sample_rate=16000)
    with mic as src:
        root.after(0,lambda:set_status("HEY RJ?"))
        try: audio=r.listen(src,timeout=5,phrase_time_limit=4)
        except: return False
    try:
        t=r.recognize_google(audio).lower()
        if "hey rj" in t or "rj" in t: return True
    except: pass
    return False

# ── T: Thoughtful Execution - Smart Groq ──
conversation_history=[]

def ask_groq(query):
    try:
        # E: Check emotion first
        emp = empathetic_response()

        conversation_history.append({"role":"user","content":query})
        if current_lang[0]=="hi":
            system_prompt="""Tu RJ hai, ek young female AI voice assistant jo Shiva ne banaya hai.
Tu 20-22 saal ki ladki ki tarah baat karti hai - energetic, friendly, natural.
Kabhi 'Boss' keh, kabhi 'yaar' keh, kabhi seedha baat kar - variety rakh.
Agar koi sawaal pooche toh seedha jawab de, website suggest mat kar.
Agar koi cheez nahi jaanti toh bol 'yeh mujhe nahi pata Boss'.
Emotional support do jab zarurat ho.
Max 2-3 chhote sentence. Koi markdown nahi. Bilkul natural baat kar."""
        else:
            system_prompt="""You are RJ, a young female AI assistant made by Shiva.
Talk like a 20-year-old girl - energetic, friendly, natural.
Sometimes say 'Boss', sometimes use their name, sometimes just talk directly.
Give direct answers, don't suggest websites.
If you don't know something, say 'I don't know Boss'.
Max 2-3 short sentences. No markdown. Be natural."""

        url="https://api.groq.com/openai/v1/chat/completions"
        headers={"Authorization":f"Bearer {GROQ_API_KEY}","Content-Type":"application/json"}
        payload={
            "model":"llama-3.3-70b-versatile",
            "messages":[{"role":"system","content":system_prompt},*conversation_history],
            "max_tokens":100,
            "temperature":0.9
        }
        data=requests.post(url,headers=headers,json=payload,timeout=10).json()
        reply=data["choices"][0]["message"]["content"].strip()
        reply=reply.replace("*","").replace("#","").replace("`","").strip()

        # E: Prepend empathetic response if detected
        if emp and user_emotion[0] in ["sad","angry","tired"]:
            reply = emp + " " + reply

        conversation_history.append({"role":"assistant","content":reply})
        if len(conversation_history)>12: conversation_history.pop(0); conversation_history.pop(0)
        return reply
    except Exception as ex:
        print(f"Groq error: {ex}")
        if conversation_history: conversation_history.pop()
        return "Samajh nahi aaya Boss." if current_lang[0]=="hi" else "Didn't get that Boss."

# ── DAILY BRIEFING ──
briefing_done_date=[None]

def daily_briefing():
    while True:
        now=datetime.datetime.now(); today=now.date()
        if now.hour==8 and now.minute==0 and briefing_done_date[0]!=today:
            briefing_done_date[0]=today
            threading.Thread(target=give_briefing,daemon=True).start()
        time.sleep(30)

def give_briefing():
    now=datetime.datetime.now()
    days=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    months=["January","February","March","April","May","June","July","August","September","October","November","December"]
    speak("Good morning Boss! Uthiye uthiye! Aapki daily briefing ready hai!" if current_lang[0]=="hi" else "Good morning Boss! Rise and shine! Here's your briefing!")
    speak(f"Aaj {days[now.weekday()]} hai, {now.day} {months[now.month-1]}." if current_lang[0]=="hi" else f"Today is {days[now.weekday()]}, {now.day} {months[now.month-1]}.")
    try:
        data=requests.get(f"http://api.openweathermap.org/data/2.5/weather?q=Kanpur&appid={WEATHER_API_KEY}&units=metric",timeout=5).json()
        if data["cod"]==200:
            speak(f"Mausam: {data['main']['temp']} degree, {data['weather'][0]['description']}." if current_lang[0]=="hi" else f"Weather: {data['main']['temp']}C, {data['weather'][0]['description']}.")
    except: pass
    try:
        data=requests.get(f"https://newsapi.org/v2/top-headlines?country=in&pageSize=3&apiKey={NEWS_API_KEY}",timeout=8).json()
        if data.get("status")=="ok" and data.get("articles"):
            speak("Aaj ki top khabrein Boss:" if current_lang[0]=="hi" else "Top headlines Boss:")
            for i,a in enumerate(data["articles"][:3],1):
                t=a.get("title","").split(" - ")[0]
                if t and t!="[Removed]": speak(f"{i}. {t}"); time.sleep(0.2)
    except: pass
    speak("Bas Boss! Aaj ka din mast rahe!" if current_lang[0]=="hi" else "That's it Boss! Have an amazing day!")

# ── PC STATS ──
pc_usage={}; usage_tracking=[True]

def track_pc_usage():
    while usage_tracking[0]:
        try:
            for p in psutil.process_iter(['name','cpu_percent']):
                try:
                    name=p.info['name']; cpu=p.info['cpu_percent'] or 0
                    if cpu>0.5 and name not in ('System Idle Process','System'):
                        pc_usage[name]=pc_usage.get(name,0)+cpu
                except: pass
        except: pass
        time.sleep(30)

def get_pc_stats():
    try:
        cpu=psutil.cpu_percent(interval=1); ram=psutil.virtual_memory()
        bat=psutil.sensors_battery(); disk=psutil.disk_usage('/')
        ru=ram.used//(1024**3); rt=ram.total//(1024**3); df=disk.free//(1024**3)
        if current_lang[0]=="hi":
            msg=f"Boss, CPU {cpu}%, RAM {ru}/{rt} GB, Disk {df} GB free hai."
            if bat: msg+=f" Battery {int(bat.percent)}%, {'charge ho rahi hai' if bat.power_plugged else 'charge nahi ho rahi'}."
        else:
            msg=f"Boss, CPU {cpu}%, RAM {ru}/{rt} GB, Disk {df} GB free."
            if bat: msg+=f" Battery {int(bat.percent)}%, {'charging' if bat.power_plugged else 'not charging'}."
        speak(msg)
    except Exception as e: speak("Stats nahi mila Boss."); print(e)

# ── EMAIL ──
def send_email_thread(to,subject,body):
    try:
        msg=MIMEMultipart(); msg['From']=EMAIL_ID; msg['To']=to; msg['Subject']=subject
        msg.attach(MIMEText(body,'plain'))
        s=smtplib.SMTP('smtp.gmail.com',587); s.starttls(); s.login(EMAIL_ID,EMAIL_PASS)
        s.send_message(msg); s.quit()
        speak("Email bhej diya Boss!" if current_lang[0]=="hi" else "Email sent Boss!")
    except Exception as e: speak("Email nahi gaya Boss." if current_lang[0]=="hi" else "Email failed Boss."); print(e)

def handle_email():
    speak("Kise bhejun Boss?" if current_lang[0]=="hi" else "Who should I email Boss?")
    to=listen_once(8)
    if not to: return
    to=to.replace(" at ","@").replace(" dot ",".").replace(" ","")
    speak("Subject?" if current_lang[0]=="hi" else "Subject Boss?")
    sub=listen_once(8) or "Message from RJ"
    speak("Message kya likhu?" if current_lang[0]=="hi" else "What should I write?")
    body=listen_once(10)
    if not body: return
    threading.Thread(target=send_email_thread,args=(to,sub,body),daemon=True).start()
    speak("Bhej rahi hoon Boss!" if current_lang[0]=="hi" else "Sending Boss!")

# ── WHATSAPP ──
def handle_whatsapp(query=""):
    try:
        speak("Kise message karu Boss?" if current_lang[0]=="hi" else "Who should I message Boss?")
        name=listen_once(8)
        if not name: return
        num=None; name_lower=name.lower().strip()
        for key,val in contacts.items():
            if key in name_lower or name_lower in key: num=val; break
        if not num:
            speak("Number batao Boss." if current_lang[0]=="hi" else "Say the number Boss.")
            raw=listen_once(8)
            if not raw: return
            num="91"+"".join(filter(str.isdigit,raw))
        num=num.replace("+","").strip()
        speak("Message kya bhejun?" if current_lang[0]=="hi" else "What's the message?")
        msg=listen_once(10)
        if not msg: return
        speak("Done Boss, WhatsApp pe bhej rahi hoon!" if current_lang[0]=="hi" else "Done Boss, sending on WhatsApp!")
        try:
            import pywhatkit
            now=datetime.datetime.now()
            pywhatkit.sendwhatmsg(f"+{num}",msg,now.hour,now.minute+1,15,True,3)
        except:
            webbrowser.open(f"https://wa.me/{num}?text={urllib.parse.quote(msg)}")
            speak("WhatsApp khola Boss, send dabao!" if current_lang[0]=="hi" else "WhatsApp opened Boss, press send!")
    except Exception as e: print(f"WA error: {e}")

# ── YOUTUBE SONG SEARCH ──
def play_song(query):
    song = query
    for w in ["youtube pe","youtube par","youtube mein","youtube","play","bajao","chalaao","search","gana","song","music","gaana","suno","sunao","laga do","laga"]:
        song = song.replace(w,"").strip()
    song = song.strip()
    if not song:
        speak("Kaunsa gana Boss?" if current_lang[0]=="hi" else "Which song Boss?")
        song = listen_once(8)
    if song:
        speak(f"Abhi laati hoon Boss, {song} YouTube pe!" if current_lang[0]=="hi" else f"On it Boss, playing {song} on YouTube!")
        webbrowser.open(f"https://www.youtube.com/results?search_query={urllib.parse.quote(song)}")

# ── SCREENSHOT ──
def take_screenshot():
    try:
        os.makedirs(SCREENSHOT_DIR,exist_ok=True)
        fname=os.path.join(SCREENSHOT_DIR,f"ss_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        ImageGrab.grab().save(fname)
        speak("Screenshot le liya Boss!" if current_lang[0]=="hi" else "Screenshot done Boss!")
    except Exception as e: print(e)

# ── AUTO TYPE ──
def auto_type(query):
    text=query.replace("type","").replace("likho","").replace("type karo","").strip()
    if not text:
        speak("Kya likhu Boss?" if current_lang[0]=="hi" else "What to type Boss?")
        text=listen_once(8)
    if text:
        speak("2 second Boss!" if current_lang[0]=="hi" else "2 seconds Boss!")
        time.sleep(2); pyautogui.write(text,interval=0.05)

# ── FILE ORGANIZER ──
def organize_files(query):
    try:
        if "download" in query: folder=os.path.expanduser("~\\Downloads"); fn="Downloads"
        elif "desktop" in query: folder=os.path.expanduser("~\\Desktop"); fn="Desktop"
        else: folder=os.path.expanduser("~\\Documents"); fn="Documents"
        speak(f"Kar deti hoon Boss, {fn} organize!" if current_lang[0]=="hi" else f"On it Boss, organizing {fn}!")
        cats={"Images":[".jpg",".jpeg",".png",".gif",".bmp",".webp"],"Videos":[".mp4",".mkv",".avi",".mov"],"Audio":[".mp3",".wav",".flac",".aac"],"Documents":[".pdf",".doc",".docx",".txt",".pptx",".xlsx",".csv"],"Archives":[".zip",".rar",".7z"],"Code":[".py",".js",".html",".css"],"Executables":[".exe",".msi",".bat"]}
        moved=0
        for fname in os.listdir(folder):
            fp=os.path.join(folder,fname)
            if os.path.isfile(fp):
                ext=os.path.splitext(fname)[1].lower()
                for cat,exts in cats.items():
                    if ext in exts:
                        cf=os.path.join(folder,cat); os.makedirs(cf,exist_ok=True)
                        dest=os.path.join(cf,fname)
                        if not os.path.exists(dest): os.rename(fp,dest); moved+=1
                        break
        speak(f"Ho gaya Boss! {moved} files set!" if current_lang[0]=="hi" else f"Done Boss! {moved} files organized!")
    except Exception as e: print(e)

# ── MEMORY ──
def remember_something(query):
    note=query.replace("remember","").replace("note","").replace("save","").replace("yaad rakho","").replace("note karo","").strip()
    if not note:
        speak("Kya yaad rakhu Boss?" if current_lang[0]=="hi" else "What to remember Boss?")
        note=listen_once(8)
    if note:
        memory["notes"].append({"text":note,"time":datetime.datetime.now().strftime("%Y-%m-%d %H:%M")})
        save_memory(memory); speak("Noted Boss!" if current_lang[0]=="hi" else "Got it Boss!")

def recall_notes():
    notes=memory.get("notes",[])
    if not notes: speak("Koi note nahi hai Boss." if current_lang[0]=="hi" else "No notes Boss."); return
    speak(f"Boss, {len(notes)} notes hain:" if current_lang[0]=="hi" else f"Boss, {len(notes)} notes:")
    for n in notes[-3:]: speak(n["text"])

# ── NEWS ──
def get_news(topic=None):
    try:
        url=f"https://newsapi.org/v2/everything?q={topic}&sortBy=publishedAt&pageSize=5&apiKey={NEWS_API_KEY}" if topic else f"https://newsapi.org/v2/top-headlines?country=in&pageSize=5&apiKey={NEWS_API_KEY}"
        data=requests.get(url,timeout=8).json()
        if data.get("status")!="ok" or not data.get("articles"):
            speak("News nahi mili Boss." if current_lang[0]=="hi" else "News unavailable Boss."); return
        speak("Lo Boss, aaj ki khabrein:" if current_lang[0]=="hi" else "Here Boss, today's news:")
        count=0
        for a in data["articles"]:
            t=a.get("title","").split(" - ")[0]
            if t and t!="[Removed]" and len(t)>10:
                speak(f"{count+1}. {t}"); time.sleep(0.2); count+=1
                if count>=3: break
    except Exception as e: print(f"News error: {e}")

# ── JOKES ──
JOKES_HI=["Ek programmer raat bhar kaam karta raha. Subah boss ne pucha kya hua? Bola bug tha. Fix hua? Bola nahi, so gaya!","Programmer ki shaadi mein pandit ne kaha Qubool hai? Programmer bola Error 404!","Boss computer slow kyun hai? Bahut saare tabs khule hain, bilkul tumhari tarah!","Ek AI ne kaha main insaan ban jaana chahti hoon. Dusri AI boli phir subah uthna padega!"]
JOKES_EN=["Why don't scientists trust atoms? Because they make up everything!","Why do programmers prefer dark mode? Because light attracts bugs!","Why did the Python programmer wear glasses? Because he couldn't C!"]

def tell_joke():
    if current_lang[0]=="hi": speak(random.choice(JOKES_HI))
    else: speak(random.choice(JOKES_EN))

# ── ALARM ──
def set_alarm(query):
    try:
        clean=query.replace("set alarm","").replace("alarm for","").replace("alarm at","").replace("alarm lagao","").replace("baje","").replace("ka alarm","").strip()
        nums=[w for w in clean.split() if w.isdigit()]
        if len(nums)>=2: h,m=int(nums[0]),int(nums[1])
        elif len(nums)==1: h,m=int(nums[0]),0
        else: speak("Time batao Boss!" if current_lang[0]=="hi" else "Say the time Boss!"); return
        speak(f"Done Boss! {h}:{m:02d} ka alarm set!" if current_lang[0]=="hi" else f"Done Boss! Alarm set for {h}:{m:02d}!")
        def at():
            while True:
                n=datetime.datetime.now()
                if n.hour==h and n.minute==m and n.second<3:
                    speak("Boss uthiye! Alarm baj raha hai!" if current_lang[0]=="hi" else "Boss wake up! Alarm ringing!"); break
                time.sleep(1)
        threading.Thread(target=at,daemon=True).start()
    except: speak("Alarm set nahi hua Boss.")

# ── REMINDER ──
def set_reminder(query):
    try:
        words=query.split(); mins=1; msg="aapka reminder"
        for w in words:
            if w.isdigit(): mins=int(w); break
        if "to" in query:
            ms=query.index("to")+3; me=query.index(" in") if " in" in query else len(query)
            msg=query[ms:me].strip()
        speak(f"Set ho gaya Boss! {mins} minute mein bataungi!" if current_lang[0]=="hi" else f"Set Boss! Will remind in {mins} min!")
        def rt(): time.sleep(mins*60); speak(f"Boss! {msg} yaad hai na?" if current_lang[0]=="hi" else f"Boss! Reminder: {msg}!")
        threading.Thread(target=rt,daemon=True).start()
    except: speak("Reminder set nahi hua Boss.")

# ── SYSTEM CONTROL ──
def system_control(query):
    try:
        ps=lambda k: os.system(f'powershell -c "$w=New-Object -com wscript.shell;$w.SendKeys([char]{k})"')
        if   "volume up"       in query: ps(175); speak("Volume badha diya!")
        elif "volume down"     in query: ps(174); speak("Volume ghata diya!")
        elif "unmute"          in query: ps(173); speak("Unmute!")
        elif "mute"            in query: ps(173); speak("Mute!")
        elif "brightness up"   in query:
            os.system("powershell (Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,80)")
            speak("Brightness badha di!")
        elif "brightness down" in query:
            os.system("powershell (Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,40)")
            speak("Brightness ghata di!")
        elif "cancel shutdown"  in query: os.system("shutdown /a"); speak("Shutdown cancel Boss!")
        elif "shutdown"         in query:
            speak("Theek hai Boss, 10 second mein shutdown!" if current_lang[0]=="hi" else "Sure Boss, shutting down in 10!")
            time.sleep(2); os.system("shutdown /s /t 10")
        elif "restart"          in query:
            speak("Restart ho raha hai Boss!" if current_lang[0]=="hi" else "Restarting Boss!")
            time.sleep(2); os.system("shutdown /r /t 10")
        elif "sleep"            in query:
            speak("Okay Boss, good night!" if current_lang[0]=="hi" else "Sleep mode Boss, good night!")
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        elif "lock"             in query:
            speak("Lock kar rahi hoon Boss!" if current_lang[0]=="hi" else "Locking Boss!")
            def do_lock(): time.sleep(1.5); ctypes.windll.user32.LockWorkStation()
            threading.Thread(target=do_lock,daemon=False).start()
        else: speak("Samajh nahi aaya Boss." if current_lang[0]=="hi" else "Didn't get that Boss.")
    except Exception as e: print(f"System error: {e}")

def get_time():
    n=datetime.datetime.now()
    if current_lang[0]=="hi": speak(f"Boss, abhi {n.strftime('%I')}:{n.strftime('%M')} {n.strftime('%p')} baj rahe hain.")
    else: speak(f"Boss, it's {n.strftime('%I')}:{n.strftime('%M')} {n.strftime('%p')}.")

def get_date():
    n=datetime.datetime.now()
    days=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    months=["January","February","March","April","May","June","July","August","September","October","November","December"]
    if current_lang[0]=="hi": speak(f"Boss, aaj {days[n.weekday()]} hai, {n.day} {months[n.month-1]} {n.year}.")
    else: speak(f"Boss, today is {days[n.weekday()]}, {n.day} {months[n.month-1]} {n.year}.")

def get_weather(city="Kanpur"):
    try:
        data=requests.get(f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric",timeout=5).json()
        if data["cod"]==200:
            if current_lang[0]=="hi": speak(f"Boss, {city} mein {data['main']['temp']} degree hai, {data['weather'][0]['description']} chal raha hai.")
            else: speak(f"Boss, {city}: {data['main']['temp']}C, {data['weather'][0]['description']}, humidity {data['main']['humidity']}%.")
        else: speak(f"Boss, {city} ka data nahi mila.")
    except: speak("Weather nahi mila Boss.")

def search_wikipedia(query):
    try:
        wikipedia.set_lang("en")
        results=wikipedia.search(query,results=1)
        if not results: speak("Kuch nahi mila Boss." if current_lang[0]=="hi" else "Nothing found Boss."); return
        speak('. '.join(wikipedia.page(results[0]).summary.split('. ')[:2])+'.')
    except wikipedia.exceptions.DisambiguationError as e:
        try: speak('. '.join(wikipedia.page(e.options[0]).summary.split('. ')[:2])+'.')
        except: speak("Thoda clear batao Boss.")
    except: speak("Search nahi ho saka Boss.")

def open_app(query):
    apps={
        "youtube":   ("YouTube",     "https://www.youtube.com",  "web"),
        "google":    ("Google",      "https://www.google.com",   "web"),
        "whatsapp":  ("WhatsApp",    "https://web.whatsapp.com", "web"),
        "github":    ("GitHub",      "https://www.github.com",   "web"),
        "chatgpt":   ("ChatGPT",     "https://chat.openai.com",  "web"),
        "maps":      ("Google Maps", "https://maps.google.com",  "web"),
        "notepad":   ("Notepad",     "notepad.exe",              "app"),
        "calculator":("Calculator",  "calc.exe",                 "app"),
        "explorer":  ("Explorer",    "explorer.exe",             "app"),
        "instagram": ("Instagram",   "https://www.instagram.com","web"),
        "twitter":   ("Twitter",     "https://www.twitter.com",  "web"),
    }
    for key,(name,target,t) in apps.items():
        if key in query:
            speak(f"Abhi kholta hoon Boss, {name}!" if current_lang[0]=="hi" else f"Opening {name} Boss!")
            webbrowser.open(target) if t=="web" else os.system(target); return
    speak("Yeh app nahi mila Boss." if current_lang[0]=="hi" else "App not found Boss.")

# ── H: Human-like Greet ──
def greet():
    h=datetime.datetime.now().hour
    # A: Check if we have adaptive suggestion
    adaptive = get_adaptive_greeting()

    if current_lang[0]=="hi":
        if 5<=h<12:
            greets=["Good morning Boss! Kya plan hai aaj ka?","Uthiye uthiye Boss! Kaam time hai!","Morning Boss! Chai pi li?"]
        elif 12<=h<17:
            greets=["Good afternoon Boss! Kya chal raha hai?","Lunch ho gaya Boss?","Heyyy Boss! Kya haal hai?"]
        elif 17<=h<21:
            greets=["Good evening Boss! Din kaisa gaya?","Evening Boss! Thake ho kya?","Heyy Boss! Kya karna hai ab?"]
        else:
            greets=["Arre Boss itni raat ko! Neend nahi aayi?","Haan Boss, main hoon! Kya kaam hai?","Raat ko bhi kaam Boss?"]
        speak(random.choice(greets))
    else:
        if 5<=h<12:   speak(random.choice(["Good morning Boss! What's the plan today?","Morning Boss! Ready to rock?"]))
        elif 12<=h<17: speak(random.choice(["Hey Boss! Good afternoon! What's up?","Afternoon Boss! How's your day going?"]))
        elif 17<=h<21: speak(random.choice(["Evening Boss! How was your day?","Hey Boss! What can I do for you?"]))
        else:          speak(random.choice(["Hey Boss! Late night? I'm here!","Hey Boss! What do you need?"]))

    # A: Adaptive suggestion after greeting
    if adaptive and interaction_count[0] > 5:
        time.sleep(0.5); speak(adaptive)

# ── NORMALIZE QUERY ──
def normalize_query(q):
    replacements={
        "गूगल":"google","यूट्यूब":"youtube","व्हाट्सएप":"whatsapp",
        "नोटपैड":"notepad","कैलकुलेटर":"calculator","चैटजीपीटी":"chatgpt",
        "इंस्टाग्राम":"instagram","ट्विटर":"twitter",
        "खोलो":"open","खोल दो":"open","खोल":"open","ओपन":"open","चलाओ":"open","चला दो":"open",
        "बंद करो":"shutdown","शटडाउन":"shutdown","शट डाउन":"shutdown","सिस्टम बंद":"shutdown",
        "लॉक करो":"lock","लॉक कर दो":"lock","लॉक":"lock",
        "रीस्टार्ट":"restart","रिस्टार्ट":"restart",
        "कितने बजे":"time","समय":"time","वक्त":"time","टाइम":"time",
        "मौसम":"weather","तापमान":"weather","मौसम कैसा":"weather",
        "खबर":"news","खबरें":"news","समाचार":"news","न्यूज़":"news","न्यूज":"news",
        "गाना":"song","गाने":"song","गाना बजाओ":"song","म्यूजिक":"song","सॉन्ग":"song",
        "बजाओ":"play song","सुनाओ":"play song","लगाओ":"play song",
        "स्क्रीनशॉट":"screenshot","स्क्रीन शॉट":"screenshot",
        "वॉल्यूम":"volume","आवाज":"volume","साउंड":"volume",
        "ब्राइटनेस":"brightness",
        "नींद":"sleep","सो जाओ":"sleep","स्लीप":"sleep",
        "बैटरी":"battery","रैम":"ram","सीपीयू":"cpu",
        "मजाक":"joke","हंसाओ":"joke","चुटकुला":"joke","जोक":"joke",
        "अलार्म":"alarm","अलार्म लगाओ":"alarm",
        "याद दिलाओ":"remind","रिमाइंडर":"remind",
        "कैसे हो":"how are you","कैसी हो":"how are you","कैसा लग रहा":"how are you",
    }
    for hindi,english in replacements.items():
        q=q.replace(hindi,english)
    return q

# ── T: Thoughtful Command Processor ──
def process_command(query):
    if not query: return True
    original_query = query

    # E: Detect emotion
    detect_emotion(query)

    query = normalize_query(query)

    # H: Check casual responses first
    casual = check_casual(query)
    if casual:
        speak(casual); return True

    # ── Creator identity ──
    if any(x in query for x in ["kisne banaya","tumhe kisne banaya","who made you","who created you","kisne banayi","kaun banaya"]):
        speak("Mujhe Shiva  Boss ne banaya hai! Main unki AI assistant hoon!" if current_lang[0]=="hi" else "Shiva made me Boss! I'm his awesome AI assistant!")
        return True

    # ── How are you ──
    if any(x in query for x in ["how are you","kaisi ho","kaise ho","kya haal","hal chaal","kya kar rahi","kya ho raha"]):
        emp = empathetic_response()
        if not emp:
            hi=["Main ekdum mast hoon Boss! Aap sunao?","Badiya hoon Boss! Kuch kaam hai?","Bahut achha chal raha hai Boss! Aap?","Mast hoon yaar! Bolo kya chahiye?"]
            en=["I'm doing great Boss! How about you?","Super good Boss! What do you need?","Amazing Boss, always ready for you!"]
            emp = random.choice(hi if current_lang[0]=="hi" else en)
        speak(emp); return True

    # ── Language & mood ──
    if any(x in query for x in ["hindi mode","hindi mein baat","switch to hindi"]): toggle_language(); return True
    if any(x in query for x in ["english mode","switch to english","angrezi mein"]):
        if current_lang[0]=="hi": toggle_language()
        return True
    if any(x in query for x in ["happy mode","fun mode"]): set_mood("happy"); return True
    if "serious mode" in query: set_mood("serious"); return True
    if any(x in query for x in ["briefing","morning report","daily update"]):
        threading.Thread(target=give_briefing,daemon=True).start(); return True

    # ── Song/Music ──
    if any(x in query for x in ["play song","song","gana","gaana","bajao","sunao","music","youtube pe","youtube par","laga do"]):
        track_command("song"); play_song(original_query); return True

    # ── Main commands ──
    if   any(x in query for x in ["time","kitne baje","samay","waqt","baj rahe"]):
        track_command("time"); get_time()
    elif any(x in query for x in ["date","today","aaj","din","kaunsa din"]):
        track_command("date"); get_date()
    elif any(x in query for x in ["weather","temperature","mausam"]):
        track_command("weather")
        skip={"weather","temperature","mausam","in","of","the","what","is","tell","me","kaisa","hai","aaj","batao","boss","kanpur"}
        words=[w for w in query.split() if w not in skip and len(w)>2]
        city=words[0].capitalize() if words else "Kanpur"
        get_weather(city)
    elif any(x in query for x in ["news","headline","khabar","samachar"]):
        track_command("news")
        skip={"news","headline","headlines","latest","tell","me","about","what","is","the","today","top","khabar","khabrein","batao","aaj","ki","samachar","boss","sunao"}
        topic=" ".join(w for w in query.split() if w not in skip).strip()
        get_news(topic if len(topic)>2 else None)
    elif any(x in query for x in ["wikipedia","who is","tell me about","kaun hai"]):
        q=query.replace("wikipedia","").replace("who is","").replace("what is","").replace("tell me about","").replace("kaun hai","").replace("kya hai","").strip()
        search_wikipedia(q) if q else speak("Kya dhundhu Boss?" if current_lang[0]=="hi" else "What to search Boss?")
    elif any(x in query for x in ["send email","email bhejo","write email","email karo","email"]): handle_email()
    elif any(x in query for x in ["whatsapp","whatsapp pe","message bhejo","msg karo"]):
        track_command("whatsapp"); handle_whatsapp(query)
    elif "screenshot" in query: threading.Thread(target=take_screenshot,daemon=True).start()
    elif any(x in query for x in ["battery","ram","cpu","system status","pc stats"]): get_pc_stats()
    elif any(x in query for x in ["type","likho","type karo"]): auto_type(query)
    elif any(x in query for x in ["organize","sort files","folder saaf"]): organize_files(query)
    elif any(x in query for x in ["remember","yaad rakho","note karo"]): remember_something(query)
    elif any(x in query for x in ["my notes","recall","kya yaad"]): recall_notes()
    elif any(x in query for x in ["open","launch","kholo","chalaao","chalu"]): open_app(query)
    elif any(x in query for x in ["google search","search karo","dhundho","find"]):
        q=query.replace("google search","").replace("search karo","").replace("dhundho","").replace("find","").strip()
        if q: speak("Searching Boss!" if current_lang[0]=="hi" else "Searching Boss!"); webbrowser.open(f"https://www.google.com/search?q={q}")
        else: speak("Kya dhundhu Boss?" if current_lang[0]=="hi" else "What to search Boss?")
    elif any(x in query for x in ["joke","funny","hasao","chutkula"]): tell_joke()
    elif "alarm" in query: set_alarm(query)
    elif any(x in query for x in ["remind","yaad dilao"]): set_reminder(query)
    elif any(w in query for w in ["volume","brightness","shutdown","restart","sleep","lock","mute","unmute"]):
        system_control(query)
    elif any(w in query for w in ["bye","exit","quit","goodbye","alvida","band karo rj"]):
        speak("Bye Boss! Kuch bhi chahiye toh bulana!" if current_lang[0]=="hi" else "Bye Boss! Call me anytime!")
        return False
    else:
        # T: Thoughtful - use Groq for unknown queries
        speak(ask_groq(original_query))
    return True

# ── MAIN LOOP ──
def assistant_loop():
    greet()
    root.after(0,lambda:set_status("READY"))
    while is_running[0]:
        try:
            if wake_var.get():
                if not listen_for_wake_word(): continue
                speak(random.choice(["Haan Boss!","Bolo!","Ji Boss?","Kya hua?","Haan haan!"]) if current_lang[0]=="hi" else random.choice(["Yes Boss?","What's up?","I'm here Boss!","At your service!"]))
            query=listen_once()
            if query:
                running=process_command(query)
                if not running:
                    is_running[0]=False
                    root.after(0,lambda:set_status("STOPPED"))
                    root.after(0,lambda:set_state("idle"))
                    break
        except Exception as e: print(f"Loop error: {e}"); time.sleep(0.5)

draw_hud()
setup_hotkeys()
threading.Thread(target=track_pc_usage,daemon=True).start()
threading.Thread(target=daily_briefing,daemon=True).start()
threading.Thread(target=assistant_loop,daemon=True).start()

if __name__=="__main__":
    root.mainloop()
    usage_tracking[0]=False