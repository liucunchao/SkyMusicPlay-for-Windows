import threading
import time

import plyer

from windhide._global import global_variable
from windhide.utils.ocr_screenshot_util import resetGameFrame, get_friend_model_position

if global_variable.cpu_type == 'Intel':
    from windhide.playRobot.intel_robot import mouse_move_to, key_press, mouse_wheel_scroll
else:
    from windhide.playRobot.amd_robot import mouse_move_to, key_press, mouse_wheel_scroll

class HeartFireThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self._running = False  # 控制线程运行的标志位
        self._lock = threading.Lock()  # 保证线程安全

    def run(self):
        """线程启动后执行的主逻辑"""
        self._running = True
        resetGameFrame()
        mouse_wheel_scroll("down")
        time.sleep(2)
        key_press("g")
        time.sleep(3)
        # 先判断是不是第一页
        while self._running:
            friend_button = get_friend_model_position(0.11)["button"]
            if len(friend_button) >= 2:
                break
            else:
                key_press("z")
            self.check_running()
            time.sleep(3)
        key_press("c")
        time.sleep(2)
        # 来到第一页
        while True:
            if not self._running:
                break
            results = get_friend_model_position(0.11)
            button = results["button"]
            friend = results["friend"]
            if len(friend) != 0:
                for position in friend:
                    if not self._running:
                        break
                    time.sleep(1)
                    mouse_move_to(position[0], position[1])
                    key_press("space")
                    time.sleep(0.5)
                    key_press("space")
                    time.sleep(1.5)
                    # send_single_key_to_window_follow("left")
                    # 这里改成鼠标移动点击，无法识别方向键
                    time.sleep(0.8)
                    key_press("space")
                    time.sleep(0.8)
                    key_press("f")
                    time.sleep(1)
                    key_press("ESC")
                # 下一页
                time.sleep(1.5)
                key_press("c")
                time.sleep(3)
            else:
                # 如果没有，显示别是不是到第一页去了，否则直接下一页
                if len(button) < 2:
                    key_press("c")
                    time.sleep(3)
                else:
                    plyer.notification.notify(
                        title='🔥🔥🔥🔥🔥🔥🔥🔥',
                        message='点火结束🔥🔥🔥🔥🔥',
                        timeout=1
                    )
                    return "点火结束"

    def stop(self):
        """安全停止线程"""
        with self._lock:
            self._running = False
        global_variable.auto_thread = None

    def check_running(self):
        """检查线程是否正在运行，若未运行则安全退出"""
        with self._lock:
            if not self._running:
                raise StopIteration("线程已停止")
