from selenium import webdriver
from scrapy.selector import Selector
from selenium.webdriver.chrome.options import Options

option = webdriver.ChromeOptions()
#option.add_experimental_option('excludeSwitches', ['enable-automation'])
option.add_experimental_option('debuggerAddress', '127.0.0.1:9222')

browser = webdriver.Chrome(executable_path="./chromedriver", options=option)

browser.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
  "source": """
    Object.defineProperty(navigator, 'webdriver', {
      get: () => undefined
    })
  """
})

browser.get("https://www.zhihu.com/signin?next=%2F")

browser.find_element_by_css_selector(".SignFlow-tab.SignFlow-tab--active+.SignFlow-tab").click()
browser.find_element_by_css_selector(".SignFlow-accountInput.Input-wrapper input[type='text']").send_keys("16608006657")
browser.find_element_by_css_selector(".SignFlow-password input").send_keys("520*ihtxgq@ZH")

browser.find_element_by_css_selector(".Button.SignFlow-submitButton").click()

t_selector = Selector(text=browser.page_source)

#browser.quit()
