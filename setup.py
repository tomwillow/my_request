from setuptools import setup, find_packages

setup(
    name='my_request',  # 包的名字，应与你的库或项目名一致
    version='0.1.0',  # 版本号，遵循语义化版本控制
    packages=find_packages(),  # 告诉setuptools自动发现并包含哪些包
)