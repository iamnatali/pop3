## POP3
студент: Первушина Наталия КН-203

##### Функции
* пользователь вводит e-mail и пароль и может получить содержимое письма

реализовано с помощью сокетов

##### Справка по использованию
* чтобы получить справку, необходимо запустить pop_main.py -h
* чтобы начать работу, нужно запустить pop_main.py с соответствующими аргументами
(приведены ниже)

usage: 
pop_main.py [-h] [-top TOP] [-all_message] [-all_text] [-from_h] [-to_h] [-subject] [-date]
                   
email password number

positional arguments:
  
  email         users email
  
  password      users password
  
  number        letter number from last to oldest

optional arguments:

  -h, --help    show this message and quit
  
  -top TOP      get certain number of SYMBOLS from letter's text
  
  -all_message  get text and download attachments
  
  NB: заголовки не включены в атрибут all_message, 
  чтобы получить их воспользуйтесь другими атрибутами
  
  -all_text     get message text without attachments
  
  -from_h       get header from
  
  -to_h         get header to
  
  -subject      get header subject
  
  -date         get header date
 
##### Пример использования
 
 pop_main.py -all_message -from_h myMail@yandex.ru 12345 2
