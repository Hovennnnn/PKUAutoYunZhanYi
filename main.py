# -*- coding: utf-8
from msilib import type_binary
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from argparse import ArgumentParser
from urllib.parse import quote
from urllib import request
import sys
import time
import warnings
import json


warnings.filterwarnings('ignore')


def dropdown_handler(driver, xpath: str):
    """
    点击带有滚动条的菜单
    ref: https://stackoverflow.com/questions/57303355
    """
    wait = WebDriverWait(driver, 10)
    ele = wait.until(EC.visibility_of_element_located((By.XPATH, xpath)))
    ele.location_once_scrolled_into_view
    ele.click()
    time.sleep(0.1)


def login(driver, userName, password, retry=0):
    '''
    登录门户
    '''
    if retry == 3:
        raise Exception('门户登录失败')

    print('门户登陆中...')

    appID = 'portal2017'
    iaaaUrl = 'https://iaaa.pku.edu.cn/iaaa/oauth.jsp'
    appName = quote('北京大学校内信息门户新版')
    redirectUrl = 'https://portal.pku.edu.cn/portal2017/ssoLogin.do'

    driver.get('https://portal.pku.edu.cn/portal2017/')
    driver.get(
        f'{iaaaUrl}?appID={appID}&appName={appName}&redirectUrl={redirectUrl}'
    )
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, 'logon_button'))
    )
    driver.find_element_by_id('user_name').send_keys(userName)
    time.sleep(0.1)
    driver.find_element_by_id('password').send_keys(password)
    time.sleep(0.1)
    driver.find_element_by_id('logon_button').click()
    try:
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, 'all'))
        )
        print('门户登录成功！')
    except:
        print('Retrying...')
        login(driver, userName, password, retry + 1)


def go_to_YunZhanYi(driver):
    '''
    点击“全部”，找到“燕园云战役”并点击
    '''
    button = driver.find_element_by_id('all')
    driver.execute_script("$(arguments[0]).click()", button)
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, 'tag_s_epidemic'))
    )
    driver.find_element_by_id('tag_s_epidemic').click()
    time.sleep(2)
    driver.switch_to.window(driver.window_handles[-1])
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located(
            (By.CLASS_NAME, 'el-tabs__nav-scroll')
        )
    )


def select_in_or_out(driver):
    # 点击“每日填报”
    driver.find_element_by_xpath('//*[@id="tab-daily_info_tab"]/span').click()
    WebDriverWait(driver, 20).until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                f'//*[@id="pane-daily_info_tab"]/form/div[4]/div/div[2]/label/span[2]'
            )
        )
    )

    # 点击“未到校”
    driver.find_element_by_xpath(
        f'//*[@id="pane-daily_info_tab"]/form/div[4]/div/div[2]/label/span[2]'
    ).click()


def select_province(driver, province):
    driver.find_element_by_xpath(
        '//*[@id="pane-daily_info_tab"]/form/div[5]/div/div/div[1]/input'
    ).click()
    dropdown_handler(
        driver,
        f'/html/body/div[2]/div[1]/div[1]/ul/li/span[text()="{province}"]'
    )


def select_city(driver, city):
    driver.find_element_by_xpath(
        '//*[@id="pane-daily_info_tab"]/form/div[6]/div/div/div[1]/input'
    ).click()
    dropdown_handler(
        driver, f'/html/body/div[3]/div[1]/div[1]/ul/li/span[text()="{city}"]'
    )


def select_country(driver, country):
    driver.find_element_by_xpath(
        '//*[@id="pane-daily_info_tab"]/form/div[7]/div/div/div[1]/input'
    ).click()
    dropdown_handler(
        driver,
        f'/html/body/div[4]/div[1]/div[1]/ul/li/span[text()="{country}"]'
    )


def write_address(driver, address):
    driver.find_element_by_xpath(
        '//*[@id="pane-daily_info_tab"]/form/div[8]/div/div/textarea'
    ).clear()
    driver.find_element_by_xpath(
        '//*[@id="pane-daily_info_tab"]/form/div[8]/div/div/textarea'
    ).send_keys(f'{address}')
    time.sleep(0.1)


def select_healthy(driver):
    # 是否与确诊病例密接，尚未解除观察
    driver.find_element_by_xpath(
        f'//*[@id="pane-daily_info_tab"]/form/div[9]/div/div/label[2]/span[text()="否"]'
    ).click()

    # 是否与确诊病例密接者密接，尚未解除观察
    driver.find_element_by_xpath(
        f'//*[@id="pane-daily_info_tab"]/form/div[10]/div/div/label[2]/span[text()="否"]'
    ).click()

    # 目前是否居住在中高风险地区
    driver.find_element_by_xpath(
        f'//*[@id="pane-daily_info_tab"]/form/div[11]/div/div/label[2]/span[text()="否"]'
    ).click()

    # 是否存在以下症状 （发热、咳嗽、腹泻)
    driver.find_element_by_xpath(
        f'//*[@id="pane-daily_info_tab"]/form/div[13]/div/label[2]/span[text()="否"]'
    ).click()

    # 疫情诊断
    driver.find_element_by_xpath(
        '//*[@id="pane-daily_info_tab"]/form/div[14]/div/div/div/input'
    ).click()
    dropdown_handler(
        driver, '/html/body/div[5]/div[1]/div[1]/ul/li/span[text()="健康"]'
    )


