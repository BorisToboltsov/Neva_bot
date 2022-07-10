KEY_CONSTANT = "file.json"  # Абсолютный путь до файла авторизации google
KEY_PATH = ""  # абсолютный путь до директории в которой находится программа
SHEET_FOOD = "График Питания 2022"  # Название таблицы питания
SHEET_TRANSPORT = "2022 Транспорт"  # Название таблицы транспорт
SHEET_EXCURSIONS = "Копия Экскурсии для отелей 2022"  # Название таблицы экскурсий
TOKEN_TELEGRAM = ""
ACCESS = {'Имя': 'telegram_id'}  # Словарь авторизавнных пользователей, в формате 'фио': id_telegram
SENT_REPORT = ACCESS['Имя']  # Кому будет отправляться отчет о доставке сообщений гидам
SENDING_TIME = '18:00'  # Время отправки сообщения гидам

WEBHOOK_SSL_CERT = 'webhook_cert.pem'  # Path to the ssl certificate
WEBHOOK_SSL_PRIV = 'webhook_pkey.pem'  # Path to the ssl private key
WEBHOOK_HOST = 'bot.yandex.ru'  # Домен на котором находится бот
WEBHOOK_PORT = 8443  # 443, 80, 88 or 8443 (port need to be 'open') порт должен быть не занят каким-нибудь веб сервером.
WEBHOOK_LISTEN = '0.0.0.0'  # In some VPS you may need to put here the IP addr. На моем vps при 0.0.0.0 работает.
