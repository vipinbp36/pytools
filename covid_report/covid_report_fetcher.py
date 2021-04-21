from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import ctypes
import argparse
import os
import pytesseract
import time


def search_result(driver, srf_id):
    screenshot_file = os.getcwd() + "/my_screenshot.png"
    captcha_img = driver.find_element_by_xpath("//*[@id='imgCaptcha']")
    with open(screenshot_file, 'wb') as file:
        file.write(captcha_img.screenshot_as_png)

    text = pytesseract.image_to_string(screenshot_file)
    text = text.strip(".")
    text = text.strip()
    os.remove(screenshot_file)

    driver.find_element_by_xpath("//*[@id='txtIDorName']").send_keys(srf_id)
    driver.find_element_by_xpath("//*[@id='txtCaptcha']").send_keys(text)
    driver.find_element_by_xpath("//*[@id='GetReport']").click()
    time.sleep(3)
    result_list = []
    result_list.append(driver.find_element_by_xpath('//*[@id="alertSpn"]').text)
    result_list.append(driver.find_element_by_xpath('//*[@id="TestStatusPSpn"]').text)
    result_list.append(driver.find_element_by_xpath('//*[@id="TestStatusSpn"]').text)
    result = [x for x in result_list if x][0]
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--srfid', help='Provide the SRF ID')
    parser.add_argument('--interval', default=120, help='Enter the time interval between each retry')
    args = parser.parse_args()
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(executable_path="./drivers/chromedriver", options=chrome_options)
    driver.get("https://www.covidwar.karnataka.gov.in/service1")
    srf_id = args.srfid
    retry_interval = args.interval
    search_status = False
    result = ""

    while search_status == False:
        try:
            result = search_result(driver, srf_id)
            print("\nCovid Result: ",result)
            search_status = True
            while "result awaited" in result:
                try:
                    result = search_result(driver, srf_id)
                    if "result awaited" in result:
                        print("Waiting for Covid report. Retrying after few seconds..")
                        time.sleep(retry_interval)
                    else:
                        if os.name == "nt":
                            ctypes.windll.user32.MessageBoxA(0, result, "Covid Result", 4)
                        else:
                            command = "osascript -e \'Tell application \"System Events\" to display dialog \"" + result.replace(
                                "\'s", " is") + "\" with title \"Covid Result\"\'"
                            os.system(command)
                except:
                    print("Error (Most likely captcha error). Retrying")
                    driver.refresh()
            driver.close()
        except:
            print("Error (Most likely captcha error). Retrying")
            driver.refresh()


