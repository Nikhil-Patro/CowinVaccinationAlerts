import requests
from datetime import datetime
import calendar
import time
import schedule
import os
from dotenv import load_dotenv
load_dotenv()

from requests.models import Response
API_TOKEN = os.getenv("API_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
telegram_api_url = "https://api.telegram.org/bot"+API_TOKEN+"/sendMessage?chat_id=@"+CHAT_ID+"&text="

base_cowin_url = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict"
now = datetime.now()
today_date = now.strftime("%d-%m-%Y")
#Ernakulam = 307, Khurda = 446
district_ids = [307]

def fetch_data_for_district(district_ids):
    for district_id in district_ids:
        query_params = "?district_id={}&date={}".format(district_id, today_date)
        final_url = base_cowin_url + query_params
        response = requests.get(final_url)
        extract_data(response)

def extract_data(response):
    count = 1
    response_json = response.json()
    for center in response_json["centers"]:
        message = "*{}) {}* \nAddress: {} {} \n-----------------------\n".format(count, center["name"], center["address"], center["pincode"])
        for session in center["sessions"]:
            if(session["available_capacity"] > 0):
                datetime_obj = datetime.strptime(session["date"], "%d-%m-%Y")
                message += "Date: *{} ({})* \nTiming: *{} - {}* \nVaccine: *{}* \nAge: *{}+ ({})* \nSlots Available: 1st Dose: *{}*, 2nd Dose: *{}* \n======================\n\n"
                message = message.format(session["date"], calendar.day_name[datetime_obj.weekday()], center["from"], center["to"], 
                session["vaccine"], session["min_age_limit"], center["fee_type"], session["available_capacity_dose1"]
                , session["available_capacity_dose2"])
        if(message[-1]=='\n' and message[-2]=='\n' ):
            prev_message = message
            send_message_telegram(message)
            count = count + 1
            time.sleep(4)

def send_message_telegram(message):
    final_telegram_url = telegram_api_url + message
    final_telegram_url +="&parse_mode=markdown"
    response = requests.get(final_telegram_url)
    print(response)

if __name__ == "__main__":
    schedule.every(3600).seconds.do(lambda: (fetch_data_for_district(district_ids)))
while True:
    schedule.run_pending()
    time.sleep(1)
