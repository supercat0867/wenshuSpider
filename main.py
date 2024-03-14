from selenium import webdriver
import json

from spider.spider import Spider


# 读取配置文件
def read_config(config_file):
    with open(config_file, 'r') as file:
        config = json.load(file)
        return config


if __name__ == '__main__':
    conf = read_config("config.json")

    options = webdriver.ChromeOptions()
    # 保持浏览器的打开状态（测试用）
    options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(options=options)

    spider = Spider(driver, conf)
    # 步骤1: 登录
    spider.login()
    # 步骤2: 点击具体案件类型，并切换窗口
    spider.switch_window("民事案件")
    # 选择分页
    spider.selectPageSize(15)
    # 选择四川省
    spider.selectArea("四川省")
    # 点击日期排序
    spider.clickDateSort()

    for i in range(1, 10):
        # 获取案件列表
        case_list = spider.getList()
        # 保存案件
        spider.saveList(case_list)
        # 点击下一页
        spider.clickNextPage()
