import firebase_api
import schedule
import time

def job():
    firebase_api.renewal()
    
everyday = schedule.every().day.at("06:01").do(job)
saturday = schedule.every().saturday.at("13:01").do(job)
sunday = schedule.every().sunday.at("13:01").do(job)

while True:
    schedule.run_pending()
    time.sleep(60)
