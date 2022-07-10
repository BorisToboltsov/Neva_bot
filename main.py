import ssl
import threading
import settings
import telebot
import schedule
from aiohttp import web
from connect_telegram import bot
from shedule import thr
from send_message import send_message

WEBHOOK_URL_BASE = f"https://{settings.WEBHOOK_HOST}:{settings.WEBHOOK_PORT}"
WEBHOOK_URL_PATH = f"/{settings.TOKEN_TELEGRAM}/"

app = web.Application()

 
# Process webhook calls
async def handle(request):
    if request.match_info.get('token') == bot.token:
        request_body_dict = await request.json()
        update = telebot.types.Update.de_json(request_body_dict)
        bot.process_new_updates([update])
        return web.Response()
    else:
        return web.Response(status=403)


app.router.add_post('/{token}/', handle)

# schedule.every(1).minutes.do(send_message, settings.SENT_REPORT)
# Set shedule
# Отправка сообщения по заданному времени.
schedule.every().day.at(settings.SENDING_TIME).do(send_message, settings.SENT_REPORT)
threading.Thread(target=thr).start()

# Remove webhook, it fails sometimes the set if there is a previous webhook
bot.remove_webhook()

# Set webhook
bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH,
                certificate=open(settings.WEBHOOK_SSL_CERT, 'r'))

# Build ssl context
context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
context.load_cert_chain(settings.WEBHOOK_SSL_CERT, settings.WEBHOOK_SSL_PRIV)

# Start aiohttp server
web.run_app(
    app,
    host=settings.WEBHOOK_LISTEN,
    port=settings.WEBHOOK_PORT,
    ssl_context=context,
)
