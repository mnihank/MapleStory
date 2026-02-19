import tkinter as tk
from tkinter import messagebox
import keyboard
import time
import threading
import json
import os

# ======================
# 1. 核心數據與存檔管理
# ======================
SAVE_FILE = "macro_pro_config.json"

def get_default_settings():
    return {
        "slots": [{"name": "巨集 1", "events": []}, {"name": "巨集 2", "events": []}],
        "timers": [{"key": "q", "seconds": "10", "avoid": True}],
        "timer_gap": "100",
        "show_timer_zone": True,
        "timer_active": True,
        "slot_count": 2,
        "window_size": "480x600"
    }

def load_settings():
    settings = get_default_settings()
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                settings.update(data)
                while len(settings["slots"]) < settings["slot_count"]:
                    settings["slots"].append({"name": f"分組 {len(settings['slots'])+1}", "events": []})
        except: pass
    return settings

macro_data = load_settings()
recording, playing, last_action_time = False, False, 0 
MOVE_KEYS = {'up', 'down', 'left', 'right'}
all_entries = []
macro_frames = [] # 儲存每一組的 Frame 以便動態改變顏色

def save_to_file():
    try: macro_data["window_size"] = root.geometry().split('+')[0]
    except: pass
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(macro_data, f, ensure_ascii=False, indent=4)

# ======================
# 2. 核心邏輯 (加入視覺變化)
# ======================

def safe_press(key_str):
    if not key_str.strip(): return
    k = key_str.strip().lower()
    try:
        sc = keyboard.key_to_scan_codes(k)[0]
        keyboard.press(sc); time.sleep(0.03); keyboard.release(sc)
    except: keyboard.press_and_release(k)

def run_macro(idx, repeat_val, btn_play):
    global playing, last_action_time
    if playing: 
        playing = False
        return

    events = macro_data["slots"][idx]["events"]
    if not events: return

    playing = True
    # 視覺反饋：變更當前 Frame 顏色
    macro_frames[idx].config(bg="#e8f5e9") # 淺綠色背景
    btn_play.config(text="■ 停止", bg="#e57373", fg="white")
    status_label.config(text=f"▶ 正在執行：{macro_data['slots'][idx]['name']}", fg="#2e7d32")
    set_ui_state("disabled")
    
    repeat_count = int(repeat_val) if repeat_val.isdigit() else None
    
    def macro_loop():
        global playing, last_action_time
        count = 0
        last_trigger_times = [time.time()] * len(macro_data["timers"])
        while playing:
            last_event_time = 0
            for e in events:
                if not playing: break
                time.sleep(max(0, e["time"] - last_event_time))
                k = e["key"].lower()
                if k not in MOVE_KEYS: last_action_time = time.time()
                try:
                    sc = keyboard.key_to_scan_codes(k)[0]
                    if e["type"] == "down": keyboard.press(sc)
                    else: keyboard.release(sc)
                except:
                    if e["type"] == "down": keyboard.press(k)
                    else: keyboard.release(k)
                last_event_time = e["time"]

            count += 1
            if repeat_count and count >= repeat_count: break
            
            if macro_data.get("timer_active") and playing:
                now = time.time()
                gap = int(macro_data["timer_gap"]) / 1000.0
                for i, t in enumerate(macro_data["timers"]):
                    if not playing: break
                    try:
                        if now - last_trigger_times[i] >= float(t["seconds"]):
                            if t.get("avoid"):
                                while playing and (time.time() - last_action_time < 0.3):
                                    time.sleep(0.05)
                            safe_press(t["key"])
                            last_trigger_times[i] = time.time()
                            time.sleep(gap)
                    except: continue
            if not events: time.sleep(0.1)

        playing = False
        root.after(0, lambda: reset_ui_after_play(idx, btn_play))

    threading.Thread(target=macro_loop, daemon=True).start()

# ======================
# 3. UI 輔助函式
# ======================

def set_ui_state(state):
    for ent in all_entries:
        try: ent.config(state=state)
        except: pass

def reset_ui_after_play(idx, btn):
    macro_frames[idx].config(bg="SystemButtonFace")
    btn.config(text="播 放", bg="#f1f8e9", fg="black")
    set_ui_state("normal")
    status_label.config(text="準備就緒", fg="blue")

