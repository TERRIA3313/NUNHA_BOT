import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import requests
from bs4 import BeautifulSoup
import datetime
import discord


cred = credentials.Certificate('nunha-bot-key.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://nunha-bot-default-rtdb.asia-southeast1.firebasedatabase.app/'
})


def island_split(row_data: str):
    island_kind = row_data[:2]
    island_name = row_data[2:]
    return island_kind, island_name


def renewal():
    KST = datetime.timezone(datetime.timedelta(hours=9))
    now = datetime.datetime.now(KST)
    hour = now.hour
    week = now.weekday()
    
    ref = db.reference("today_island")
    url = "https://kloa.gg"
    req = requests.get(url=url)
    soup = BeautifulSoup(req.content, "html.parser")
    weekend_day = soup.find("div", {"class": "grid lg:grid-cols-3 grid-cols-1 gap-5 lg:mx-[20px] mx-[14px] mt-[28px]"})
    data_dict = {}
    if week >= 5:
        count = 0
        for i in weekend_day:
            if now.hour >= 13 and count > 2:
                island_kind, island_name = island_split(i.get_text())
                data_dict[island_name] = island_kind
            elif now.hour < 13 and count <= 2:
                island_kind, island_name = island_split(i.get_text())
                data_dict[island_name] = island_kind
            count += 1
        ref.set(data_dict)
        
    else:
        for i in weekend_day:
            island_kind, island_name = island_split(i.get_text())
            data_dict[island_name] = island_kind
        ref.set(data_dict)
        
        
def get_island_url(island_name: str):
    ref = db.reference("island_img/" + island_name)
    data = ref.get()
    if data == None:
        data = "https://i.imgur.com/a2vIXu8.png"
    return data
            

def get_island_embed():
    ref = db.reference("today_island")
    data = ref.get()
    island_list = []
    for i in data.keys():
        island_kind = data[i]
        island_name = i
        embed = discord.Embed()
        embed.set_author(name=island_name, icon_url=get_island_url(island_name))
        embed.add_field(name="종류", value=island_kind)
        island_list.append(embed)
    return island_list