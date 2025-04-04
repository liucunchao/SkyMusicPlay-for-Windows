import ctypes
import time

import keyboard
import pyautogui
import win32con
import win32gui

from windhide.static.global_variable import GlobalVariable
from windhide.thread.intel_play_thread import ControlledThread
from windhide.utils.path_util import convert_notes_to_delayed_format, convert_json_to_play

PostMessageW = ctypes.windll.user32.PostMessageW  # 消息队列
SendMessageW = ctypes.windll.user32.SendMessageW  # 立即处理
MapVirtualKeyW = ctypes.windll.user32.MapVirtualKeyW
VkKeyScanW = ctypes.windll.user32.VkKeyScanW
user32 = ctypes.windll.user32

WM_KEYDOWN = 0x100
WM_KEYUP = 0x101
pyautogui.FAILSAFE = False

def send_single_key_to_window_task(key, duration):
    """发送单个按键，减少延迟"""
    key_down(key)
    time.sleep(duration/1000 + GlobalVariable.duration)
    key_up(key)

def send_multiple_key_to_window_task(keys, duration):
    """发送组合按键，减少延迟"""
    for key in keys:
        key_down(key)
    time.sleep(duration/1000 + GlobalVariable.duration)
    for key in keys:
        key_up(key)

def send_single_key_to_window(key, duration):
    """发送单个按键（单线程）"""
    if GlobalVariable.compatibility_mode:
        send_single_key_to_window_follow(key, duration)
    else:
        send_single_key_to_window_task(key, duration)

def send_multiple_key_to_window(keys, duration):
    """发送组合按键（单线程）"""
    if GlobalVariable.compatibility_mode:
        send_multiple_key_to_window_follow(keys, duration)
    else:
        send_multiple_key_to_window_task(keys, duration)

def send_single_key_to_window_follow(key, duration):
    """发送单个按键，减少延迟（单线程）"""
    keyboard.press(key)
    time.sleep(duration/1000 + GlobalVariable.duration)
    keyboard.release(key)

def send_multiple_key_to_window_follow(keys, duration):
    """发送组合按键，减少延迟（单线程）"""
    for key in keys:
        keyboard.press(key)
    time.sleep(duration/1000 + GlobalVariable.duration)
    for key in keys:
        keyboard.release(key)

def playMusic(fileName, type):
    """优化音乐播放逻辑，只加载乐谱数据一次"""
    convert_notes_to_delayed_format(fileName, type)
    if GlobalVariable.thread is not None:
        stop()
    GlobalVariable.thread = ControlledThread()
    GlobalVariable.thread.start()

def playMusic_edit(text):
    """优化音乐播放逻辑，只加载乐谱数据一次"""
    convert_json_to_play(text)
    if GlobalVariable.thread is not None:
        stop()
    GlobalVariable.thread = ControlledThread()
    GlobalVariable.thread.start()

def resume():
    """恢复播放"""
    if GlobalVariable.thread:
        GlobalVariable.thread.resume()

def pause():
    """暂停播放"""
    if GlobalVariable.thread:
        GlobalVariable.thread.pause()

def stop():
    """停止播放"""
    if GlobalVariable.thread:
        GlobalVariable.thread.stop()
        GlobalVariable.set_progress = 0
        GlobalVariable.thread = None

# 点击，按下
def mouse_move_to(x: int, y: int):
    # 获取窗口的屏幕位置
    window_rect = win32gui.GetWindowRect(GlobalVariable.window["hWnd"])  # 返回 (left, top, right, bottom)
    window_x, window_y = window_rect[0], window_rect[1]
    client_x = window_x + x
    client_y = window_y + y
    if GlobalVariable.is_post_w:
        PostMessageW(GlobalVariable.window["hWnd"], win32con.WM_ACTIVATE, win32con.WA_ACTIVE, 0)
    else:
        SendMessageW(GlobalVariable.window["hWnd"], win32con.WM_ACTIVATE, win32con.WA_ACTIVE, 0)
    pyautogui.moveTo(client_x, client_y, duration=0)

