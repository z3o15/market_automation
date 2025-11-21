import cv2
import numpy as np
import uiautomator2 as u2
import time

def find_button(template_path, threshold=0.8):
    """
    图像识别找按钮
    :param template_path: 按钮模板图路径
    :param threshold: 匹配阈值（0-1，越高越精准）
    :return: 按钮中心点坐标 (x, y)，没找到返回 None
    """
    # 1. 截当前游戏全屏图
    d = u2.connect("127.0.0.1:5557")
    screen_path = "temp_screen.png"
    d.screenshot(screen_path)  # 用uiautomator2截图，更方便

    # 2. 读取全屏图和模板图
    screen = cv2.imread(screen_path)
    template = cv2.imread(template_path)
    if screen is None or template is None:
        print("截图或模板图读取失败！")
        return None

    # 3. 图像匹配（模板匹配）
    h, w = template.shape[:2]
    result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    # 4. 判断是否匹配成功
    if max_val >= threshold:
        # 计算中心点坐标
        x = max_loc[0] + w // 2
        y = max_loc[1] + h // 2
        print(f"找到按钮！坐标：({x}, {y})，匹配度：{max_val:.2f}")
        return (x, y)
    else:
        print(f"未找到按钮，最高匹配度：{max_val:.2f}（低于阈值 {threshold}）")
        return None

def click_button_by_image(template_path):
    """
    图像识别并点击按钮
    """
    d = u2.connect("127.0.0.1:5557")
    # 确保游戏在前台
    d.screen_on()
    d.app_start("com.example.game", stop=True)  # 替换为你的游戏包名（可选）
    time.sleep(2)

    # 找按钮
    button_pos = find_button(template_path)
    if button_pos:
        x, y = button_pos
        print(f"点击按钮坐标：({x}, {y})")
        d.click(x, y)
        time.sleep(1)  # 点击后等待1秒
        return True
    else:
        print("点击失败：未找到按钮")
        return False

if __name__ == "__main__":
    # 替换为你的按钮模板图路径
    BUTTON_TEMPLATE = "market_automation\market_btn.png"
    click_button_by_image(BUTTON_TEMPLATE)