from configparser import ConfigParser
from appium import webdriver

file = './config.ini'
parser = ConfigParser()
parser.read(file)

dc = {
    'app': parser['setup']['app'],
    'packageName': parser['setup']['packageName'],
    'appActivity': parser['setup']['appActivity'],
    'platformName': parser['setup']['platformName'],
    'deviceName': parser['setup']['deviceName'],
    'autoGrantPermissions': parser['setup']['autoGrantPermissions'],
}

driver = webdriver.Remote("http://localhost:4723/wd/hub", dc)

username = parser['auth']['username']
password = parser['auth']['password']
successful_messages = parser['messages']['successful-messages']
failed_messages = parser['messages']['failed-messages']





















