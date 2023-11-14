import pystray
from pystray import MenuItem as item
from PIL import Image
import sys
state = True
def menu_callback(icon, item):
    print(f"Выбран пункт меню: {item.text}")
def on_clicked(icon, item):
    global state
    state = not item.checked
def on_exit(icon, item):
    icon.stop()
    sys.exit()
#def createMenu():
image = Image.open("icon.png")
menu = (
    item("Пункт меню 1", menu_callback),
    item("Проверять объявления", on_clicked,checked=lambda item: state),
    item("Выход", on_exit)
)

# Создание иконки в трее
icon = pystray.Icon("name", image, "Заголовок", menu)
icon.run()