def write_temperature(driver, temperature):
    '''
    今日体温(单位：摄氏度)
    '''
    driver.find_element_by_xpath(
        '//*[@id="pane-daily_info_tab"]/form/div[12]/div/div/div/input'
    ).clear()
    driver.find_element_by_xpath(
        '//*[@id="pane-daily_info_tab"]/form/div[12]/div/div/div/input'
    ).send_keys(f'{temperature}')
    time.sleep(0.1)


def submit(driver):
    '''
    保存今日信息
    '''
    driver.find_element_by_xpath(
        '//*[@id="pane-daily_info_tab"]/form/div[17]/div/button/span'
    ).click()
    time.sleep(1)


def fill(driver, province, city, country, address):
    print('开始云战役填报')

    print('选择到校情况', end='')
    select_in_or_out(driver)
    print('Done')

    print('选择省份    ', end='')
    select_province(driver, province)
    print('Done')

    print('选择市   ', end='')
    select_city(driver, city)
    print('Done')

    print('选择县   ', end='')
    select_country(driver, country)
    print('Done')

    print('输入详细地址    ', end='')
    write_address(driver, address)
    print('Done')

    print('选择健康状况    ', end='')
    select_healthy(driver)
    print('Done')

    print('填写温度     ', end='')
    write_temperature(driver, 36.2)

    print('填写行动轨迹')
    print('非必要，跳过')
    print('Done')

    print('其它情况说明')
    print('非必要，跳过')
    submit(driver)
    print('Done')


def exception_printer(driver, e: Exception or None):
    '''
    打印报错信息
    '''
    exception_text = []
    try:
        # lookup error message on the page
        exception_text.append(
            driver.find_element_by_class_name('el-form-item__error').text
        )
    except NoSuchElementException:
        pass

    # print error message
    print_bold = lambda x: print('\033[1;31m' + x + '\033[0m', file=sys.stderr)
    print_bold('备案发生错误：')
    if len(exception_text) > 0:
        for text in exception_text:
            # print with bold
            print_bold(text)

    print_bold('请检查您的配置是否正确，或者稍后重试')
    print_bold(
        '如果错误依然存在，请在这里汇报Bug：https://github.com/xiazhongyv/PKUAutoSubmit_online/issues'
    )
    print_bold('错误详细信息：')
    raise e


def wechat_notification(userName, sckey):
    '''
    微信提醒
    '''
    with request.urlopen(
        quote(
            'https://sctapi.ftqq.com/' + sckey + '.send?title=成功报备&desp=学号' +
            str(userName) + '成功报备',
            safe='/:?=&'
        )
    ) as response:
        response = json.loads(response.read().decode('utf-8'))


def run(driver, userName, password, province, city, country, address, sendkey):
    try:
        login(driver, userName, password)
        print('=================================')

        go_to_YunZhanYi(driver)
        fill(driver, province, city, country, address)
        print('=================================')

        print('=================================')
    except Exception as e:
        exception_printer(driver, e)
        return

    if sendkey:
        try:
            wechat_notification(userName, sendkey)
        except Exception as e:
            print(e)
            print('微信推送失败！请检查密钥SENDKEY是否过期！')

    print('报备成功！\n')


if __name__ == '__main__':

    parser = ArgumentParser()
    parser.add_argument('--ID', type=str)
    parser.add_argument('--PASSWORD', type=str)
    parser.add_argument('--PROVINCE', type=str)
    parser.add_argument('--CITY', type=str)
    parser.add_argument('--COUNTRY', type=str)
    parser.add_argument('--ADDRESS', type=str)
    parser.add_argument('--SENDKEY', type=str)
    argconf = parser.parse_args()

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver_pjs = webdriver.Edge(
        options=chrome_options,
                                                                          # executable_path = r'C:\Program Files\Google\Chrome\Application\chromedriver',
        executable_path='/usr/bin/chromedriver',
        service_args=['--ignore-ssl-errors=true', '--ssl-protocol=TLSv1']
    )
    print('Driver Launched\n')

    run(
        driver_pjs, argconf.ID, argconf.PASSWORD, argconf.PROVINCE,
        argconf.CITY, argconf.COUNTRY, argconf.ADDRESS, argconf.SENDKEY
    )

    driver_pjs.quit()