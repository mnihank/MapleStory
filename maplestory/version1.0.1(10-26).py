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
##參數設定
global var1,var2,var3
global str1,str2
var1 = 200 #每幾秒補一次藥水 (1000為1秒)
str1 = "ctrl+esc" #強制關閉程式
str2 = "ctrl+r" #飛好友紀錄滑鼠點的位置(目前只能按四下)
var2 = 0.7 #HP在幾成以下開始喝藥水
var3 = 0.2 #MP在幾成以下開始喝藥水
str3 = "delete" #HP藥水按鍵
str4 = "end" #MP藥水按鍵




# 建立主視窗
window = tk.Tk()
window.title("功能設定")
window.geometry("400x300")

win_width=800
win_height=400


global a,a2,b,b2,n2
global n,n1,listener,clicks,upper_left,upper_right,recordlist,upper_left2,upper_right2
n,n1,n2=0,0,0
a,a2,b,b2=0,0,0,0
clicks,recordlist = [],[]
try:
    with open("HPMPaxis.txt", "r", encoding="utf-8") as f:
        content = f.read().strip()
        data = ast.literal_eval(content)
        a3 = [num for pair in data for num in pair]
        upper_left=[a3[0],a3[1]]
        upper_right=[a3[2],a3[3]]
        upper_left2=[a3[4],a3[5]]
        upper_right2=[a3[6],a3[7]]

except Exception as err:
    upper_left,upper_right,upper_left2,upper_right2=[],[],[],[]
    # print(str(err))

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
    global str1,str2
    keyboard.add_hotkey(str1, cleanup)  # 全域攔截 Ctrl+C
    keyboard.add_hotkey(str2, record)
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
    global a,a2,b,b2,n2,str3,str4,var2,var3
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
        if (a < b*var2):
            pyautogui.press(str3)
        if (a2 < b2*var3):
            pyautogui.press(str4)

        if n2==0:
            path = 'HPMPaxis.txt'
            f = open(path, 'w')
            new = [upper_left,upper_right,upper_left2,upper_right2]
            f.write(str(new))
            f.close()
            n2=1
        
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
    global clicks,upper_left,upper_right,upper_left2,upper_right2,n2
    toggle_button_color(btn)
    if btn1.cget("bg") == "yellow":
        threading.Thread(target=logic, daemon=True).start()
        print('開始連線')
    if btn4.cget("bg") == "yellow":
        print('開始記錄')
    if btn5.cget("bg") == "yellow":
        n2=0

def recordaxis(btn):   
    global clicks,upper_left,upper_right,upper_left2,upper_right2
    if btn==btn2:
        upper_left = clicks[-2]
        clicks=[]
    elif btn==btn3:
        upper_right = clicks[-2]
        clicks=[]
    elif btn==btn6:
        upper_left2 = clicks[-2]
        clicks=[]
    elif btn==btn7:
        upper_right2 = clicks[-2]
        clicks=[]
    pass

btn1 = tk.Button(window, text="連線",width=10, height=1, command=lambda: show_message(btn1))
btn1.place(x=win_width*0.1-80,y=win_height*0.1)
btn4 = tk.Button(window, text="紀錄",width=10, height=1, command=lambda: show_message(btn4))
btn4.place(x=win_width*0.1-80,y=win_height*0.1-30)
lb4_text = tk.Label(window, bg="#000000", fg='white', 
               text=f'record={recordlist}', font=('微軟正黑體', 8), 
               padx=0, pady=0)
lb4_text.place(x=win_width*0.1,y=win_height*0.1-30)

#--------------------------------------
lb8_text = tk.Label(window, bg="#FF0000", fg='white', 
               text=f'HP', font=('微軟正黑體', 15), 
               padx=0, pady=0)
lb8_text.place(x=win_width*0.1-80,y=win_height*0.2)
btn2 = tk.Button(window, text="左上",width=10, height=1, command=lambda: recordaxis(btn2))
btn2.place(x=win_width*0.1-80,y=win_height*0.3)
lbl_text = tk.Label(window, bg="#000000", fg='white', 
               text=f'{upper_left}', font=('微軟正黑體', 8), 
               padx=0, pady=0)
lbl_text.place(x=win_width*0.1-80,y=win_height*0.37)
#--------------------------------------
btn3 = tk.Button(window, text="右下",width=10, height=1, command=lambda: recordaxis(btn3))
btn3.place(x=win_width*0.1-80,y=win_height*0.5)
lb2_text = tk.Label(window, bg="#000000", fg='white', 
               text=f'{upper_right}', font=('微軟正黑體', 8), 
               padx=0, pady=0)
lb2_text.place(x=win_width*0.1-80,y=win_height*0.57)


#--------------------------------------
lb9_text = tk.Label(window, bg="#001AFF", fg='white', 
               text=f'MP', font=('微軟正黑體', 15), 
               padx=0, pady=0)
lb9_text.place(x=win_width*0.3-80,y=win_height*0.2)
btn6 = tk.Button(window, text="左上",width=10, height=1, command=lambda: recordaxis(btn6))
btn6.place(x=win_width*0.3-80,y=win_height*0.3)
lb6_text = tk.Label(window, bg="#000000", fg='white', 
               text=f'{upper_left}', font=('微軟正黑體', 8), 
               padx=0, pady=0)
lb6_text.place(x=win_width*0.3-80,y=win_height*0.37)
#--------------------------------------
btn7 = tk.Button(window, text="右下",width=10, height=1, command=lambda: recordaxis(btn7))
btn7.place(x=win_width*0.3-80,y=win_height*0.5)
lb7_text = tk.Label(window, bg="#000000", fg='white', 
               text=f'{upper_right}', font=('微軟正黑體', 8), 
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
    global clicks,recordlist,var1
    # print(clicks)
    if len(clicks)>100:
        clicks=[]

    if btn5.cget("bg") == "yellow":
        auto()



    lbl_text.config(text=f'{upper_left}')
    lb2_text.config(text=f'{upper_right}')
    lb6_text.config(text=f'{upper_left2}')
    lb7_text.config(text=f'{upper_right2}')
    lb4_text.config(text=f'record={len(recordlist)}')
    lb5_text.config(text=f'HP={a}/{b}\nMP={a2}/{b2}')
    window.after(var1, my_loop)  # 1秒後再呼叫自己






# 啟動循環
my_loop()
window.protocol("WM_DELETE_WINDOW", cleanup)
window.mainloop()