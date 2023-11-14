from undetected_chromedriver import Chrome, ChromeOptions
from selenium.webdriver.remote.webdriver import By
import pystray
from pystray import MenuItem as item
from PIL import Image
import asyncio
import configparser
import time
import telegram
import sys
import threading
import pandas as pd
import numpy as np
import os
import configparser
from savetable import savetable


checkads = True
send_notification = True
exit=True
def on_clicked1(icon, item):
    global checkads
    checkads = not item.checked
def on_clicked2(icon, item):
    global send_notification
    send_notification = not item.checked
def on_exit(icon, item):
    global exit
    exit=False
    icon.stop()



image = Image.open("icon.png")
menu = (
    item("Проверять объявления", on_clicked1,checked=lambda item: checkads),
    item("Отправлять уведомления", on_clicked2,checked=lambda item: send_notification),
    item("Выход", on_exit)
)
icon = pystray.Icon("name", image, "Заголовок", menu)

async def main():
    options = ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.headless = True
    driver = Chrome(options=options)
    if not os.path.isfile('output.xlsx'):
        dff = pd.DataFrame(
            columns=["Ссылка", "Машина", "Цена", "Год выпуска", "Поколение", "Пробег", "История пробега", "ПТС",
                     "Владельцев по ПТС", "Состояние",
                     "Модификация", "Объём двигателя", "Тип двигателя", "Коробка передач", "Привод",
                     "Комплектация", "Тип кузова", "Цвет", "Руль", "VIN или номер кузова"])
    else:
        dff = pd.read_excel('output.xlsx', index_col=False)

    cfg = configparser.ConfigParser()
    cfg.read('config.ini')
    TOKEN = cfg.get('BOT', 'token')
    CHAT_ID = cfg.get('BOT', 'chat_id')
    bot = telegram.Bot(token=TOKEN)
    limit = int(cfg.get('LIMIT', 'limit'))

    while True and exit:
        if checkads:
            for option in cfg.options('REFS'):
                temp_df = pd.DataFrame(index=[0])
                path=cfg.get('REFS', option)
                driver.get(path)
                advertisements = driver.find_elements(By.XPATH,"//div[contains(@class, 'iva-item-titleStep-pdebR')]")
                refs=[]
                for ad in advertisements[:limit]:
                    element =  ad.find_element(By.XPATH, ".//a[contains(@class, 'styles-module-root-QmppR styles-module-root_noVisited-aFA10') and @itemprop='url' and @data-marker='item-title' and @rel='noopener']")
                    refs.append(element.get_attribute("href"))
                for ref in refs:
                    if (ref in dff['Ссылка'].values):
                        print('Найдено совпадение')
                        break
                    driver.get(ref)
                    price = driver.find_element(By.CSS_SELECTOR,"span.styles-module-size_xxxl-A2qfi").text
                    price = price.replace('&nbsp;',' ')
                    title = driver.find_element(By.CSS_SELECTOR,"h1.styles-module-root-TWVKW").text
                    title = title.replace('&nbsp;', ' ')
                    elements = driver.find_elements(By.XPATH,".//li[contains(@class, 'params-paramsList__item-appQw')]")
                    row=pd.DataFrame(index=[0])
                    row['Ссылка'] = ref
                    row['Машина'] = title
                    row['Цена'] = price
                    for i,element in enumerate(elements):
                        text = element.text
                        t=text.split(':')
                        t1=t[0].strip()
                        t2=t[1].strip()
                        row[t1]=t2
                    if send_notification:
                        await bot.send_message(chat_id=CHAT_ID, text=title+'\n'+price+'\n'+ref)
                    temp_df = pd.concat([temp_df,row]).reset_index(drop=True)
                if len(temp_df)>1:
                    dff = pd.concat([temp_df, dff]).reset_index(drop=True)
            dff = dff.dropna(subset=['Ссылка'])
            savetable('output.xlsx','output.xlsx',dff)
            print('Цикл завершен')
            time.sleep(10)
    driver.quit()
def run_main():
    asyncio.run(main())
def run_icon():
    icon.run()
icon_thread = threading.Thread(target=run_icon)
main_thread = threading.Thread(target=run_main)

icon_thread.start()
main_thread.start()

# Ожидание завершения основного потока
main_thread.join()

# Остановка иконки и ожидание завершения потока иконки
icon.stop()
icon_thread.join()