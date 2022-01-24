import random

from selenium import webdriver

chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option('debuggerAddress', '127.0.0.1:9222')
browser = webdriver.Chrome(executable_path=r'C:\Program Files\Google\Chrome\Application\chromedriver.exe',
                           chrome_options=chrome_options)
from selenium.webdriver import ActionChains

url = "https://www.wjx.cn/vm/wpEwPeZ.aspx"
# source = browser.find_element_by_class_name('nc_iconfont btn_slide')

source = browser.find_element_by_xpath('//span[@class="nc_iconfont btn_slide"]')
target = browser.find_element_by_xpath('//span[@class="nc-lang-cnt"]')

# sli_ele = browser.find_element_by_id('tcaptcha_drag_thumb')
# ------------鼠标滑动操作------------
action = ActionChains(browser)
# 第一步：在滑块处按住鼠标左键
action.click_and_hold(source)
# 第二步：相对鼠标当前位置进行移动
action.move_by_offset(target.size.get("width") + random.randint(10, 20), 0)
# 第三步：释放鼠标
action.release()
# 执行动作
action.perform()
