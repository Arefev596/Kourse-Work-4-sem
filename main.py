import tempfile
import os
import requests
import json
from tkinter import ttk
from PIL import ImageTk, Image
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox as mb
import sqlite3


def insert_in_table(num, name, sum, price):
    try:
        db = sqlite3.connect('venv/database.db')
        print("Подключение к SQLITE")
        cursor = db.cursor()
        query = """ CREATE TABLE IF NOT EXISTS Products (№ INTEGER, Name TEXT, Sum INTEGER, Price INTEGER) """
        query1 = """ INSERT INTO Products (№, Name, Sum, Price) VALUES(?, ?, ?, ? ) """
        data_tuple = (num, name, sum, price)
        cursor.execute(query)
        cursor.execute(query1, data_tuple)

        lst = []
        for row in db.execute('SELECT name FROM Products'):
            lst.append(row)
        with open("lex.txt", 'w') as file:
            for x in lst:
                for n in x:
                    file.write(str(n) + '\n')

        db.commit()
        cursor.close()

    except sqlite3.Error as error:
        print("Ошибка в работе с SQLITE ", error)
    finally:
        if db:
            db.close()
            print("Соединение закрыто")


logwin = tk.Tk()
logwin.config(bg='#DFE1FF')
logwin.title("Сканирование чеков")
logwin.geometry(f"450x250+100+100")
logwin.minsize(300, 400)
# logwin.maxsize(1200,600)
logwin.resizable(False, False)
logwin.grid_columnconfigure(0, minsize=150)
logwin.grid_columnconfigure(1, minsize=170)
logwin.grid_columnconfigure(2, minsize=150)

menubar = tk.Menu(logwin)
logwin.config(menu=menubar)


def opennewdialog():
    newbox = mb.showinfo(title='Справка', message="""
    Программа Арефьева А. Курсовая работа за 4 семестр.
    """)


menubar.add_command(label='Справка', command=opennewdialog)


def openfn():
    filename = filedialog.askopenfilename(title='Выберите файл jpg', filetypes=[('*.jpeg *.jpg')])

    url = 'https://proverkacheka.com/api/v1/check/get'
    data = {'token': '14023.uQ0uGby7nN3VXKV99'}
    # print(filename)
    files = {'qrfile': open(filename, 'rb')}
    r = requests.post(url, data=data, files=files)
    py_data = json.loads(r.text)

    tempList = []

    with open('Your_check.json', 'w') as f:
        json.dump(py_data, f, indent=3, ensure_ascii=False)

    with open("Your_check.json") as jsonFile:
        data1 = json.load(jsonFile)
        jsonItems = data1["data"]["json"]["items"]

    for item in data1["data"]["json"]["items"]:
        if (item == ['nds']):
            del item['nds']
        if (item == ['ndsSum']):
            del item['ndsSum']
        if (item == ['paymentType']):
            del item['paymentType']
        if (item == ['modifiers']):
            del item['modifiers']
        tempList.append([item['name'], item['sum'], item['price']])

    logwin.geometry(f"805x550+100+100")

    def show():
        for i, (name, sum, price) in enumerate(tempList, start=1):
            listBox.insert("", "end", values=(i, name, sum, price))
            insert_in_table(i, name, sum, price)

    cols = ('№', 'Название', 'Сумма, коп.', 'Цена, коп.')
    listBox = ttk.Treeview(logwin, columns=cols, show='headings')
    for col in cols:
        listBox.heading(col, text=col)
    listBox.grid(row=3, column=0, columnspan=3)

    showScores = tk.Button(logwin, text="Показать данные чека", width=20, command=show).grid(row=4, column=0)
    tk.Label(logwin, text="Сумма чека: ", width=11).grid(row=4, column=1, sticky="e")
    tk.Label(logwin, text=data1["data"]["json"]["totalSum"], width=20).grid(row=4, column=2)
    tk.Button(logwin, text="Распечатать таблицу", width=20, bg="white", fg="Black", activebackground="grey",
              command=lambda: os.startfile("lex.txt", "print")).grid(row=5, column=0)
    return filename


def open_img():
    x = openfn()
    img = Image.open(x)
    img = img.resize((230, 230), Image.ANTIALIAS)
    img = ImageTk.PhotoImage(img)
    panel = tk.Label(logwin, image=img)
    panel.image = img
    tk.Label(logwin, text="Ваш чек: ", width=13, font=('bold')).grid(row=1, column=0)
    panel.grid(row=1, column=1, stick='we')


btn_load = tk.Button(logwin, text='Загрузить фото чека', bg="white", fg="Black", activebackground="grey",
                     command=open_img).grid(row=2, column=0, pady=25, columnspan=3, rowspan=2, stick='s')

logwin.mainloop()
