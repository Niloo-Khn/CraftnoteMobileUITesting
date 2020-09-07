# CraftnoteMobileUITesting

NOTICE: 
      - The project is based on Emulator, by using real device please check the divice name and its host and change them in config.ini file.
      - The application should be dowload from attachment dont use any other version.
      
INSTALLATION REQUIERMENTS: 
1- Appium Server 
2- Android studio
3- Python3
4- Pycharm

Steps to run demo test
Clone this git repository

#git clone
Start Appium Server using Appium Desktop installed in your PC. The project expects the Appium Server to run on localhost:4723. If you run the server to different host and port. Please change the code.

Its important to download the application from attachment. (Please change the code in case you change the download location)

Import the cloned project in Pycharm (In Pycharm menu, navigate to File > Open or "Open" if no projects are open)

Modify following variables in the code if necessary

Open config.ini and modify following if necessary,

Appium Server listening host and port.

self.driver = webdriver.Remote("http://localhost:4723/wd/hub",self.dc)
Path of the application (in case downloaded location is different)

self.dc['app'] = "c:\craftnote-construction-management_1.26.2.apk"
Device name (After excecuting adb devices. See "Android device recognition" in the blogs)

self.dc['deviceName'] = 'emulator-5554'
