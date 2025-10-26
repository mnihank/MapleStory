import tkinter as tk
from pynput import mouse
import pyautogui
import threading
import signal
import sys
import time
import ast
import keyboard
import pytesseract
import re
# 建立主視窗
window = tk.Tk()
window.title("功能設定")
window.geometry("400x300")

win_width=800
win_height=400


global a,a2,b,b2
global n,n1,listener,clicks,upper_left,upper_right,recordlist,upper_left2,upper_right2
n,n1=0,0
a,a2,b,b2=0,0,0,0
clicks,recordlist = [],[]

upper_left,upper_right,upper_left2,upper_right2=[],[],[],[]

# ----------- 安全關閉處理 -----------
def cleanup():
    global listener
    print("\n正在關閉程式...")
    if listener is not None:
        listener.stop()
        listener = None
    window.destroy()
    sys.exit(0)

def global_key_monitor():
    keyboard.add_hotkey('ctrl+c', cleanup)  # 全域攔截 Ctrl+C
    keyboard.add_hotkey('ctrl+r', record)
    keyboard.wait()  # 阻塞在此直到程式被結束


class Mouse:
    def __init__(self):
        pass
    def on_click(x, y, Button,pressed):
        global listener,clicks
        if pressed:
            clicks.append((x, y))
            # print(f"Clicked at: {x}, {y}")

            if btn4.cget("bg") == "yellow":
                recordlist.append(clicks[len(clicks)-1])
    # 啟動滑鼠監聽（放到子執行緒中）
    def start_mouse_listener():
        global listener
        listener = mouse.Listener(on_click = Mouse.on_click)
        listener.start()
            

# ------------------------------------------飛好友設定
def logic():
    with open("data.txt", "r", encoding="utf-8") as f:
        content = f.read().strip()
        data = ast.literal_eval(content)
        a = [num for pair in data for num in pair]
    while 1:
        if keyboard.is_pressed('ctrl+c'):
            print("偵測到 Ctrl+C，全域中止。")
            break

        pyautogui.moveTo(a[0], a[1], duration=0.3)
        pyautogui.click()
        pyautogui.moveTo(a[2], a[3], duration=0.3)
        pyautogui.click()
        pyautogui.moveTo(a[4], a[5], duration=0.3)
        pyautogui.click()
        time.sleep(3)
        pyautogui.moveTo(a[6], a[7], duration=0.3)
        pyautogui.click()
        time.sleep(3)
# ------------------------------------------紀錄動作
def record():
    global recordlist
    path = 'data.txt'
    f = open(path, 'w')
    f.write(str(recordlist))
    recordlist=[]
    f.close()

# ------------------------------------------自動補水
 # 指定 tesseract 的路徑（Windows 安裝後需設定）
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
def auto():
    global a,a2,b,b2
    try:
        region = (upper_left[0],upper_left[1],abs(upper_left[0]-upper_right[0]),abs(upper_left[1]-upper_right[1]))
        region2 = (upper_left2[0],upper_left2[1],abs(upper_left2[0]-upper_right2[0]),abs(upper_left2[1]-upper_right2[1]))
        # print("region = ", region)
        screenshot = pyautogui.screenshot(region=region)
        screenshot2 = pyautogui.screenshot(region=region2)
        # --- OCR 設定：只辨識數字與基本符號 ---
        custom_config = r'--psm 6 -c tessedit_char_whitelist=0123456789+-*/()='
        # OCR 辨識
        text = pytesseract.image_to_string(screenshot, config=custom_config)
        text2 = pytesseract.image_to_string(screenshot2, config=custom_config)
        # print("text =",text)
        nums = re.findall(r'\d+(?:,\d+)*', text)
        nums2 = re.findall(r'\d+(?:,\d+)*', text2)
        # print(nums)
        a, b = [int(n.replace(",", "")) for n in nums]
        a2, b2 = [int(n.replace(",", "")) for n in nums2]
        # print(a,b)
        if (a < b*0.5):
            pyautogui.press('delete')
        if (a2 < b2*0.2):
            pyautogui.press('end')
    except Exception as err:
        print(str(err))


# 切換顏色的共用函式
button_states = {}
def toggle_button_color(btn):
    current_state = button_states.get(btn, False)
    if current_state:
        btn.config(bg="SystemButtonFace")  # 回到原色
    else:
        btn.config(bg="yellow")            # 改成黃色
    button_states[btn] = not current_state

