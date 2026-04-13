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
VOICE_EN        = "en-US-BrianNeural"
VOICE_HI        = "hi-IN-MadhurNeural"

current_mood = ["happy"]
MOOD_HAPPY_PHRASES   = ["Sure thing!", "On it!", "Absolutely!", "You got it!"]
MOOD_SERIOUS_PHRASES = ["Understood.", "Right away.", "Noted."]

def get_mood_ack():
    return random.choice(MOOD_HAPPY_PHRASES if current_mood[0]=="happy" else MOOD_SERIOUS_PHRASES)

def set_mood(mood):
    current_mood[0] = mood
    memory["preferences"]["mood"] = mood
    save_memory(memory)
    speak("Happy mode on!" if mood=="happy" else "Serious mode on.")

def load_memory():
    try:
        if os.path.exists(MEMORY_FILE):
            with open(MEMORY_FILE,"r") as f: return json.load(f)
    except: pass
    return {"name":"Shiva","preferences":{},"notes":[],"last_seen":"","lang":"en"}

def save_memory(m):
    try:
        with open(MEMORY_FILE,"w") as f: json.dump(m,f,indent=2)
    except: pass

memory = load_memory()
memory["last_seen"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
save_memory(memory)
current_lang = [memory.get("lang","en")]
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
        speak("Hindi mode on.")
    else:
        current_lang[0]="en"; memory["lang"]="en"; save_memory(memory)
        speak("English mode on.")

def toggle_mood_hotkey():
    set_mood("serious" if current_mood[0]=="happy" else "happy")

def setup_hotkeys():
    try:
        keyboard.add_hotkey("ctrl+l",lambda:root.after(0,toggle_language))
        keyboard.add_hotkey("ctrl+m",lambda:root.after(0,toggle_mood_hotkey))
        keyboard.add_hotkey("ctrl+shift+s",lambda:threading.Thread(target=take_screenshot,daemon=True).start())
        print("Hotkeys: Ctrl+L=Language, Ctrl+M=Mood, Ctrl+Shift+S=Screenshot")
    except Exception as e: print(f"Hotkey error: {e}")

# ── SPEAK - faster rate ──
async def _tts(text,voice,rate="+15%"):
    communicate=edge_tts.Communicate(text,voice,rate=rate)
    await communicate.save(VOICE_FILE)

def speak(text):
    print(f"RJ: {text}")
    root.after(0,lambda:set_state("speaking"))
    root.after(0,lambda:set_status("SPEAKING"))
    try:
        voice=VOICE_HI if current_lang[0]=="hi" else VOICE_EN
        rate="+20%" if current_lang[0]=="hi" else "+15%"
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
            e=pyttsx3.init(); e.setProperty('rate',175); e.setProperty('volume',1.0)
            v=e.getProperty('voices'); e.setProperty('voice',v[0].id)
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

# ── GROQ - better prompt ──
conversation_history=[]

def ask_groq(query):
    try:
        conversation_history.append({"role":"user","content":query})
        nm=memory.get("name","Shiva")
        if current_lang[0]=="hi":
           system_prompt=f"Tu RJ hai, ek AI voice assistant jo {nm} sir ne banaya hai. User ko 'sir' kehkar baat kar. Seedha kaam ki baat kar, baar baar naam mat le. Jab koi kaam karne ko kaho to bolo 'Theek hai sir, ye kaam kar raha hoon.' Natural Hindi mein baat kar. Max 2 sentence. No markdown."
        else:
            system_prompt=f"You are RJ, an AI voice assistant. Be direct and helpful. Don't repeat the user's name too much. Max 2 sentences. No markdown. {'Be casual and friendly.' if current_mood[0]=='happy' else 'Be professional.'}"

        url="https://api.groq.com/openai/v1/chat/completions"
        headers={"Authorization":f"Bearer {GROQ_API_KEY}","Content-Type":"application/json"}
        payload={
            "model":"llama-3.3-70b-versatile",
            "messages":[{"role":"system","content":system_prompt},*conversation_history],
            "max_tokens":100,
            "temperature":0.8 if current_mood[0]=="happy" else 0.4
        }
        data=requests.post(url,headers=headers,json=payload,timeout=10).json()
        reply=data["choices"][0]["message"]["content"].strip()
        reply=reply.replace("*","").replace("#","").replace("`","").strip()
        conversation_history.append({"role":"assistant","content":reply})
        if len(conversation_history)>10: conversation_history.pop(0); conversation_history.pop(0)
        return reply
    except Exception as ex:
        print(f"Groq error: {ex}")
        if conversation_history: conversation_history.pop()
        return "Samajh nahi aaya." if current_lang[0]=="hi" else "Sorry, couldn't process that."

briefing_done_date=[None]

def daily_briefing():
    while True:
        now=datetime.datetime.now(); today=now.date()
        if now.hour==8 and now.minute==0 and briefing_done_date[0]!=today:
            briefing_done_date[0]=today
            threading.Thread(target=give_briefing,daemon=True).start()
        time.sleep(30)

def give_briefing():
    nm=memory.get("name","Shiva"); now=datetime.datetime.now()
    days=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    months=["January","February","March","April","May","June","July","August","September","October","November","December"]
    speak(f"Good morning {nm}! Daily briefing sun lo." if current_lang[0]=="hi" else f"Good morning {nm}! Here's your daily briefing.")
    speak(f"Aaj {days[now.weekday()]} hai, {now.day} {months[now.month-1]}." if current_lang[0]=="hi" else f"Today is {days[now.weekday()]}, {now.day} {months[now.month-1]}.")
    try:
        data=requests.get(f"http://api.openweathermap.org/data/2.5/weather?q=Kanpur&appid={WEATHER_API_KEY}&units=metric",timeout=5).json()
        if data["cod"]==200:
            speak(f"Mausam: {data['main']['temp']} degree, {data['weather'][0]['description']}." if current_lang[0]=="hi" else f"Weather: {data['main']['temp']}°C, {data['weather'][0]['description']}.")
    except: pass
    try:
        data=requests.get(f"https://newsapi.org/v2/top-headlines?country=in&pageSize=3&apiKey={NEWS_API_KEY}",timeout=8).json()
        if data.get("status")=="ok" and data.get("articles"):
            speak("Top khabrein:" if current_lang[0]=="hi" else "Top headlines:")
            for i,a in enumerate(data["articles"][:3],1):
                t=a.get("title","").split(" - ")[0]
                if t and t!="[Removed]": speak(f"{i}. {t}"); time.sleep(0.2)
    except: pass
    speak("Bas! Achha din ho!" if current_lang[0]=="hi" else f"That's it! Have a great day!")

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
            msg=f"CPU {cpu}%, RAM {ru}/{rt} GB, Disk free {df} GB."
            if bat: msg+=f" Battery {int(bat.percent)}%, {'charge ho rahi' if bat.power_plugged else 'nahi charge ho rahi'}."
        else:
            msg=f"CPU {cpu}%, RAM {ru}/{rt} GB, Disk {df} GB free."
            if bat: msg+=f" Battery {int(bat.percent)}%, {'charging' if bat.power_plugged else 'not charging'}."
        if pc_usage:
            top=sorted(pc_usage.items(),key=lambda x:x[1],reverse=True)[:3]
            apps=", ".join(n.replace(".exe","") for n,_ in top)
            msg+=f" Top apps: {apps}."
        speak(msg)
    except Exception as e: speak("Stats nahi mila." if current_lang[0]=="hi" else "Could not get stats."); print(e)

def send_email_thread(to,subject,body):
    try:
        msg=MIMEMultipart(); msg['From']=EMAIL_ID; msg['To']=to; msg['Subject']=subject
        msg.attach(MIMEText(body,'plain'))
        s=smtplib.SMTP('smtp.gmail.com',587); s.starttls(); s.login(EMAIL_ID,EMAIL_PASS)
        s.send_message(msg); s.quit()
        speak("Email chala gaya!" if current_lang[0]=="hi" else "Email sent!")
    except Exception as e: speak("Email fail." if current_lang[0]=="hi" else "Email failed."); print(e)

def handle_email():
    speak("Kise?" if current_lang[0]=="hi" else "Who should I email?")
    to=listen_once(8)
    if not to: return
    to=to.replace(" at ","@").replace(" dot ",".").replace(" ","")
    speak("Subject?" if current_lang[0]=="hi" else "Subject?")
    sub=listen_once(8) or "Message from RJ"
    speak("Message?" if current_lang[0]=="hi" else "Message?")
    body=listen_once(10)
    if not body: return
    threading.Thread(target=send_email_thread,args=(to,sub,body),daemon=True).start()
    speak(f"Bhej raha hoon." if current_lang[0]=="hi" else "Sending.")

def handle_whatsapp():
    try:
        speak("Kise?" if current_lang[0]=="hi" else "Who?")
        name=listen_once(8)
        if not name: return
        num=None; name_lower=name.lower().strip()
        for key,val in contacts.items():
            if key in name_lower or name_lower in key: num=val; break
        if not num:
            speak("Number batao." if current_lang[0]=="hi" else "Say the number.")
            raw=listen_once(8)
            if not raw: return
            num="91"+"".join(filter(str.isdigit,raw))
        num=num.replace("+","").strip()
        speak("Message?" if current_lang[0]=="hi" else "Message?")
        msg=listen_once(10)
        if not msg: return
        speak("WhatsApp khol raha hoon." if current_lang[0]=="hi" else "Opening WhatsApp.")
        webbrowser.open(f"https://wa.me/{num}?text={urllib.parse.quote(msg)}")
    except Exception as e: print(f"WA error: {e}")

def take_screenshot():
    try:
        os.makedirs(SCREENSHOT_DIR,exist_ok=True)
        fname=os.path.join(SCREENSHOT_DIR,f"ss_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        ImageGrab.grab().save(fname)
        speak("Screenshot liya!" if current_lang[0]=="hi" else "Screenshot saved!")
    except Exception as e: print(e)

def auto_type(query):
    text=query.replace("type","").replace("likho","").replace("type karo","").strip()
    if not text: speak("Kya likhu?" if current_lang[0]=="hi" else "What to type?"); text=listen_once(8)
    if text: speak("2 second..." if current_lang[0]=="hi" else "Typing in 2s!"); time.sleep(2); pyautogui.write(text,interval=0.05)

def organize_files(query):
    try:
        if "download" in query: folder=os.path.expanduser("~\\Downloads"); fn="Downloads"
        elif "desktop" in query: folder=os.path.expanduser("~\\Desktop"); fn="Desktop"
        else: folder=os.path.expanduser("~\\Documents"); fn="Documents"
        speak(f"{fn} organize kar raha hoon." if current_lang[0]=="hi" else f"Organizing {fn}.")
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
        speak(f"{moved} files organize ki." if current_lang[0]=="hi" else f"Done! Moved {moved} files.")
    except Exception as e: print(e)

def remember_something(query):
    note=query.replace("remember","").replace("note","").replace("save","").replace("yaad rakho","").replace("note karo","").strip()
    if not note: speak("Kya?" if current_lang[0]=="hi" else "What to remember?"); note=listen_once(8)
    if note:
        memory["notes"].append({"text":note,"time":datetime.datetime.now().strftime("%Y-%m-%d %H:%M")})
        save_memory(memory); speak("Yaad rakh liya!" if current_lang[0]=="hi" else "Noted!")

def recall_notes():
    notes=memory.get("notes",[])
    if not notes: speak("Koi note nahi." if current_lang[0]=="hi" else "No notes."); return
    speak(f"{len(notes)} notes hain:" if current_lang[0]=="hi" else f"{len(notes)} notes:")
    for n in notes[-3:]: speak(n["text"])

def get_news(topic=None):
    try:
        url=f"https://newsapi.org/v2/everything?q={topic}&sortBy=publishedAt&pageSize=5&apiKey={NEWS_API_KEY}" if topic else f"https://newsapi.org/v2/top-headlines?country=in&pageSize=5&apiKey={NEWS_API_KEY}"
        data=requests.get(url,timeout=8).json()
        if data.get("status")!="ok" or not data.get("articles"):
            speak("News nahi mili." if current_lang[0]=="hi" else "News unavailable."); return
        speak("Khabrein:" if current_lang[0]=="hi" else "Headlines:")
        for i,a in enumerate(data["articles"][:3],1):
            t=a.get("title","").split(" - ")[0]
            if t and t!="[Removed]": speak(f"{i}. {t}"); time.sleep(0.2)
    except Exception as e: print(e)

JOKES_HAPPY=["Why don't scientists trust atoms? Because they make up everything!","Why do programmers prefer dark mode? Because light attracts bugs!","Why did the Python programmer wear glasses? Because he couldn't C!","Why is the computer so cold? Because it left its Windows open!"]
JOKES_HI=["Ek programmer raat bhar kaam karta raha. Subah boss ne pucha kya hua? Bola bug tha. Boss bola fix hua? Bola nahi, so gaya!","Programmer ki shaadi mein pandit ne kaha Qubool hai? Programmer bola Error 404 Response not found!","Student ne teacher se pucha sir computer slow kyun hai? Teacher bola bahut saare tabs khule hain, theek tumhari tarah!"]
JOKES_SERIOUS=["Why did the programmer quit? He didn't get arrays.","There are 10 types of people: those who understand binary and those who don't."]

def tell_joke():
    if current_lang[0]=="hi": speak(random.choice(JOKES_HI))
    elif current_mood[0]=="happy": speak(random.choice(JOKES_HAPPY))
    else: speak(random.choice(JOKES_SERIOUS))

def set_alarm(query):
    try:
        clean=query.replace("set alarm","").replace("alarm for","").replace("alarm at","").replace("alarm lagao","").replace("baje","").strip()
        nums=[w for w in clean.split() if w.isdigit()]
        if len(nums)>=2: h,m=int(nums[0]),int(nums[1])
        elif len(nums)==1: h,m=int(nums[0]),0
        else: speak("Time batao." if current_lang[0]=="hi" else "Say the time."); return
        speak(f"{h}:{m:02d} ka alarm set ho gaya." if current_lang[0]=="hi" else f"Alarm set for {h}:{m:02d}.")
        def at():
            while True:
                n=datetime.datetime.now()
                if n.hour==h and n.minute==m and n.second<3: speak("Alarm! Uthiye!" if current_lang[0]=="hi" else "Wake up! Alarm!"); break
                time.sleep(1)
        threading.Thread(target=at,daemon=True).start()
    except: speak("Alarm fail." if current_lang[0]=="hi" else "Alarm failed.")

def set_reminder(query):
    try:
        words=query.split(); mins=1; msg="reminder"
        for i,w in enumerate(words):
            if w.isdigit(): mins=int(w); break
        if "to" in query:
            ms=query.index("to")+3; me=query.index(" in") if " in" in query else len(query)
            msg=query[ms:me].strip()
        speak(f"{mins} minute mein remind karunga." if current_lang[0]=="hi" else f"Reminder in {mins} min.")
        def rt(): time.sleep(mins*60); speak(f"Reminder: {msg}")
        threading.Thread(target=rt,daemon=True).start()
    except: speak("Reminder fail." if current_lang[0]=="hi" else "Reminder failed.")

def system_control(query):
    try:
        ps=lambda k: os.system(f'powershell -c "$w=New-Object -com wscript.shell;$w.SendKeys([char]{k})"')
        if   "volume up" in query or "volume badha" in query: ps(175); speak("Volume up.")
        elif "volume down" in query or "volume ghata" in query: ps(174); speak("Volume down.")
        elif "unmute" in query: ps(173); speak("Unmuted.")
        elif "mute" in query: ps(173); speak("Muted.")
        elif "brightness up" in query or "brightness badha" in query:
            os.system("powershell (Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,80)")
            speak("Brightness up.")
        elif "brightness down" in query or "brightness ghata" in query:
            os.system("powershell (Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,40)")
            speak("Brightness down.")
        elif "cancel shutdown" in query: os.system("shutdown /a"); speak("Cancelled.")
        elif "shutdown" in query or "band karo" in query:
            speak("10 second mein shutdown." if current_lang[0]=="hi" else "Shutting down in 10s.")
            time.sleep(2); os.system("shutdown /s /t 10")
        elif "restart" in query:
            speak("Restart ho raha hai." if current_lang[0]=="hi" else "Restarting.")
            time.sleep(2); os.system("shutdown /r /t 10")
        elif "sleep" in query:
            speak("Sleep mode." if current_lang[0]=="hi" else "Going to sleep.")
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        elif "lock" in query or "lock karo" in query:
            speak("Lock kar raha hoon." if current_lang[0]=="hi" else "Locking.")
            def do_lock(): time.sleep(1.5); ctypes.windll.user32.LockWorkStation()
            threading.Thread(target=do_lock,daemon=False).start()
        else: speak("Samajh nahi aaya." if current_lang[0]=="hi" else "Command not recognized.")
    except Exception as e: print(e)

def get_time():
    n=datetime.datetime.now()
    if current_lang[0]=="hi": speak(f"Abhi {n.strftime('%I')}:{n.strftime('%M')} {n.strftime('%p')} hue hain.")
    else: speak(f"It's {n.strftime('%I')}:{n.strftime('%M')} {n.strftime('%p')}.")

def get_date():
    n=datetime.datetime.now()
    days=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    months=["January","February","March","April","May","June","July","August","September","October","November","December"]
    if current_lang[0]=="hi": speak(f"Aaj {days[n.weekday()]} hai, {n.day} {months[n.month-1]} {n.year}.")
    else: speak(f"Today is {days[n.weekday()]}, {n.day} {months[n.month-1]} {n.year}.")

def get_weather(city="Kanpur"):
    try:
        data=requests.get(f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric",timeout=5).json()
        if data["cod"]==200:
            if current_lang[0]=="hi": speak(f"{city} mein {data['main']['temp']} degree hai, {data['weather'][0]['description']}.")
            else: speak(f"{city}: {data['main']['temp']}°C, {data['weather'][0]['description']}, humidity {data['main']['humidity']}%.")
        else: speak(f"{city} nahi mila." if current_lang[0]=="hi" else f"{city} not found.")
    except: speak("Weather nahi mila." if current_lang[0]=="hi" else "Weather unavailable.")

def search_wikipedia(query):
    try:
        wikipedia.set_lang("en")
        results=wikipedia.search(query,results=1)
        if not results: speak("Kuch nahi mila." if current_lang[0]=="hi" else "Nothing found."); return
        speak('. '.join(wikipedia.page(results[0]).summary.split('. ')[:2])+'.')
    except wikipedia.exceptions.DisambiguationError as e:
        try: speak('. '.join(wikipedia.page(e.options[0]).summary.split('. ')[:2])+'.')
        except: speak("Thoda clear batao." if current_lang[0]=="hi" else "Be more specific.")
    except: speak("Search fail." if current_lang[0]=="hi" else "Search failed.")

def open_app(query):
    apps={
        "youtube":("YouTube","https://www.youtube.com","web"),
        "google":("Google","https://www.google.com","web"),
        "whatsapp":("WhatsApp","https://web.whatsapp.com","web"),
        "github":("GitHub","https://www.github.com","web"),
        "notepad":("Notepad","notepad.exe","app"),
        "calculator":("Calculator","calc.exe","app"),
        "explorer":("Explorer","explorer.exe","app"),
        "chatgpt":("ChatGPT","https://chat.openai.com","web"),
        "maps":("Google Maps","https://maps.google.com","web"),
    }
    for key,(name,target,t) in apps.items():
        if key in query:
            speak(f"{name} khol raha hoon." if current_lang[0]=="hi" else f"Opening {name}.")
            webbrowser.open(target) if t=="web" else os.system(target); return
    speak("App nahi mila." if current_lang[0]=="hi" else "App not found.")

def greet():
    h=datetime.datetime.now().hour; nm=memory.get("name","Shiva")
    if current_lang[0]=="hi":
        if 5<=h<12: speak(f"Good morning sir! RJ taiyaar hai.")
        elif 12<=h<17: speak(f"Namaste sir! Kya kaam hai?")
        elif 17<=h<21: speak(f"Good evening sir! Batao kya karna hai.")
        else: speak(f"Haan sir, RJ hazir hai.")
    else:
        if 5<=h<12: speak(f"Good morning sir! RJ is ready.")
        elif 12<=h<17: speak(f"Hey sir! What can I do for you?")
        elif 17<=h<21: speak(f"Good evening sir! How can I help?")
        else: speak(f"Hey sir, RJ here.")

# ── NORMALIZE QUERY (Hindi → English keywords) ──
def normalize_query(q):
    replacements={
        "गूगल":"google","यूट्यूब":"youtube","व्हाट्सएप":"whatsapp",
        "नोटपैड":"notepad","कैलकुलेटर":"calculator","चैटजीपीटी":"chatgpt",
        "खोलो":"open","खोल":"open","ओपन":"open","चलाओ":"open","चला":"open",
        "बंद करो":"shutdown","लॉक करो":"lock","लॉक":"lock","रीस्टार्ट":"restart",
        "समय":"time","बजे":"alarm","कितने बजे":"time","वक्त":"time",
        "मौसम":"weather","तापमान":"weather","गर्मी":"weather",
        "खबर":"news","खबरें":"news","समाचार":"news",
        "स्क्रीनशॉट":"screenshot","तस्वीर":"screenshot",
        "मजाक":"joke","हंसाओ":"joke","चुटकुला":"joke",
        "अलार्म":"alarm","अलार्म लगाओ":"alarm",
        "याद दिलाओ":"remind","याद":"remind",
        "बैटरी":"battery","रैम":"ram","सीपीयू":"cpu",
        "वॉल्यूम":"volume","आवाज":"volume",
        "ब्राइटनेस":"brightness","रोशनी":"brightness",
        "नींद":"sleep","सो जाओ":"sleep",
    }
    for hindi,english in replacements.items():
        q=q.replace(hindi,english)
    return q

# ── COMMAND PROCESSOR (single, correct version) ──
def process_command(query):
    if not query: return True
    query=normalize_query(query)

    if "hindi mode" in query or "hindi mein" in query or "switch to hindi" in query:
        toggle_language(); return True
    if "english mode" in query or "switch to english" in query or "angrezi" in query:
        if current_lang[0]=="hi": toggle_language()
        return True
    if "happy mode" in query or "khush" in query or "fun mode" in query:
        set_mood("happy"); return True
    if "serious mode" in query or "serious" in query:
        set_mood("serious"); return True
    if "briefing" in query or "morning report" in query or "daily update" in query:
        threading.Thread(target=give_briefing,daemon=True).start(); return True
    if "kisne banaya" in query or "tumhe kisne banaya" in query or "who made you" in query or "who created you" in query:
        speak("Mujhe Shiva sir ne banaya hai!" if current_lang[0]=="hi" else "I was created by Shiva sir!")
    return True
    if   "time" in query or "kitne baje" in query or "samay" in query: get_time()
    elif "date" in query or "today" in query or "aaj" in query or "din" in query: get_date()
    elif "weather" in query or "temperature" in query or "mausam" in query:
        skip={"weather","temperature","mausam","in","of","the","what","is","tell","me","whats","kaisa","hai","aaj","batao","kanpur"}
        words=[w for w in query.split() if w not in skip and len(w)>2]
        city=words[0].capitalize() if words else "Kanpur"
        get_weather(city)
    elif "news" in query or "headline" in query or "khabar" in query or "samachar" in query:
        skip={"news","headline","headlines","latest","tell","me","about","what","is","the","today","give","top","khabar","khabrein","batao","aaj","ki","samachar"}
        topic=" ".join(w for w in query.split() if w not in skip).strip()
        get_news(topic if topic else None)
    elif "wikipedia" in query or "who is" in query or "tell me about" in query or "kaun hai" in query:
        q=query.replace("wikipedia","").replace("who is","").replace("what is","").replace("tell me about","").replace("kaun hai","").replace("kya hai","").strip()
        search_wikipedia(q) if q else speak("Kya dhundhu?" if current_lang[0]=="hi" else "What to search?")
    elif "send email" in query or "email" in query: handle_email()
    elif "whatsapp" in query or ("message" in query and "alarm" not in query): handle_whatsapp()
    elif "screenshot" in query: threading.Thread(target=take_screenshot,daemon=True).start()
    elif "battery" in query or "ram" in query or "cpu" in query or "system status" in query or "pc stats" in query: get_pc_stats()
    elif "type" in query or "likho" in query: auto_type(query)
    elif "organize" in query or "sort files" in query: organize_files(query)
    elif "remember" in query or "yaad rakho" in query or "note" in query: remember_something(query)
    elif "my notes" in query or "recall" in query or "kya yaad" in query: recall_notes()
    elif "open" in query or "launch" in query or "kholo" in query or "chalaao" in query: open_app(query)
    elif "search" in query or "find" in query or "dhundho" in query:
        q=query.replace("search","").replace("find","").replace("dhundho","").strip()
        if q: speak(f"Search kar raha hoon." if current_lang[0]=="hi" else "Searching."); webbrowser.open(f"https://www.google.com/search?q={q}")
        else: speak("Kya dhundhu?" if current_lang[0]=="hi" else "What to search?")
    elif "joke" in query or "funny" in query or "hasao" in query or "chutkula" in query: tell_joke()
    elif "alarm" in query: set_alarm(query)
    elif "remind" in query or "yaad dilao" in query: set_reminder(query)
    elif any(w in query for w in ["volume","brightness","shutdown","restart","sleep","lock","mute","unmute","band karo","lock karo"]):
        system_control(query)
    elif any(w in query for w in ["bye","exit","quit","goodbye","alvida"]):
        speak("Alvida! RJ ja raha hai." if current_lang[0]=="hi" else "Goodbye! RJ signing off.")
        return False
    else:
        speak(ask_groq(query))
    return True

def assistant_loop():
    greet()
    root.after(0,lambda:set_status("READY"))
    while is_running[0]:
        try:
            if wake_var.get():
                if not listen_for_wake_word(): continue
                speak(random.choice(["Haan!","Boliye!","Ji?"]) if current_lang[0]=="hi" else random.choice(["Yeah?","How can I help?","I'm listening!"]))
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
