import json
import os
import re
import shutil
import winreg
import zipfile
from pathlib import Path
import requests
from my_request import MyDownloader

current_dir = Path().parent  #
version_re = re.compile(r'^[1-9]\d*\.\d*.\d*')  # 匹配前3位版本信息


def get_chrome_version():
    """通过注册表查询Chrome版本信息: HKEY_CURRENT_USER\SOFTWARE\Google\Chrome\BLBeacon: version"""
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'SOFTWARE\Google\Chrome\BLBeacon')
        value = winreg.QueryValueEx(key, 'version')[0]
        return version_re.findall(value)[0]
    except WindowsError as e:
        raise RuntimeError("没有检测到Chrome浏览器。")


def get_chrome_driver_version():
    """
    检查当前路径下的chromedriver.exe的版本。只返回版本号的前3个数字。失败则返回0.0.0
    """
    try:
        result = os.popen('chromedriver --version').read()
        version = result.split(' ')[1]
        return '.'.join(version.split('.')[:-1])
    except Exception as e:
        return '0.0.0'  # 没有安装ChromeDriver


def download_zip_and_extract_delete(download_url):
    # 下载chromedriver zip文件
    local_file = current_dir / 'chromedriver.zip'

    MyDownloader.download_with_progress(download_url, str(local_file))

    # 解压缩zip文件到python安装目录
    f = zipfile.ZipFile(str(local_file), 'r')
    for file in f.namelist():
        f.extract(file, current_dir)
    f.close()

    local_file.unlink()  # 解压缩完成后删除zip文件


def get_latest_chrome_driver_from_taobao(chrome_version):
    base_url = 'http://npm.taobao.org/mirrors/chromedriver/'  # chromedriver在国内的镜像网站
    url = f'{base_url}LATEST_RELEASE_{chrome_version}'
    latest_version = requests.get(url).text
    download_url = f'{base_url}{latest_version}/chromedriver_win32.zip'

    download_zip_and_extract_delete(download_url)


def get_latest_chrome_driver_from_official(chrome_version):
    json_url = "https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json"
    print(f"- 正在获取chromedriver版本列表...")
    print(f"- from: {json_url}")
    response = requests.get(json_url)
    j = json.loads(response.content)
    versions = j["versions"]
    for obj in versions:
        version = obj["version"]
        if version.find(chrome_version) == -1:
            continue

        # 找到对应版本
        chromedrivers = obj["downloads"]["chromedriver"]
        for chromedriver in chromedrivers:
            if chromedriver["platform"] != "win64":
                continue
            # 平台匹配
            download_url = chromedriver["url"]
            print(f"- 开始下载{download_url}")
            download_zip_and_extract_delete(download_url)

            # 上一步解压到了 ./chromedriver-win64，所以还要到里面把东西移出来
            shutil.move("chromedriver-win64/chromedriver.exe", "chromedriver.exe")
            shutil.rmtree("chromedriver-win64")
            return
    raise RuntimeError("没有找到合适的版本")



def check_chrome_driver_update():
    """
    自动更新chromedriver到当前目录
    """
    print(f"- 检查本地Chrome浏览器版本...")
    chrome_version = get_chrome_version()
    print(f"- Chrome已安装：{chrome_version}")
    print(f"- 检查当前路径下的chromedriver版本...")
    driver_version = get_chrome_driver_version()
    print(f"- 当前路径下的chromedriver版本：{driver_version}")
    if chrome_version == driver_version:
        print('- chromedriver版本匹配，不需要更新')
    else:
        try:
            print('- chromedriver版本不匹配，需要更新...')
            get_latest_chrome_driver_from_official(chrome_version)
        except Exception as e:
            print(f'Fail to update: {e}')


if __name__ == '__main__':
    check_chrome_driver_update()
