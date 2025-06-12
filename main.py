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
def move_mouse_to_window_center_partial(title_prefix):
    # 제목에 title_prefix를 포함한 창들 모두 가져오기
    windows = gw.getWindowsWithTitle(title_prefix)

    if not windows:
        print(f"[오류] '{title_prefix}' 가 포함된 창을 찾을 수 없습니다.")
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
MATCH_THRESHOLD = 0.8
running = False

def find_and_move():
    global running
    while True:
        if running:
            # 스크린샷 가져오기 (PIL 사용 → numpy로 변환)
            screenshot = ImageGrab.grab()
            screenshot_np = np.array(screenshot)
            screenshot_bgr = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)

            # 1.png ~ 6.png 반복
            for i in range(1, 7):
                img_path = os.path.join(IMAGE_FOLDER, f'{i}.png')
                if not os.path.exists(img_path):
                    continue

                template = cv2.imread(img_path, cv2.IMREAD_COLOR)
                h, w = template.shape[:2]

                result = cv2.matchTemplate(screenshot_bgr, template, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, max_loc = cv2.minMaxLoc(result)
                print(f"[{i}.png] 매칭률 : {max_val}")
                if max_val >= MATCH_THRESHOLD:
                    center_x = max_loc[0] + w // 2
                    center_y = max_loc[1] + h // 2
                    pyautogui.moveTo(center_x, center_y, duration=0.2)
                    print(f"[{i}.png] 매칭됨 → 마우스 이동 ({center_x}, {center_y})")
                    time.sleep(1)
                    # 사용 예
                    move_mouse_to_window_center("Metin1")
                    continue  # 하나만 찾으면 멈춤

                time.sleep(0.4)
        else:
            time.sleep(0.2)

def hotkey_listener():
    keyboard.add_hotkey('F1', start)
    keyboard.add_hotkey('F2', stop)
    keyboard.wait()

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

if __name__ == '__main__':
    print("■ 이미지 탐색 시작 (F1), 정지(F2)")
    threading.Thread(target=find_and_move, daemon=True).start()
    hotkey_listener()
