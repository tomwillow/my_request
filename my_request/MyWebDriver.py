# -*- coding: utf-8 -*-
"""

@author: tomwi
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import SessionNotCreatedException
import pickle  # save cookie
from .自动更新ChromeDriver import check_chrome_driver_update
import typing

from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

#get直接返回，不再等待界面加载完成
desired_capabilities = DesiredCapabilities.CHROME
desired_capabilities["pageLoadStrategy"] = "none"

chromePath = "chromedriver.exe"

class MyWebDriver:

    def __init__(self):
        # 检查WebDriver版本，并自动更新
        check_chrome_driver_update()
        self.__OpenWebDriver()

    # 启动
    def __OpenWebDriver(self):
        try:
            serv = webdriver.ChromeService(executable_path=chromePath)

            # chrome options 这段是为了反反爬
            chrome_options = webdriver.ChromeOptions()
            # chrome_options.add_experimental_option(
            #     "excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            # chrome_options.add_argument('lang=zh-CN,zh,zh-TW,en-US,en')
            # chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36')
            chrome_options.add_argument("disable-blink-features=AutomationControlled")  # 就是这一行告诉chrome去掉了webdriver痕迹

            # 启动
            self.wd = webdriver.Chrome(service=serv, options=chrome_options)

            # 设置显性等待时间：若页面在限时内未加载完，则阻塞；超过限时仍未加载完，则继续执行。
            self.wd.implicitly_wait(3)
        except SessionNotCreatedException as e:
            print(e)

    # 打开网页
    def OpenUrl(self, url: str):
        self.wd.get(url)

    def Quit(self):
        self.wd.quit()

    # 根据XPath设置值
    def SetInput(self, xpath: str, value: str):
        element=self.wd.find_element(by=By.XPATH, value=xpath)
        element.clear()
        element.send_keys(value)

    # 点击对应的XPath对象
    def Click(self, xpath: str):
        self.wd.find_element(by=By.XPATH,value=xpath).click()

    # 点击包含text字符串的对象
    def ClickByText(self, text: str):
        self.wd.find_element(by=By.XPATH, value="//*[contains(text(),'%s')]" % text).click()

    # 执行javascript
    def ExecuteJS(self, js: str):
        self.wd.execute_script(js)

    # 切换到最新的窗口
    def SwitchToNewestWindow(self):
        self.wd.switch_to.window(self.wd.window_handles[-1])

    # 关闭除最新窗口以外的所有窗口
    def CloseAllTabsExceptNewestWindow(self):
        shouldCloseWindow = self.wd.window_handles[0:-1]
        for window in shouldCloseWindow:
            self.wd.switch_to.window(window)
            self.wd.close()
        self.SwitchToNewestWindow()

    # 打开新标签
    def OpenNewTab(self, url: str):
        js = "window.open('" + url + "');"
        self.ExecuteJS(js)

    def OnlyReserveAWindow(self, title: str):
        found=False
        for window in self.wd.window_handles:
            self.wd.switch_to.window(window)
            if self.wd.title != title:
                self.wd.close()
            else:
                found=True
        if not found:
            raise RuntimeError("not found window: "+title)

    def SaveCookie(self):
        # 保存 Cookies
        pickle.dump(self.wd.get_cookies(), open("cookies.pkl", "wb"))

    def LoadCookie(self, url: str):
        # 载入 Cookies
        self.OpenUrl(url)
        cookies = pickle.load(open("cookies.pkl", "rb"))
        for cookie in cookies:
            self.wd.add_cookie(cookie)
            print(cookie)

    def GetCookies(self) -> typing.List[dict]:
        return self.wd.get_cookies()