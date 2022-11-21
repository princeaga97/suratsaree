from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import selenium
from bs4 import BeautifulSoup as BSoup
from selenium.webdriver.common.action_chains import ActionChains
import time
import urllib.request
from PIL import Image ,ImageEnhance 
import pytesseract
import glob
import os
import pathlib


def add_category(name, parent):
    url = "http://127.0.0.1:8000/admin/core/category/add/"
    driver.get(url)
    driver.find_element_by_name("name").send_keys(name)
    driver.find_element_by_name("slug").send_keys(name.replace(" ","_"))
    s1 = Select(driver.find_element_by_name('parent'))
    s1.select_by_value(str(parent))
    driver.find_element_by_name("slug").send_keys(Keys.RETURN)



url = "http://127.0.0.1:8000/admin/core/item/add/"
driver = webdriver.Firefox()
driver.maximize_window()
driver.get(url)
time.sleep(2)
driver.find_element_by_name("username").send_keys("Prince")
driver.find_element_by_name("username").send_keys(Keys.RETURN)
time.sleep(2)
driver.find_element_by_name("password").send_keys("9653")
driver.find_element_by_name("password").send_keys(Keys.RETURN)
time.sleep(2)
path = pathlib.Path().absolute()
category = 7
for folder in glob.glob(str(path.parent)+"/Hemant/*"):
    for subfolder in  glob.glob(folder+"/*"):
        mixname =subfolder.split("/")[-1]
        DesignName , Price = mixname.split("_")
        parent_category = subfolder.split("/")[-2]
        if parent_category == "Print_Saree":
            add_category(DesignName,2)
        elif parent_category == "Work_Saree":
            add_category(DesignName,7)
        elif parent_category == "Work_Dupatta":
            add_category(DesignName,5)
        print("category added successfully")
        category =category+1
        count = (category-8)*300
        for photo in glob.glob(subfolder+"/*"):
            count = count+1
            driver.get(url)
            driver.find_element_by_name("title").send_keys(DesignName+ str(count).zfill(3))
            driver.find_element_by_name("price").send_keys(Price)
            driver.find_element_by_name("discount_price").send_keys(Price)
            s1 = Select(driver.find_element_by_name('category'))
            s1.select_by_value(str(category))
            driver.find_element_by_name("slug").send_keys(DesignName.replace(" ","_")+ str(count).zfill(3))
            driver.find_element_by_name("description").send_keys(DesignName+ str(count).zfill(3))
            driver.find_element_by_name("image").send_keys(photo)
            driver.find_element_by_name("slug").send_keys(Keys.RETURN)
            time.sleep(2)
    