# 各按鈕功能加上顏色切換
def show_message(btn):
    global clicks,upper_left,upper_right,upper_left2,upper_right2
    toggle_button_color(btn)
    if btn1.cget("bg") == "yellow":
        threading.Thread(target=logic, daemon=True).start()
        print('開始連線')
    if btn2.cget("bg") == "yellow":
        upper_left = clicks[-2]
        clicks=[]
        print('upper_left',upper_left)
    if btn3.cget("bg") == "yellow":
        upper_right = clicks[-2]
        clicks=[]
        print('upper_right',upper_right)
    if btn4.cget("bg") == "yellow":
        print('開始記錄')
    if btn6.cget("bg") == "yellow":
        upper_left2 = clicks[-2]
        clicks=[]
        print('開始記錄')
    if btn7.cget("bg") == "yellow":
        upper_right2 = clicks[-2]
        clicks=[]
        print('開始記錄')
        

btn1 = tk.Button(window, text="連線",width=10, height=1, command=lambda: show_message(btn1))
btn1.place(x=win_width*0.1-80,y=win_height*0.1)
btn4 = tk.Button(window, text="紀錄",width=10, height=1, command=lambda: show_message(btn4))
btn4.place(x=win_width*0.1-80,y=win_height*0.1-30)
lb4_text = tk.Label(window, bg="#000000", fg='white', 
               text=f'record={recordlist}', font=('微軟正黑體', 8), 
               padx=0, pady=0)
lb4_text.place(x=win_width*0.1,y=win_height*0.1-30)

#--------------------------------------
btn2 = tk.Button(window, text="左上",width=10, height=1, command=lambda: show_message(btn2))
btn2.place(x=win_width*0.1-80,y=win_height*0.3)
lbl_text = tk.Label(window, bg="#000000", fg='white', 
               text=f'upper_left={upper_left}', font=('微軟正黑體', 8), 
               padx=0, pady=0)
lbl_text.place(x=win_width*0.1-80,y=win_height*0.37)
#--------------------------------------
btn3 = tk.Button(window, text="右下",width=10, height=1, command=lambda: show_message(btn3))
btn3.place(x=win_width*0.1-80,y=win_height*0.5)
lb2_text = tk.Label(window, bg="#000000", fg='white', 
               text=f'upper_right={upper_right}', font=('微軟正黑體', 8), 
               padx=0, pady=0)
lb2_text.place(x=win_width*0.1-80,y=win_height*0.57)


#--------------------------------------
btn6 = tk.Button(window, text="左上",width=10, height=1, command=lambda: show_message(btn6))
btn6.place(x=win_width*0.3-80,y=win_height*0.3)
lb6_text = tk.Label(window, bg="#000000", fg='white', 
               text=f'upper_left2={upper_left}', font=('微軟正黑體', 8), 
               padx=0, pady=0)
lb6_text.place(x=win_width*0.3-80,y=win_height*0.37)
#--------------------------------------
btn7 = tk.Button(window, text="右下",width=10, height=1, command=lambda: show_message(btn7))
btn7.place(x=win_width*0.3-80,y=win_height*0.5)
lb7_text = tk.Label(window, bg="#000000", fg='white', 
               text=f'upper_right2={upper_right}', font=('微軟正黑體', 8), 
               padx=0, pady=0)
lb7_text.place(x=win_width*0.3-80,y=win_height*0.57)





btn5 = tk.Button(window, text="自動補水",width=10, height=1, command=lambda: show_message(btn5))
btn5.place(x=win_width*0.3+50,y=win_height*0.5)
lb5_text = tk.Label(window, bg="#000000", fg='white', 
               text=f'HP/MP={0}', font=('微軟正黑體', 8), 
               padx=0, pady=0)
lb5_text.place(x=win_width*0.3+50,y=win_height*0.57)



if n!=1:
    threading.Thread(target=Mouse.start_mouse_listener, daemon=True).start()
    print("n = ",n)
    n=1

if n1!=1:
    threading.Thread(target=global_key_monitor, daemon=True).start()
    print("n1 = ",n1)
    n1=1


def my_loop():
    global clicks,recordlist
    # print(clicks)
    if len(clicks)>100:
        clicks=[]

    if btn5.cget("bg") == "yellow":
        auto()



    lbl_text.config(text=f'upper_left={upper_left}')
    lb2_text.config(text=f'upper_right={upper_right}')
    lb6_text.config(text=f'upper_left2={upper_left2}')
    lb7_text.config(text=f'upper_right2={upper_right2}')
    lb4_text.config(text=f'record={recordlist}')
    lb5_text.config(text=f'HP={a}/{b} \n MP={a2}/{b2}')
    window.after(200, my_loop)  # 1秒後再呼叫自己






# 啟動循環
my_loop()
window.protocol("WM_DELETE_WINDOW", cleanup)
window.mainloop()