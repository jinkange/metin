import cv2
import pyautogui
import keyboard
import threading
import time
import os
import numpy as np
from PIL import ImageGrab
import pygetwindow as gw
import pyautogui
import ctypes
import time

def find_metin_window():
    windows = gw.getWindowsWithTitle("Metin") or gw.getWindowsWithTitle("METIN")
    if not windows:
        print("Metin 창을 찾을 수 없습니다.")
        return None
    win = windows[0]
    if win.isMinimized:
        win.restore()
    return win


def move_mouse_to_window_center_partial():
    
    windows = gw.getWindowsWithTitle("Metin")
    if not windows:
        windows = gw.getWindowsWithTitle("METIN")
    
    if not windows:
        print(f"창을 찾을 수 없습니다.")
        return

    # 가장 먼저 찾은 창 사용
    win = windows[0]

    # 최소화 되어 있으면 복원
    if hasattr(win, 'isMinimized') and win.isMinimized:
        win.restore()

    # 중앙 좌표 계산
    center_x = win.left + win.width // 2
    center_y = win.top + win.height // 2

    # 마우스 이동
    pyautogui.moveTo(center_x, center_y, duration=0.2)

# 이미지 폴더 경로
IMAGE_FOLDER = './image'

# 탐색 조건
MATCH_THRESHOLD = 0.85
running = False
def find_metin_window():
    windows = gw.getWindowsWithTitle("Metin")
    if not windows:
        windows = gw.getWindowsWithTitle("METIN")
    if not windows:
        print("Metin 창을 찾을 수 없습니다.")
        return None
    win = windows[0]
    if hasattr(win, 'isMinimized') and win.isMinimized:
        win.restore()
    return win
def press_key_3():
    KEYEVENTF_KEYUP = 0x0002
    MapVirtualKey = ctypes.windll.user32.MapVirtualKeyW
    # 가상 키코드 (VK_4 = 0x34)
    vk = 0x33  
    scan_code = MapVirtualKey(vk, 0)
    # 눌림
    ctypes.windll.user32.keybd_event(vk, scan_code, 0, 0)
    time.sleep(0.05)
    # 뗌
    ctypes.windll.user32.keybd_event(vk, scan_code, KEYEVENTF_KEYUP, 0)


def find_and_move():
    global running

    while True:
        if running:
            win = find_metin_window()
            if not win:
                time.sleep(1)
                continue

            bbox = (win.left, win.top, win.left + win.width, win.top + win.height)
            screenshot = ImageGrab.grab(bbox=bbox)            
            # 스크린샷 찍고 numpy로 변환
            # screenshot = ImageGrab.grab()
            screenshot_np = np.array(screenshot)
            screenshot_bgr = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)

            img_path = os.path.join(IMAGE_FOLDER, f'check.png')
            if os.path.exists(img_path):
                template = cv2.imread(img_path, cv2.IMREAD_COLOR)
                h, w = template.shape[:2]
                result = cv2.matchTemplate(screenshot_bgr, template, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, max_loc = cv2.minMaxLoc(result)
                if max_val <= MATCH_THRESHOLD:
                    press_key_3()

            found = False
            # 1.png ~ 6.png 반복 탐색
            for i in range(1, 11):
                img_path = os.path.join(IMAGE_FOLDER, f'{i}.png')
                if not os.path.exists(img_path):
                    continue

                template = cv2.imread(img_path, cv2.IMREAD_COLOR)
                h, w = template.shape[:2]
                result = cv2.matchTemplate(screenshot_bgr, template, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, max_loc = cv2.minMaxLoc(result)
                print(f"[{i}.png] 찾기 :({max_val})")
                if max_val >= MATCH_THRESHOLD:
                    center_x = max_loc[0] + w // 2
                    center_y = max_loc[1] + h // 2
                    pyautogui.moveTo(center_x, center_y, duration=0.1)
                    print(f"[{i}.png] 매칭됨 → 마우스 이동 ({center_x}, {center_y})")
                    time.sleep(0.2)
                    found = True
                    continue
            if not found:
                move_mouse_to_window_center_partial()
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

if __name__ == '__main__':
    print("■ 프로그램 시작 (F1: 시작, F2: 정지, ESC: 종료)")
    threading.Thread(target=find_and_move, daemon=True).start()
    threading.Thread(target=hotkey_listener, daemon=True).start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("종료됨")
    
