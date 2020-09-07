import time
import str


driver = str.driver


def login():
    time.sleep(10)
    app_logo = driver.find_element_by_xpath(
        "/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.view.ViewGroup/android.widget.LinearLayout/android.view.ViewGroup/android.widget.ImageView")
    if app_logo:
        # find the login link
        driver.find_element_by_id("btn_intro_login").click()
        time.sleep(10)
        # input email
        driver.find_element_by_id("et_login_email").send_keys(str.username)
        # input password
        driver.find_element_by_id("et_login_password").send_keys(str.password)
        time.sleep(5)
        # select the login button
        driver.find_element_by_id("btn_login_custom").click()
        time.sleep(10)
        # find the project page by text
        if driver.find_element_by_xpath(
                   "//android.widget.LinearLayout[@content-desc=\"Projects\"]/android.widget.TextView"):
            print(str.successful_messages)

    else:
        print(str.failed_messages + ' cannot load the page')


def tearDown():
    driver.quit()
