
import time
import json
from selenium import webdriver
from selenium.webdriver.support.ui import Select

values = {
    "old": {
        "teacher": {},
        "unit": {},
        "classroom": {}
    },

    "new": {
        "teacher": {},
        "unit": {},
        "classroom": {}
    },
}

drv = webdriver.Chrome()


def test(driver, tgt, tgt_url):
    global values

    driver.get("http://127.0.0.1:5502/web/index.html")
    time.sleep(0.5)
    driver.execute_script(f'app.fetchData("{tgt_url}")')
    time.sleep(0.5)

    select_teacher = Select(driver.find_element_by_id("units"))
    select_unit = Select(driver.find_element_by_id("teachers"))
    select_classroom = Select(driver.find_element_by_id("rooms"))

    for value in select_teacher.options[1:]:
        value = value.get_attribute("value")
        select_teacher.select_by_value(value)

        tbl = driver.find_element_by_id("maintable").get_attribute('innerHTML')
        values[tgt]["teacher"][value] = tbl

    for value in select_unit.options[1:]:
        value = value.get_attribute("value")
        select_unit.select_by_value(value)

        tbl = driver.find_element_by_id("maintable").get_attribute('innerHTML')
        values[tgt]["unit"][value] = tbl

    for value in select_classroom.options[1:]:
        value = value.get_attribute("value")
        select_classroom.select_by_value(value)

        tbl = driver.find_element_by_id("maintable").get_attribute('innerHTML')
        values[tgt]["classroom"][value] = tbl


test(drv, "old", "http://127.0.0.1:5503/old.json")
test(drv, "new", "http://127.0.0.1:5503/test.json")

drv.close()

with open("test_old.json", "w", encoding="UTF-8") as f:
    json.dump(values["old"], f)

with open("test_new.json", "w", encoding="UTF-8") as f:
    json.dump(values["new"], f)