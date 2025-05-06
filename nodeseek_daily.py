# -- coding: utf-8 --
"""
Copyright (c) 2024 [Hosea]
Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import traceback
import undetected_chromedriver as uc

ns_random = os.environ.get("NS_RANDOM", "false")
cookie = os.environ.get("NS_COOKIE") or os.environ.get("COOKIE")
# 通过环境变量控制是否使用无头模式，默认为 True（无头模式）
headless = os.environ.get("HEADLESS", "true").lower() == "true"

def click_sign_icon(driver):
    """
    尝试点击签到图标/链接，然后点击奖励按钮的通用方法
    """
    try:
        print("步骤 1: 查找签到入口元素...")

        # --- Using the confirmed XPath based on your HTML ---
        sign_icon_xpath = "//span[@title='签到']"
        # --- This XPath matches the HTML you provided ---

        print(f"  尝试使用 XPath (初始签到入口): {sign_icon_xpath}")
        print(f"  等待元素变为可见 (最多 30 秒)...")

        # --- MODIFICATION: Wait for VISIBILITY instead of CLICKABLE ---
        sign_icon = WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located((By.XPATH, sign_icon_xpath))
        )
        # --- END OF MODIFICATION ---

        print(f"  找到并确认签到入口元素可见: Tag={sign_icon.tag_name}, Title='{sign_icon.get_attribute('title')}'")

        # --- 后续逻辑 (滚动、点击、等待、查找奖励按钮) ---
        print("  滚动到签到入口并尝试点击...")
        driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});", sign_icon)
        time.sleep(1) # Wait for scroll

        # Try clicking the element now that it's visible
        try:
            # It might be better to wait briefly for clickability AFTER visibility is confirmed
            WebDriverWait(driver, 5).until(EC.element_to_be_clickable(sign_icon)) # Short wait for clickability
            sign_icon.click()
            print("  签到入口点击成功。")
        except Exception as click_error:
            print(f"  直接点击失败 (元素可见但无法点击?)，尝试使用 JavaScript 点击: {str(click_error)}")
            try:
                driver.execute_script("arguments[0].click();", sign_icon)
                print("  JavaScript 点击尝试完成。")
            except Exception as js_click_error:
                 print(f"  JavaScript 点击也失败: {js_click_error}")
                 raise js_click_error # Re-raise error if JS click fails

        print("步骤 2: 等待签到确认/奖励按钮出现 (等待最多 10 秒)...")
        time.sleep(5) # General wait, might need refinement

        print(f"  当前页面 URL (点击签到入口后): {driver.current_url}")

        print("步骤 3: 查找并点击奖励按钮 ('试试手气' 或 '鸡腿 x 5')...")
        try:
            click_button = None
            # Using the updated XPath for "试试手气" from previous step
            lucky_button_xpath = "//button[contains(@class, 'btn') and contains(text(), '试试手气')]"
            fixed_reward_xpath = "//button[contains(text(), '鸡腿 x 5')]" # Keep original or update if needed
            wait_time_for_reward = 10

            if ns_random == "true":
                print(f"  NS_RANDOM is true. 查找 '{lucky_button_xpath}'...")
                click_button = WebDriverWait(driver, wait_time_for_reward).until(
                    EC.element_to_be_clickable((By.XPATH, lucky_button_xpath))
                )
            else:
                print(f"  NS_RANDOM is false. 查找 '{fixed_reward_xpath}'...")
                click_button = WebDriverWait(driver, wait_time_for_reward).until(
                    EC.element_to_be_clickable((By.XPATH, fixed_reward_xpath))
                )

            print(f"  找到奖励按钮: '{click_button.text}'")
            driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});", click_button)
            time.sleep(0.5)
            click_button.click()
            print("  奖励按钮点击成功。")
            time.sleep(3) # Wait for click effect

        except Exception as lucky_error:
            print(f"  未能点击奖励按钮。可能原因：已签到、签到失败、按钮未出现、选择器错误或超时。")
            print(f"  详细错误: {type(lucky_error).__name__}: {str(lucky_error)}")

        print("签到流程尝试完毕。")
        return True

    except TimeoutException: # Catch timeout specifically when waiting for VISIBILITY
        print(f"错误：在等待初始签到入口变为可见时超时 ({sign_icon_xpath})。")
        print(f"当前页面URL: {driver.current_url}")
        # Save debug info
        try:
            screenshot_file = "debug_screenshot_signin_visibility_timeout.png"
            page_source_file = "debug_page_signin_visibility_timeout.html"
            driver.save_screenshot(screenshot_file)
            with open(page_source_file, "w", encoding="utf-8") as f:
               f.write(driver.page_source)
            print(f"已保存调试信息：{screenshot_file} 和 {page_source_file}。请检查页面是否正确加载，元素是否真的可见。")
        except Exception as save_err:
            print(f"保存调试信息时出错: {save_err}")
        print("详细错误信息:")
        traceback.print_exc()
        return False # Sign-in failed

    except Exception as e: # Catch other errors
        print(f"签到主流程出错 (非初始查找超时):")
        print(f"错误类型: {type(e).__name__}")
        print(f"错误信息: {str(e)}")
        print(f"当前页面URL: {driver.current_url}")
        traceback.print_exc()
        return False
        
def setup_driver_and_cookies():
    """
    初始化浏览器并设置cookie的通用方法
    返回: 设置好cookie的driver实例
    """
    try:
        cookie = os.environ.get("NS_COOKIE") or os.environ.get("COOKIE")
        headless = os.environ.get("HEADLESS", "true").lower() == "true"
        
        if not cookie:
            print("未找到cookie配置")
            return None
            
        print("开始初始化浏览器...")
        options = uc.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        if headless:
            print("启用无头模式...")
            options.add_argument('--headless')
            # 添加以下参数来绕过 Cloudflare 检测
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            # 设置 User-Agent
            options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        print("正在启动Chrome...")
        # ========== START: Replacement Code Block ==========
        # This block replaces the original `driver = uc.Chrome(options=options)` line
        # It handles using the correct browser path in GitHub Actions

        chrome_executable_path = '/opt/hostedtoolcache/setup-chrome/chromium/stable/x64/chrome'
        print(f"检查 Chrome 可执行文件路径: {chrome_executable_path}")

        # Check if running inside GitHub Actions and the path exists
        if os.environ.get("GITHUB_ACTIONS") == "true" and os.path.exists(chrome_executable_path):
            print(f"在 GitHub Actions 环境中运行，并找到 Chrome 路径。强制使用该路径。")
            # Use browser_executable_path argument
            driver = uc.Chrome(browser_executable_path=chrome_executable_path, options=options)
        else:
            # Fallback to default behavior if not in Actions or path not found
            if os.environ.get("GITHUB_ACTIONS") == "true":
                print(f"警告: 在 GitHub Actions 环境中运行，但未找到指定路径的 Chrome: {chrome_executable_path}。")
            print("未使用 GitHub Actions 或未找到指定 Chrome 路径。使用 uc 默认浏览器检测。")
            driver = uc.Chrome(options=options) # Original call as fallback
        # ========== END: Replacement Code Block ==========
        
        if headless:
            # 执行 JavaScript 来修改 webdriver 标记
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            driver.set_window_size(1920, 1080)
        
        print("Chrome启动成功")
        
        print("正在设置cookie...")
        driver.get('https://www.nodeseek.com')
        
        # 等待页面加载完成
        time.sleep(5)
        
        for cookie_item in cookie.split(';'):
            try:
                name, value = cookie_item.strip().split('=', 1)
                driver.add_cookie({
                    'name': name, 
                    'value': value, 
                    'domain': '.nodeseek.com',
                    'path': '/'
                })
            except Exception as e:
                print(f"设置cookie出错: {str(e)}")
                continue
        
        print("刷新页面...")
        driver.refresh()
        time.sleep(5)  # 增加等待时间
        
        return driver
        
    except Exception as e:
        print(f"设置浏览器和Cookie时出错: {str(e)}")
        print("详细错误信息:")
        print(traceback.format_exc())
        return None

if __name__ == "__main__":
    print("开始执行NodeSeek签到脚本...")
    driver = setup_driver_and_cookies()
    if not driver:
        print("浏览器初始化失败")
        exit(1)
    click_sign_icon(driver)
    print("脚本执行完成 ")
