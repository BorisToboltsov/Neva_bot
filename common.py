import datetime


def date():
    """Даты"""
    list_month = {'January': 'Январь', 'February': 'Февраль', 'March': 'Март', 'April': 'Апрель',
                  'May': 'Май', 'June': 'Июнь', 'July': 'Июль', 'August': 'Август',
                  'September': 'Сентябрь', 'October': 'Октябрь', 'November': 'Ноябрь', 'December': 'Декабрь'}
    today = datetime.datetime.today()
    tomorrow = today + datetime.timedelta(days=1)
    next_month_ru = list_month[tomorrow.strftime("%B")]
    tomorrow = tomorrow.strftime("%d.%m")
    today = today.strftime("%d.%m")

    return next_month_ru, tomorrow, list_month, today
