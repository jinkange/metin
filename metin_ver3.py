import cv2
import pyautogui
import keyboard
import threading
import time
import os
import numpy as np
from PIL import ImageGrab
import pygetwindow as gw
import random
import ctypes

# 방향 정의
DIRECTIONS = {
    "up": (0, -80),
    "down": (0, 80),
    "left": (-80, 0),
    "right": (80, 0),
    "up_left": (-60, -60),
    "up_right": (60, -60),
    "down_left": (-60, 60),
    "down_right": (60, 60),
}

OPPOSITE = {
    "up": "down", "down": "up", "left": "right", "right": "left",
    "up_left": "down_right", "down_right": "up_left",
    "up_right": "down_left", "down_left": "up_right",
}

IMAGE_FOLDER = './image'
MATCH_THRESHOLD = 0.85
running = False
click_delay = 0.2
repeat_times = {6: 0, 7: 0, 8: 0, 9: 0}

# 숫자 키 누르기 함수 (ctypes 기반)
def press_key(vk):
    KEYEVENTF_KEYUP = 0x0002
    MapVirtualKey = ctypes.windll.user32.MapVirtualKeyW
    scan_code = MapVirtualKey(vk, 0)
    ctypes.windll.user32.keybd_event(vk, scan_code, 0, 0)
    time.sleep(0.05)
    ctypes.windll.user32.keybd_event(vk, scan_code, KEYEVENTF_KEYUP, 0)

# 숫자 키 지정 함수들
def press_key_0(): press_key(0x30)
def press_key_1(): press_key(0x31)
def press_key_2(): press_key(0x32)
def press_key_3(): press_key(0x33)
def press_key_4(): press_key(0x34)
def press_key_6(): press_key(0x36)
def press_key_7(): press_key(0x37)
def press_key_8(): press_key(0x38)
def press_key_9(): press_key(0x39)

def get_next_direction(prev_dir):
    exclude = {prev_dir, OPPOSITE[prev_dir]}
    available_dirs = [d for d in DIRECTIONS if d not in exclude]
    return random.choice(available_dirs)

def move_mouse_to_window_center_partial():
    windows = gw.getWindowsWithTitle("Metin") or gw.getWindowsWithTitle("METIN")
    if not windows:
        print("창을 찾을 수 없습니다.")
        return
    win = windows[0]
    if win.isMinimized:
        win.restore()
    center_x = win.left + win.width // 2
    center_y = win.top + win.height // 2
    pyautogui.moveTo(center_x, center_y, duration=0.2)

def find_metin_window():
    windows = gw.getWindowsWithTitle("Metin") or gw.getWindowsWithTitle("METIN")
    if not windows:
        print("Metin 창을 찾을 수 없습니다.")
        return None
    win = windows[0]
    if win.isMinimized:
        win.restore()
    return win

def find_and_move():
    global running, click_delay
    prev_dir = random.choice(list(DIRECTIONS))
    while True:
        if running:
            win = find_metin_window()
            if not win:
                time.sleep(1)
                continue


            bbox = (win.left, win.top, win.left + win.width, win.top + win.height)
            screenshot = ImageGrab.grab(bbox=bbox)
            
            screenshot_np = np.array(screenshot)
            screenshot_bgr = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)

            for j in range(1, 4):
                img_path = os.path.join(IMAGE_FOLDER, f'check{j}.png')
                if os.path.exists(img_path):
                    template = cv2.imread(img_path, cv2.IMREAD_COLOR)
                    h, w = template.shape[:2]
                    result = cv2.matchTemplate(screenshot_bgr, template, cv2.TM_CCOEFF_NORMED)
                    _, max_val, _, _ = cv2.minMaxLoc(result)
                    if max_val >= MATCH_THRESHOLD:
                        print(f"check{j}.png 감지됨 → {j}번 키 누름")
                        press_key(0x30 + j)  # 0x31 = 1, 0x32 = 2, 0x33 = 3
                        press_key(0x30 + j)  # 0x31 = 1, 0x32 = 2, 0x33 = 3

            found = False
            for i in range(1, 11):
                img_path = os.path.join(IMAGE_FOLDER, f'{i}.png')
                if not os.path.exists(img_path):
                    continue
                template = cv2.imread(img_path, cv2.IMREAD_COLOR)
                h, w = template.shape[:2]
                result = cv2.matchTemplate(screenshot_bgr, template, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, max_loc = cv2.minMaxLoc(result)
                if max_val >= MATCH_THRESHOLD:
                    center_x = max_loc[0] + w // 2
                    center_y = max_loc[1] + h // 2
                    pyautogui.moveTo(center_x+20, center_y-25, duration=0.1)
                    print(f"[{i}.png] 매칭됨 → 마우스 이동 ({center_x}, {center_y})")
                    press_key_4()
                    press_key_4()
                    time.sleep(click_delay)
                    found = True
            if not found:
                move_mouse_to_window_center_partial()
                print("몬스터 없음 → 0번 클릭")
                press_key_0()
                # prev_dir = get_next_direction(prev_dir)
                time.sleep(4)
        time.sleep(0.2)

def start():
    global running
    if not running:
        print("▶ 이미지 탐색 시작 (F2로 정지)")
        running = True

def stop():
    global running
    if running:
        print("■ 이미지 탐색 정지 (F1으로 재시작)")
        running = False

def hotkey_listener():
    keyboard.add_hotkey('F1', start)
    keyboard.add_hotkey('F2', stop)
    print("★ 핫키 리스너 실행 중 (F1=시작, F2=정지, ESC=종료)")
    keyboard.wait('esc')

def set_parameters():
    global click_delay, repeat_times
    try:
        click_delay_input = input("클릭 딜레이를 초단위로 입력하세요 (0.1 이상): ")
        click_delay = float(click_delay_input)
        if click_delay < 0.1:
            raise ValueError("딜레이는 0.1초 이상이어야 합니다.")
        for key in [6, 7, 8, 9]:
            t = input(f"숫자 {key}번 키를 누를 주기를 초 단위로 입력하세요 (0이면 비활성화): ")
            repeat_times[key] = float(t) if float(t) > 0 else 0
    except ValueError as e:
        print(f"입력 오류: {e}")
        exit(1)

def key_spammer(key, interval):
    while True:
        if running and interval > 0:
            press_key(0x30 + key)
        time.sleep(interval if interval > 0 else 1)

if __name__ == '__main__':
    print("■ 프로그램 시작 (F1: 시작, F2: 정지, ESC: 종료)")
    set_parameters()
    threading.Thread(target=find_and_move, daemon=True).start()
    for k in [6, 7, 8, 9]:
        threading.Thread(target=key_spammer, args=(k, repeat_times[k]), daemon=True).start()
    threading.Thread(target=hotkey_listener, daemon=True).start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("종료됨")
