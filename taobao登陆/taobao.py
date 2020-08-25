from selenium import webdriver
option = webdriver.ChromeOptions()
option.add_experimental_option('excludeSwitches', ['enable-automation']) #这里去掉window.navigator.webdriver的特性

domain = "https://www.taobao.com/"

#下面的chromedriver.exe使用特殊的可执行文件，去掉了$cdc_lasutopfhvcZLmcfl等特性
browser = webdriver.Chrome( options=option)
import time
browser.get(domain)
browser.find_element_by_xpath('//*[@id="J_SiteNavLogin"]/div[1]/div[1]/a[1]').click()
time.sleep(5)
# browser.find_element_by_xpath('//*[@id="J_Quick2Static"]').click()
# time.sleep(5)
username_el = browser.find_element_by_id("fm-login-id")
#淘宝会检测输入的速度，所以控制一下输入速度
username = "tb8270086_00"
for character in username:
    username_el.send_keys(character)
    time.sleep(0.3) # pause for 0.3 seconds

pwd_el = browser.find_element_by_id("fm-login-password")
password = "xxx"
for character in password:
    pwd_el.send_keys(character)
    time.sleep(0.3) # pause for 0.3 seconds

time.sleep(2)
sub = browser.find_elements_by_xpath('//*[@id="login-form"]/div[4]/button')[0]
sub.click()
time.sleep(5)
time.sleep(20)