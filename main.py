import time
import os
import sys
from utils.config_manager import ConfigManager
from utils.device_manager import DeviceManager
from utils.uiautomator2_manager import UIAutomator2Manager
from utils.logger import Logger
from market_automation.market_clicker import MarketClicker

# 添加项目根目录到Python路径
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

class SimpleCaptureManager:
    """简化的截图管理器"""
    
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.save_path = config.get("screenshot", {}).get("save_path", "data/screenshots/")
        
        # 确保目录存在
        os.makedirs(self.save_path, exist_ok=True)
    
    def capture_full_screen(self, device):
        """截取全屏"""
        try:
            # 使用UIAutomator2截图
            screenshot_data = device.screenshot()
            if screenshot_data:
                # 生成文件名
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"{timestamp}_full.png"
                filepath = os.path.join(self.save_path, filename)
                
                # 保存截图
                screenshot_data.save(filepath)
                self.logger.info(f"全屏截图保存成功：{filepath}")
                return filepath
            else:
                self.logger.error("截图失败")
                return None
        except Exception as e:
            self.logger.error(f"截图异常：{str(e)}")
            return None
    
    def capture_region(self, device, x1, y1, x2, y2):
        """截取指定区域"""
        try:
            # 先截取全屏
            screenshot_data = device.screenshot()
            if screenshot_data:
                # 裁剪指定区域
                region = screenshot_data.crop((x1, y1, x2, y2))
                
                # 生成文件名
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"{timestamp}_region_{x1}_{y1}_{x2}_{y2}.png"
                filepath = os.path.join(self.save_path, filename)
                
                # 保存截图
                region.save(filepath)
                self.logger.info(f"区域截图保存成功：{filepath}")
                return filepath
            else:
                self.logger.error("截图失败")
                return None
        except Exception as e:
            self.logger.error(f"区域截图异常：{str(e)}")
            return None

def main():
    # 1. 初始化工具（读取配置 + 连接设备 + 初始化截图/日志）
    config = ConfigManager("config/market_config.json")
    logger = Logger()
    device_manager = DeviceManager(config, logger)
    
    # 2. 确认设备连接成功
    if not device_manager.check_device():
        logger.error("设备连接失败！请检查 ADB 和模拟器端口")
        return
    
    # 初始化UIAutomator2管理器
    u2_manager = UIAutomator2Manager(config, logger)
    if not u2_manager.initialize():
        logger.error("UIAutomator2初始化失败")
        return
    
    # 初始化截图管理器
    capture_manager = SimpleCaptureManager(config.config, logger)
    
    # 初始化市场点击器
    market_clicker = MarketClicker(u2_manager, config, logger)
    if not market_clicker.initialize():
        logger.error("市场点击器初始化失败")
        return
    
    logger.info("设备连接成功：" + device_manager.device_id)
    
    # 3. 定位游戏按钮（以"市场"按钮为例，你需要替换成实际的按钮文本/ID）
    try:
        logger.info("开始定位游戏按钮...")
        
        # 获取当前应用信息
        current_app = u2_manager.get_current_app()
        if current_app:
            logger.info(f"当前应用：{current_app.get('package')} - {current_app.get('activity')}")
        
        # 截取当前屏幕用于调试
        logger.info("截取当前屏幕用于调试...")
        full_screen_path = capture_manager.capture_full_screen(u2_manager.device)
        if full_screen_path:
            logger.info(f"当前屏幕截图保存成功：{full_screen_path}")
        
        # 方法1：通过按钮文本定位（最常用，比如游戏里"市场"按钮的文本是"市场"）
        market_btn = u2_manager.find_element_by_text("市场")
        if market_btn:
            logger.info(f"找到\"市场\"按钮，坐标：{u2_manager.get_element_center(market_btn)}")
            
            # 模拟点击"市场"按钮（进入市场界面）
            u2_manager.click_element(market_btn)
            time.sleep(2)  # 等待界面加载（根据游戏加载速度调整）
            
            # 4. 获取市场装备价格图片（截图市场界面的价格区域）
            logger.info("开始截图市场价格区域...")
            
            # 方法1：截全屏（简单，直接保存整个市场界面）
            full_screen_path = capture_manager.capture_full_screen(u2_manager.device)
            if full_screen_path:
                logger.info(f"全屏截图保存成功：{full_screen_path}")
            
            # 方法2：截指定区域（精准截价格标签，需要手动找区域坐标）
            # 比如价格区域的左上角(x1,y1)=[300,400]，右下角(x2,y2)=[600,500]
            # price_area_path = capture_manager.capture_region(u2_manager.device, 300, 400, 600, 500)
            # if price_area_path:
            #     logger.info(f"价格区域截图保存成功：{price_area_path}")
            
        else:
            logger.error("未找到\"市场\"按钮！请检查按钮文本是否正确，或是否是图像按钮")
            logger.info("提示：请确保游戏已运行并显示在主界面")
            
            # 如果是图像按钮（无文本），用坐标定位（之前教你的 ADB 截图找坐标）
            # u2_manager.tap_element(x=500, y=800)  # 替换成实际的"市场"按钮坐标
        
        # 5. 执行市场自动化操作序列
        logger.info("开始执行市场自动化操作序列...")
        try:
            success = market_clicker.execute_market_sequence()
            if success:
                logger.info("市场自动化操作序列执行成功")
            else:
                logger.error("市场自动化操作序列执行失败")
        except Exception as e:
            logger.error(f"市场自动化操作异常：{str(e)}")
    
    except Exception as e:
        logger.error(f"操作失败：{str(e)}")
    
    finally:
        # 清理资源
        if 'market_clicker' in locals():
            market_clicker.cleanup()
        u2_manager.cleanup()

if __name__ == "__main__":
    main()