import schedule
import time


def thr():
    while True:
        schedule.run_pending()
        time.sleep(1)
