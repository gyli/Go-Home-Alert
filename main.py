#!/usr/bin/python
# -*-coding:UTF-8 -*-

from datetime import datetime
import json
import requests
import schedule
import time


with open('conn.json', 'r') as conn_file:
    conn = json.load(conn_file)

end_time = datetime.strptime(conn['end_time'], '%H:%M').time()


def send_message(metro_time):
    request_url = 'https://api.mailgun.net/v2/{0}/messages'.format(conn['mail_domain'])
    request = requests.post(request_url, auth=('api', conn['mail_key']), data={
        'from': conn['mail_from'],
        'to': conn['mail_to'],
        'subject': 'Time to go home!',
        'text': 'You have {0} minutes for the metro.'.format(metro_time)
    })


def job():
    url = "https://api.wmata.com/StationPrediction.svc/json/GetPrediction/{0}".format(conn['metro_station'])
    headers = {'Host': 'api.wmata.com', 'api_key': conn['metro_api']}

    r = requests.get(url, headers=headers)

    metro_info = json.loads(r.text)

    metro_info_list = metro_info.get('Trains')

    time_list = [int(m.get('Min')) for m in metro_info_list if m.get('Line') == conn['metro_line'] and (m.get('DestinationCode') == conn['metro_destination'] or m.get('Group') == conn['metro_direction']) and m.get('Min').isdecimal()]

    # I need 8 minutes to walk to station and the time of a new train record is normally greater than 8
    if max(time_list) > 8:
        send_message(metro_time=max(time_list))
        raise SystemExit(0)


schedule.every().monday.tuesday.wednesday.thursday.friday.at(conn['start_time']).do(job)

while True:
    schedule.run_pending()

    # if end time passed and no message sent, quit anyway
    if end_time < datetime.now().time():
        raise SystemExit(0)

    time.sleep(20)
