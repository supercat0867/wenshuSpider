import mysql.connector
from mysql.connector import Error
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import Select
import time

searchTypeMaps = {"刑事案件": "2", "民事案件": "3", "行政案件": "4", "赔偿案件": "5", "执行案件": "6", "其他案件": "7",
                  "民族语言文书": "8"}
areaMaps = {"四川省": "N00_anchor"}


class Spider:
    def __init__(self, driver, conf):
        self.driver = driver
        self.conf = conf
        self.wait = WebDriverWait(driver, 3)
        # 连接数据库
        conn = None
        try:
            conn = mysql.connector.connect(
                host=conf["mysql"]["host"],
                port=conf["mysql"]["port"],
                database=conf["mysql"]["database"],
                user=conf["mysql"]["user"],
                password=conf["mysql"]["password"])
            print('成功连接到数据库')
        except Error as e:
            print('数据库连接或操作失败：', e)
        self.conn = conn

    # 步骤1: 登录
    def login(self):
        driver = self.driver
        conf = self.conf
        wait = self.wait
        driver.get("https://wenshu.court.gov.cn/website/wenshu/181010CARHS5BS3C/index.html?open=login")
        while True:
            try:
                # 设置显式等待，尝试等待iframe出现
                iframe_element = wait.until(EC.presence_of_element_located((By.ID, 'contentIframe')))
                break
            except TimeoutException:
                # iframe未在2秒内出现，刷新页面
                driver.refresh()
        # 切换到iframe
        driver.switch_to.frame(iframe_element)
        # 定位到username输入框
        username_input = wait.until(EC.presence_of_element_located((By.NAME, 'username')))
        # 定位到password输入框
        password_input = wait.until(EC.presence_of_element_located((By.NAME, 'password')))
        # 定位到登录按钮
        login_button = driver.find_element(By.XPATH, '//span[@data-api="/api/login"]')
        # 输入用户名和密码
        username_input.send_keys(conf["account"][0]["username"])
        password_input.send_keys(conf["account"][0]["password"])
        # 等待2s点击登录按钮
        time.sleep(2)
        login_button.click()
        print("登录成功")
        time.sleep(4)

    # 步骤2: 点击具体案件类型，并切换窗口
    def switch_window(self, searchType):
        driver = self.driver
        searchType = searchTypeMaps[searchType]
        wait = WebDriverWait(driver, 5)
        while True:
            try:
                case = wait.until(EC.presence_of_element_located(
                    (
                        By.XPATH,
                        f'//div[@class="navlist_aj"]/ul[@class="navlist_aj_ul clearfix"]/li[{searchType}]')))
                break
            except TimeoutException:
                driver.refresh()
            # 获取当前窗口的句柄
        original_window = driver.current_window_handle
        # 点击执行案件
        case.click()
        time.sleep(3)
        # 获取所有窗口的句柄
        all_windows = driver.window_handles
        # 关闭原窗口
        driver.switch_to.window(original_window)
        driver.close()
        # 切换到新窗口
        for window in all_windows:
            if window != original_window:
                driver.switch_to.window(window)
        time.sleep(3)
        while True:
            try:
                wait.until(EC.presence_of_element_located(
                    (By.ID, 'N00_anchor')))
                wait.until(EC.presence_of_element_located(
                    (By.XPATH, "//div[@data-value='s51']/a")))
                break
            except TimeoutException:
                driver.refresh()
        print("窗口切换成功")
        time.sleep(3)

    # 选择分页数(只能为 5、10、15)
    def selectPageSize(self, pageSize):
        wait = self.wait
        value = 5
        if pageSize in [5, 10, 15]:
            value = pageSize
        print(f"正在选择分页{value}")
        select_element = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "pageSizeSelect")))
        select = Select(select_element)
        select.select_by_visible_text(str(value))
        print("成功")
        time.sleep(5)

    # 选择地域
    def selectArea(self, areaName):
        wait = self.wait
        areaCode = areaMaps[areaName]
        print("正在点击地域")
        area = wait.until(EC.presence_of_element_located(
            (By.ID, areaCode)))
        area.click()
        print("成功")
        time.sleep(5)

    # 点击日期排序
    def clickDateSort(self):
        wait = self.wait
        print("正在点击日期排序")
        date_sort = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//div[@data-value='s51']/a")))
        date_sort.click()
        print("成功")
        time.sleep(5)

    # 点击下一页
    def clickNextPage(self):
        driver = self.driver
        print("正在点击下一页")
        next_page_button = driver.find_element(By.LINK_TEXT, "下一页")
        next_page_button.click()
        print("成功")
        time.sleep(5)

    # 获取文书列表
    def getList(self):
        driver = self.driver
        case_list = []
        elements = driver.find_elements(By.CLASS_NAME, "LM_list")
        print("正在获取文书列表")
        for element in elements:
            try:
                # 获取案件标题
                title = element.find_element(By.CSS_SELECTOR, ".list_title a.caseName").text
                # 获取裁判文书原文链接
                url = element.find_element(By.CSS_SELECTOR, ".list_title a.caseName").get_attribute("href")
                # 获取审判程序
                progress = element.find_element(By.CSS_SELECTOR, ".List_label .labelTwo").text
                # 获取法院名
                court = element.find_element(By.CSS_SELECTOR, ".list_subtitle .slfyName").text
                # 获取案号
                case_number = element.find_element(By.CSS_SELECTOR, ".list_subtitle .ah").text
                # 获取裁判日期
                date_str = element.find_element(By.CSS_SELECTOR, ".list_subtitle .cprq").text

                case = [title, url, progress, court, case_number, date_str]
                case_list.append(case)
            except:
                continue
        print("成功")
        return case_list

    # 保存文书到数据库
    def saveList(self, case_list):
        conn = self.conn
        cursor = conn.cursor()
        print("正在保存文书到数据库")
        for case in case_list:
            # 检查是否存在
            query = "SELECT * FROM legal_documents WHERE title = %s"
            cursor.execute(query, (case[0],))
            records = cursor.fetchall()
            if not records:
                insert_query = "INSERT INTO legal_documents (title,original_link,court,case_number,progress,document_date) VALUES (%s,%s,%s,%s,%s,%s)"
                cursor.execute(insert_query, (case[0], case[1], case[3], case[4], case[2], case[5]))
                conn.commit()
        print("成功")