def start_rec(idx, btn_stop, frame):
    global recording, start_time
    if recording or playing: return
    
    # 視覺反饋：變更為錄製模式顏色
    frame.config(bg="#ffebee") # 淺紅色背景
    btn_stop.config(bg="#d32f2f", fg="white", text="● 停止錄製")
    status_label.config(text=f"🔴 正在錄製：{macro_data['slots'][idx]['name']} (結束請按停止)", fg="red")
    
    set_ui_state("disabled")
    macro_data["slots"][idx]["events"] = []
    recording, start_time = True, time.time()
    
    keyboard.hook(lambda e: macro_data["slots"][idx]["events"].append({
        "key": e.name, "type": e.event_type, "time": round(time.time() - start_time, 4)
    }) if recording else None)

def stop_rec(idx, btn_stop, frame):
    global recording
    if not recording: return
    recording = False
    keyboard.unhook_all()
    keyboard.hook(global_action_monitor)
    
    # 恢復顏色
    frame.config(bg="SystemButtonFace")
    btn_stop.config(bg="SystemButtonFace", fg="black", text="停止")
    set_ui_state("normal")
    save_to_file()
    status_label.config(text="錄製已儲存", fg="blue")

def move_slot(idx, direction):
    if playing or recording: return
    new_idx = idx + direction
    if 0 <= new_idx < len(macro_data["slots"]):
        macro_data["slots"][idx], macro_data["slots"][new_idx] = \
            macro_data["slots"][new_idx], macro_data["slots"][idx]
        save_to_file()
        rebuild_ui()

# ======================
# 4. 主介面建構
# ======================
root = tk.Tk()
root.title("Maple Story - UI")
root.attributes('-topmost', True)

def on_close():
    save_to_file()
    root.destroy()
root.protocol("WM_DELETE_WINDOW", on_close)

