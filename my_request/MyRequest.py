
import requests
import json


class MyRequest:
    def __init__(self):
        # 设置请求头
        self.req_header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36',
        }
        self.session = requests.Session()
        pass

    def LoadCookieFromWebDriver(self, wd):
        cookies = wd.get_cookies()
        for cookie in cookies:
            self.session.cookies.set(cookie['name'], cookie['value'])
            # print(cookie)

    def Get(self, url: str) -> str:
        print(f"[GET]{url}")
        response = self.session.get(url, headers=self.req_header) # 不加verify=False的话开启Fiddler抓包状态会抛出SSL Error
        return response.text

    def AddHeader(self, key: str, val: str):
        """
        为请求头加上内容
        :param key:
        :param val:
        :return:
        """
        self.req_header[key] = val

    def Post(self, url: str, data: dict) -> dict:
        self.req_header['Accept'] = 'application/json'
        self.req_header['Content-Type'] = 'application/json'
        response = self.session.post(url, headers=self.req_header, data=json.dumps(data))
        return json.loads(response.text)

    def Download(self, url: str, destDir: str):
        response = self.session.get(url, headers=self.req_header)
        filename = url.rpartition("/")[-1]
        with open(destDir + "/" + filename, "wb") as f:
            f.write(response.content)