import random
from time import sleep

from selenium import webdriver
from selenium.webdriver import ActionChains


# from selenium.webdriver import ChromeOptions
#
# option = ChromeOptions()
# option.add_experimental_option('excludeSwitches', ['enable-automation'])
#
# # 1.创建Chrome浏览器对象，这会在电脑上在打开一个浏览器窗口
# browser = webdriver.Chrome(executable_path="C:\Program Files\Google\Chrome\Application\chromedriver.exe",
#                            options=option)


def c():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option('debuggerAddress', '127.0.0.1:9222')
    browser = webdriver.Chrome(executable_path=r'./chromedriver.exe',
                               options=chrome_options)

    url = "https://www.wjx.cn/vm/wpEwPeZ.aspx"

    # 2.通过浏览器向服务器发送URL请求
    browser.set_window_size(800, 1050)
    browser.get(url)

    sleep(2)
    try:
        element = browser.find_element_by_xpath(f'//*[@id="confirm_box"]/div[2]/div[3]/button[{random.randint(1, 2)}]')
        # element = browser.find_element_by_xpath('//*[@id="slideChunk"]/div[2]')
        element.click()
        sleep(2)
    except:
        print("new")
    # 4.设置浏览器的大小

    # element = browser.find_element_by_xpath("slideChunkWord")

    # ActionChains(browser).move_by_offset(200, 100).click().perform()

    action = ActionChains(browser)
    # 第一步：在滑块处按住鼠标左键
    # action.click_and_hold(element)
    # 第二步：相对鼠标当前位置进行移动
    action.move_by_offset
    action.move_by_offset(random.randint(100, 400), random.randint(300, 500))
    action.click_and_hold()
    action.move_by_offset(random.randint(20, 50), random.randint(150, 260))
    # 第三步：释放鼠标
    action.release()
    # 执行动作
    action.perform()
    # element.click()
    sleep(2)
    choice = [
        random.randint(1, 4),
        random.randint(1, 2),
        random.randint(1, 2),
        random.randint(1, 2),
        random.randint(1, 5),
        random.randint(1, 4),
        random.randint(1, 2),
    ]
    print(choice)

    for i in range(7):
        # '//div[@class="field ui-field-contain"]{i + 1}/div[@class="ui-radio"][{choice[i]}]'
        # element = browser.find_element_by_xpath(f'//*[@id="div{i + 1}"]/div[2]/div[{choice[i]}]/div')
        element = browser.find_element_by_xpath(
            f'//div[@class="field ui-field-contain"][{i + 1}]//div[@class="ui-radio"][{choice[i]}]')
        element.click()
        if i == 4:
            js = f"var q=document.documentElement.scrollTop={random.randint(900, 1000)};"
            browser.execute_script(js)
            sleep(2)
        sleep(random.randint(1, 2))
    sleep(1)
    element = browser.find_element_by_xpath('//*[@id="ctlNext"]')
    element.click()
    sleep(2)
    try:
        element = browser.find_element_by_xpath('//*[@id="alert_box"]/div[2]/div[2]/button')
        element.click()

        element = browser.find_element_by_xpath('//*[@id="SM_BTN_1"]/div[1]/div[4]')
        element.click()
        sleep(3)
        try:
            # 拖动滑块

            source = browser.find_element_by_xpath('//span[@class="nc_iconfont btn_slide"]')
            target = browser.find_element_by_xpath('//span[@class="nc-lang-cnt"]')

            # sli_ele = browser.find_element_by_id('tcaptcha_drag_thumb')
            # ------------鼠标滑动操作------------
            action = ActionChains(browser)
            # 第一步：在滑块处按住鼠标左键
            action.click_and_hold(source)
            # 第二步：相对鼠标当前位置进行移动
            lenth = target.size.get("width") - random.randint(10, 20)
            action.move_by_offset(int(lenth / 3) + 3, 0)
            action.move_by_offset(int(lenth / 3) + 3, 0)
            action.move_by_offset(int(lenth / 3) + 3, 0)
            # 第三步：释放鼠标
            action.release()
            # 执行动作
            action.perform()
            sleep(2)

        except:

            print("此次不用滑动验证")
    except:
        print("element")
    sleep(3)


# c()
while True:
    c()
