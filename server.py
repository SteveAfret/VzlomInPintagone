from flask import Flask, request, render_template, redirect
from random import *
import sqlite3

app = Flask(__name__, static_folder="images")

def url_prefix():
  return '/pintagone' if request.environ.get('SERVER_NAME') == 'hmsm.ru' else ''

# Для Запуска На Сайте
@app.context_processor
def template_vars():
  return dict(url_prefix=url_prefix())

bukvi = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
cifri = '0123456789'
vse_images = ['viviviviDancing.webp','vzlomm.jpg','King.png','How.png','gun.png', 'Eyes.png']

generated_password = ''

# Функция Установки Подключения
def get_connection():
  connection = sqlite3.connect('my_database.db')
  return connection

all_hints = []

# Функция Получения Подсказок
def get_hint(pwd):
  nomer_mesta = randint(0, len(generated_password)-1)
  hints = [
    'Символ На Месте ' + str(nomer_mesta+1) + ': ' + str(pwd[nomer_mesta]),
    'Символ ' + str(pwd[nomer_mesta]) + ' Встречается ' + str(pwd.count(pwd[nomer_mesta])) + ' Раз\а',
    'Длина Пароля: ' + str(len(generated_password)),
    'Символ На Месте ' + str(nomer_mesta+1) + ': ' + str(pwd[nomer_mesta]),
    'Символ ' + str(pwd[nomer_mesta]) + ' Встречается ' + str(pwd.count(pwd[nomer_mesta])) + ' Раз\а',
    'nope_C',
    'nope_B']
  final_hint = hints[randint(0,6)]
  if final_hint == 'nope_C':
    for i in cifri:
      if i not in generated_password:
        final_hint = 'В Пароле Нет Цифр'
      else:
        final_hint = hints[randint(0,4)]
        break
  if final_hint == 'nope_B':
    for i in bukvi:
      if i not in generated_password:
        final_hint = 'В Пароле Нет Букв'
      else:
        final_hint = hints[randint(0,4)]
        break  
  if final_hint not in all_hints:  
    return final_hint
  else:
    return 'Бзз! Неправильно!'

# Функция Всего
@app.route('/')
def hello():
  password = request.args.get('password', "")
  if password != '':
    data_write(password)
  if password == generated_password:
    create_password()
    return redirect(url_prefix()+'/you_win', code=302)
  hint = get_hint(generated_password)
  which_one = randint(0,5)
  image = vse_images[which_one]
  colour = get_colour()
  if hint not in all_hints and password != '':     
    all_hints.append(hint)
    connection = get_connection()
    with connection:
      connection.cursor().execute('INSERT INTO Hints (pass, hintes) VALUES (?, ?)',
                        (password, hint))
      connection.commit()

  return render_template('hello.html', password=password, hint=hint, image=image, colour=colour)

# Функция Победы
@app.route('/you_win')
def you_win():
  colour = get_colour()
  return render_template('win.html', colour=colour)

# Функция Перезаписывающая Пароль
@app.route('/reset')
def reset_password():
  create_password()
  return redirect(url_prefix()+'/', code=302)

# Функция Удаляющая Историю Попыток
@app.route('/delete')
def delete_history():
  create_password()
  connection = get_connection()
  with connection:
    cursor = connection.cursor()  
    cursor.execute('DELETE FROM Results')
    connection.commit()
  return redirect(url_prefix()+'/', code=302)

# Функция Удаляющая Историю Подсказок
@app.route('/delete_hints')
def delete_hints():
  connection = get_connection()
  with connection:
    cursor = connection.cursor()  
    cursor.execute('DELETE FROM hints')
    connection.commit()
  return redirect(url_prefix()+'/', code=302)

# Функция Создающая Пароль
def create_password():
  global generated_password
  generated_password = ''
  global all_hints
  all_hints = []
  dlina = randint(4,10)
  for i in range(dlina):
    kto = randint(1,2)
    if kto == 1:
      symb = bukvi[randint(0,25)]
      generated_password += symb
    else:
      symb = cifri[randint(0,9)]
      generated_password += symb
  print(generated_password) 
  
# Функция Просмотра Истории Попыток
@app.route('/history')
def history():
  connection = get_connection()
  with connection:
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM Results')
    results = cursor.fetchall()  
  colour = get_colour()
  return render_template('history.html', results=results, colour=colour)

# Функция Просмотра Истории Подсказок
@app.route('/hints')
def hints():
  connection = get_connection()
  with connection:
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM Hints')
    hints = cursor.fetchall()  
  colour = get_colour()
  return render_template('hints.html', hints=hints, colour=colour)

# Функция Записи Попыток
def data_write(password):
  connection = get_connection()
  with connection:
    connection.cursor().execute('INSERT INTO Results (generated_password, users_input) VALUES (?, ?)',
                     (generated_password, password))
    connection.commit() 

# Функция Случайного Цвета Фона
def get_colour():
  cifri = ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9')
  bukvi = ('A', 'B', 'C', 'D', 'E', 'F')
  actbacklcolor = '#'
  for i in range(6):
    cif_or_buk = randint(1, 2)
    if cif_or_buk == 1:
      cifra = randint(0, 9)
      newsymbcolor = cifri[cifra]
      actbacklcolor += newsymbcolor
    if cif_or_buk == 2:
      bukva = randint(0, 5)
      newsymbcolor = bukvi[bukva]
      actbacklcolor += newsymbcolor  
  return actbacklcolor

create_password()

connection = get_connection()
connection.cursor().execute('''CREATE TABLE IF NOT EXISTS Results(generated_password TEXT NOT NULL, users_input TEXT NOT NULL)''')
connection.commit()
connection = get_connection()
connection.cursor().execute('''CREATE TABLE IF NOT EXISTS Hints(pass TEXT NOT NULL, hintes TEXT NOT NULL)''')
connection.commit()

# Команда Для Комаендой Строки:
# D:\dev\Python310\python.exe -m flask --app server.py --debug run
if __name__ == 'main':
  app.run(debug=True)