# 核心
def key_press(key: str):
    key = key.lower()
    if key in special_keys:
        vk_code, scan_code = special_keys[key]
    else:
        # 普通按键的处理
        vk_code = VkKeyScanW(ctypes.c_wchar(key))
        scan_code = keyboard.key_to_scan_codes(key)[0] if key != '/' else keyboard.key_to_scan_codes(key)[1]
    lparam = (scan_code << 16) | 1
    if GlobalVariable.is_post_w:
        PostMessageW(GlobalVariable.window["hWnd"], win32con.WM_ACTIVATE, win32con.WA_ACTIVE, 0)
        PostMessageW(GlobalVariable.window["hWnd"], WM_KEYDOWN, vk_code, lparam)
        time.sleep(0.01)
        PostMessageW(GlobalVariable.window["hWnd"], WM_KEYUP, vk_code, lparam)
    else:
        SendMessageW(GlobalVariable.window["hWnd"], win32con.WM_ACTIVATE, win32con.WA_ACTIVE, 0)
        SendMessageW(GlobalVariable.window["hWnd"], WM_KEYDOWN, vk_code, lparam)
        time.sleep(0.01)
        SendMessageW(GlobalVariable.window["hWnd"], WM_KEYUP, vk_code, lparam)

def key_down(key: str):
    set_us_keyboard_layout()
    key = key.lower()
    if key in special_keys:
        vk_code, scan_code = special_keys[key]
    else:
        # 普通按键的处理
        vk_code = VkKeyScanW(ctypes.c_wchar(key))
        scan_code = keyboard.key_to_scan_codes(key)[0] if key != '/' else keyboard.key_to_scan_codes(key)[1]
    lparam = (scan_code << 16) | 1
    if GlobalVariable.is_post_w:
        PostMessageW(GlobalVariable.window["hWnd"], win32con.WM_ACTIVATE, win32con.WA_ACTIVE, 0)
        PostMessageW(GlobalVariable.window["hWnd"], WM_KEYDOWN, vk_code, lparam)
    else:
        SendMessageW(GlobalVariable.window["hWnd"], win32con.WM_ACTIVATE, win32con.WA_ACTIVE, 0)
        SendMessageW(GlobalVariable.window["hWnd"], WM_KEYDOWN, vk_code, lparam)

def key_up(key: str):
    key = key.lower()
    if key in special_keys:
        vk_code, scan_code = special_keys[key]
    else:
        # 普通按键的处理
        vk_code = VkKeyScanW(ctypes.c_wchar(key))
        scan_code = keyboard.key_to_scan_codes(key)[0] if key != '/' else keyboard.key_to_scan_codes(key)[1]
    lparam = (scan_code << 16) | 0XC0000001
    if GlobalVariable.is_post_w:
        PostMessageW(GlobalVariable.window["hWnd"], win32con.WM_ACTIVATE, win32con.WA_ACTIVE, 0)
        PostMessageW(GlobalVariable.window["hWnd"], WM_KEYUP, vk_code, lparam)
    else:
        SendMessageW(GlobalVariable.window["hWnd"], win32con.WM_ACTIVATE, win32con.WA_ACTIVE, 0)
        SendMessageW(GlobalVariable.window["hWnd"], WM_KEYUP, vk_code, lparam)

def mouse_wheel_scroll(operator):
    match operator:
        case 'up':
            delta =  3000
        case 'down':
            delta = -3000
    window_rect = win32gui.GetWindowRect(GlobalVariable.window["hWnd"])  # 返回 (left, top, right, bottom)
    # 窗口中心
    window_x, window_y = window_rect[0] + window_rect[0] / 2, window_rect[1] + window_rect[1] / 2
    # 激活窗口
    if GlobalVariable.is_post_w:
        PostMessageW(GlobalVariable.window["hWnd"], win32con.WM_ACTIVATE, win32con.WA_ACTIVE, 0)
    else:
        SendMessageW(GlobalVariable.window["hWnd"], win32con.WM_ACTIVATE, win32con.WA_ACTIVE, 0)
    pyautogui.moveTo(window_x, window_y)
    pyautogui.scroll(delta)

def set_us_keyboard_layout():
    # LoadKeyboardLayoutW 函数的定义
    user32.LoadKeyboardLayoutW.argtypes = [ctypes.c_wchar_p, ctypes.c_uint]
    user32.LoadKeyboardLayoutW.restype = ctypes.c_void_p
    user32.LoadKeyboardLayoutW("00000409", 1)  # 0409 是美国键盘布局标识符，1 表示激活

special_keys = {
    'space': (0x20, 0x39),  # 空格键
    'tab': (0x09, 0x0F),    # Tab 键
    'esc': (0x1B, 0x01),    # Escape 键
    'shift': (0x10, 0x2A),  # 左 Shift 键
    'right': (0x27, 0x4D),  # 方向键右
    'left': (0x25, 0x4B),   # 方向键左
    'up': (0x26, 0x48),     # 方向键上
    'down': (0x28, 0x50)    # 方向键下
}