def rebuild_ui():
    global all_entries, btn_timer_switch, status_label, macro_frames
    for w in root.winfo_children(): 
        if w not in [top_bar]: w.destroy()
    
    all_entries = []
    macro_frames = []
    main_container = tk.Frame(root)
    main_container.pack(fill="both", expand=True)

    # 巨集區
    m_zone = tk.Frame(main_container)
    m_zone.pack(fill="x", padx=10, pady=5)
    
    for i in range(min(macro_data["slot_count"], len(macro_data["slots"]))):
        slot = macro_data["slots"][i]
        frame = tk.LabelFrame(m_zone, padx=5, pady=5, text=f" Slot {i+1} ")
        frame.pack(fill="x", pady=5)
        macro_frames.append(frame)
        
        row1 = tk.Frame(frame); row1.pack(fill="x")
        tk.Button(row1, text="↑", width=2, font=("Arial", 7), command=lambda idx=i: move_slot(idx, -1)).pack(side=tk.LEFT)
        tk.Button(row1, text="↓", width=2, font=("Arial", 7), command=lambda idx=i: move_slot(idx, 1)).pack(side=tk.LEFT)
        
        name_var = tk.StringVar(value=slot["name"])
        name_var.trace_add("write", lambda *a, idx=i, v=name_var: [macro_data["slots"][idx].update({"name": v.get()}), save_to_file()])
        ent = tk.Entry(row1, textvariable=name_var, font=("微软雅黑", 9, "bold"), bd=1)
        ent.pack(side=tk.LEFT, padx=5, fill="x", expand=True); all_entries.append(ent)
        
        row2 = tk.Frame(frame); row2.pack(fill="x", pady=2)
        btn_stop = tk.Button(row2, text="停止", width=8) # 先定義以便傳入錄製函式
        btn_rec = tk.Button(row2, text="錄製", width=5, command=lambda idx=i, b=btn_stop, f=frame: start_rec(idx, b, f))
        btn_rec.pack(side=tk.LEFT)
        btn_stop.config(command=lambda idx=i, b=btn_stop, f=frame: stop_rec(idx, b, f))
        btn_stop.pack(side=tk.LEFT, padx=2)
        
        tk.Label(row2, text="| 循環:").pack(side=tk.LEFT)
        rep_e = tk.Entry(row2, width=4, justify="center"); rep_e.insert(0, "~"); rep_e.pack(side=tk.LEFT); all_entries.append(rep_e)
        
        btn_p = tk.Button(row2, text="播 放", width=10, bg="#f1f8e9", font=("微软雅黑", 9, "bold"))
        btn_p.config(command=lambda idx=i, e=rep_e, b=btn_p: run_macro(idx, e.get(), b))
        btn_p.pack(side=tk.RIGHT)

    # 定時區
    if macro_data.get("show_timer_zone"):
        t_zone = tk.LabelFrame(main_container, text=" 定時任務 (每一循環起點觸發) ", padx=10, pady=5)
        t_zone.pack(fill="x", padx=10, pady=5)
        # ... (定時區內容維持原樣)
        gap_f = tk.Frame(t_zone); gap_f.pack(fill="x")
        tk.Label(gap_f, text="觸發間隔(ms):").pack(side=tk.LEFT)
        gv = tk.StringVar(value=macro_data["timer_gap"])
        gv.trace_add("write", lambda *a, v=gv: [macro_data.update({"timer_gap": v.get()}), save_to_file()])
        ge = tk.Entry(gap_f, textvariable=gv, width=6); ge.pack(side=tk.LEFT); all_entries.append(ge)
        list_f = tk.Frame(t_zone); list_f.pack(fill="x", pady=5)
        for idx, t in enumerate(macro_data["timers"]):
            r = tk.Frame(list_f); r.pack(fill="x", pady=1)
            kv = tk.StringVar(value=t["key"])
            kv.trace_add("write", lambda *a, i=idx, v=kv: [macro_data["timers"][i].update({"key": v.get()}), save_to_file()])
            ke = tk.Entry(r, textvariable=kv, width=5); ke.pack(side=tk.LEFT); all_entries.append(ke)
            tk.Label(r, text=" 每").pack(side=tk.LEFT)
            sv = tk.StringVar(value=t["seconds"])
            sv.trace_add("write", lambda *a, i=idx, v=sv: [macro_data["timers"][i].update({"seconds": v.get()}), save_to_file()])
            se = tk.Entry(r, textvariable=sv, width=5); se.pack(side=tk.LEFT); all_entries.append(se)
            tk.Label(r, text=" 秒").pack(side=tk.LEFT)
            tk.Button(r, text="✕", fg="red", bd=0, command=lambda i=idx: [macro_data["timers"].pop(i), save_to_file(), rebuild_ui()]).pack(side=tk.RIGHT)

        btn_timer_switch = tk.Button(t_zone, command=toggle_timer_master); btn_timer_switch.pack(fill="x", pady=5)
        active = macro_data.get("timer_active")
        btn_timer_switch.config(text=f"定時任務：{'已啟用' if active else '已停用'}", bg="#ffecb3" if active else "#e3f2fd")
        tk.Button(t_zone, text="+ 新增定時", command=lambda: [macro_data["timers"].append({"key": "F1", "seconds": "60", "avoid": True}), save_to_file(), rebuild_ui()]).pack()

    status_label = tk.Label(root, text="準備就緒", fg="blue", relief="sunken", anchor="w")
    status_label.pack(fill="x", side=tk.BOTTOM)

def toggle_timer_master():
    macro_data["timer_active"] = not macro_data["timer_active"]
    save_to_file()
    active = macro_data.get("timer_active")
    btn_timer_switch.config(text=f"定時任務：{'已啟用' if active else '已停用'}", bg="#ffecb3" if active else "#e3f2fd")

def global_action_monitor(event):
    global last_action_time
    if event.event_type == 'down' and event.name.lower() not in MOVE_KEYS:
        last_action_time = time.time()

# 初始化
top_bar = tk.Frame(root); top_bar.pack(fill="x")
tk.Button(top_bar, text="介面設置", command=lambda: open_settings_win()).pack(side=tk.RIGHT, padx=10)

def open_settings_win():
    win = tk.Toplevel(root); win.title("設置"); win.attributes('-topmost', True)
    tk.Label(win, text="巨集數量:").pack()
    s = tk.Spinbox(win, from_=1, to=10, width=5); s.delete(0, "end"); s.insert(0, macro_data["slot_count"]); s.pack()
    v = tk.BooleanVar(value=macro_data["show_timer_zone"])
    tk.Checkbutton(win, text="顯示定時設定區", variable=v).pack()
    def apply():
        macro_data["slot_count"] = int(s.get()); macro_data["show_timer_zone"] = v.get()
        save_to_file(); win.destroy(); rebuild_ui()
    tk.Button(win, text="套用", command=apply).pack()

keyboard.hook(global_action_monitor)
root.geometry(macro_data.get("window_size", "480x500"))
rebuild_ui()
root.mainloop()
