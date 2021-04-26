import sys
from selenium import webdriver
import chromedriver_autoinstaller
from selenium.webdriver.chrome.options import Options
import os
import pytesseract
import time
import tkinter as tk


def clear_text(e):
    srf_id = e[0]
    retry_dur = e[1]
    srf_id.delete(0,tk.END)
    retry_dur.delete(0,tk.END)

def quit_program(root):
    root.destroy()
    sys.exit()

def create_form(root):
    root.geometry("250x100+600+300")
    root.title("Fetch Covid Report")
    tk.Label(root, text="SRF ID", pady=4, padx=4).grid(row=0)
    tk.Label(root, text="Retry Duration", pady=4, padx=4).grid(row=1)
    srf_id = tk.Entry(root)
    retry_dur = tk.Entry(root)
    retry_dur.insert(tk.END,"120")
    srf_id.grid(row=0, column=1, pady=4, padx=4, columnspan=3)
    retry_dur.grid(row=1, column=1, pady=4, padx=4, columnspan=3)
    tk.Button(root,text='Accept',command=root.quit).grid(row=3,column=1,sticky=tk.W,pady=10)
    tk.Button(root,text='Clear', command=(lambda e=(srf_id,retry_dur): clear_text(e))).grid(row=3,column=2,sticky=tk.W,pady=10)
    tk.Button(root,text='Quit',command=(lambda e=root: quit_program(e))).grid(row=3,column=3,pady=10)
    root.mainloop()
    return srf_id.get(),retry_dur.get()


def search_result(driver, srf_id):
    screenshot_file = os.getcwd() + "/my_screenshot.png"
    captcha_img = driver.find_element_by_xpath("//*[@id='imgCaptcha']")
    with open(screenshot_file, 'wb') as file:
        file.write(captcha_img.screenshot_as_png)

    if os.name == "nt":
        pytesseract.pytesseract.tesseract_cmd = '.\\tesseract\\tesseract.exe'
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

def covid_result_window(result_root):
    result_root.geometry("250x75+600+300")
    result_root.title("Covid Report")
    tk.Label(result_root, text="Your Covid Report is: \n"+result).pack()
    tk.Button(result_root, text="ok", command=result_root.destroy,width=10).pack()
    result_root.mainloop()

if __name__ == '__main__':
    root = tk.Tk()
    srf_id,retry_interval = create_form(root)
    root.destroy()
    print(srf_id,retry_interval)
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chromedriver_autoinstaller.install(cwd=True)
    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://www.covidwar.karnataka.gov.in/service1")
    search_status = False
    result = ""
    result_root = tk.Tk()
    while search_status == False:
        try:
            result = search_result(driver, srf_id)
            print("\nCovid Result: ",result)
            search_status = True
            if "result awaited" not in result:
                covid_result_window(result_root)
            else:
                while "result awaited" in result:
                    try:
                        result = search_result(driver, srf_id)
                        if "result awaited" in result:
                            print("Waiting for Covid report. Retrying after few seconds..")
                            time.sleep(int(retry_interval))
                        else:
                            covid_result_window(result_root)
                    except:
                        print("Error (Most likely captcha error). Retrying")
                        driver.refresh()
            driver.quit()
        except:
            print("Error (Most likely captcha error). Retrying")
            driver.refresh()