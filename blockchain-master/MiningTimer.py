import schedule
import time
import requests
import json

def job():
    print("I'm working...")
    url = 'http://localhost:5000/mine'
    # payload = json.load(open("request.json"))
    headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
    r = requests.get(url, headers=headers)
    print(r.json())

schedule.every(5).minutes.do(job)
# schedule.every(10).seconds.do(job)
# schedule.every().hour.do(job)
# schedule.every().day.at("10:30").do(job)

while 1:
    schedule.run_pending()
    time.sleep(1)