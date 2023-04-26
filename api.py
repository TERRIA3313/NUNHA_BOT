import discord
from discord.commands import Option
from discord.ui import Button, View, Item
import requests
from bs4 import BeautifulSoup
import datetime


key = "Secret"

class StoneView(View):
    def __init__(self, *items: Item):
        super().__init__(*items, timeout=None)
        self.ctx = None
        self.embed = None
        self.data = None
        self.stone_1_max = 10
        self.stone_1_now = 0
        self.stone_1_name = None
        self.stone_2_max = 10
        self.stone_2_now = 0
        self.stone_2_name = None
        self.stone_3_max = 10
        self.stone_3_now = 0
        self.stone_3_name = None
        self.ansi_start = "```ansi\n"
        self.ansi_end = "\n```"
    
    def set_value(self, ctx, embed, stone_data):
        self.ctx = ctx
        self.embed = embed
        self.data = stone_data

    @discord.ui.button(label="1번 각인 세공", custom_id="stone_1_button", style=discord.ButtonStyle.primary)
    async def party_in_button_callback(self, button, interaction):
        if interaction.user == self.ctx.author:
            if self.stone_1_max > 0:
                dic = self.embed.to_dict()
                if self.stone_1_name == None:
                    self.stone_1_name = str(dic['fields'][1]['name'])
                dic = self.embed.to_dict()
                chance = str(dic['fields'][0]['value'])[:-1]
                stone_data = self.data[0]
                cutting_data, cutting_chance, times = Cutting(stone_data, int(chance))
                self.data[0] = cutting_data
                self.stone_1_now += times
                ansi_data = ReplaceStr(cutting_data)
                data = self.ansi_start + ansi_data + self.ansi_end
                self.embed.set_field_at(index=0, name="확률", value=cutting_chance, inline=False)
                self.embed.set_field_at(index=1, name=self.stone_1_name + " " + str(self.stone_1_now), value=data, inline=False)
                self.stone_1_max -= 1
                if self.stone_1_max == 0:
                    self.children[0].label = "세공 완료"
                    self.children[0].disabled = True
                await interaction.response.edit_message(embeds=[self.embed], view=self)
        else:
            await interaction.response.send_message("본인 돌이 아니면 세공할 수 없습니다.", ephemeral=True)

    @discord.ui.button(label="2번 각인 세공", custom_id="stone_2_button", style=discord.ButtonStyle.primary)
    async def party_out_button_callback(self, button, interaction):
        if interaction.user == self.ctx.author:
            if self.stone_2_max > 0:
                dic = self.embed.to_dict()
                if self.stone_2_name == None:
                    self.stone_2_name = str(dic['fields'][2]['name'])
                chance = str(dic['fields'][0]['value'])[:-1]
                stone_data = self.data[1]
                cutting_data, cutting_chance, times = Cutting(stone_data, int(chance))
                self.data[1] = cutting_data
                self.stone_2_now += times
                ansi_data = ReplaceStr(cutting_data)
                data = self.ansi_start + ansi_data + self.ansi_end
                self.embed.set_field_at(index=0, name="확률", value=cutting_chance, inline=False)
                self.embed.set_field_at(index=2, name=self.stone_2_name + " " + str(self.stone_2_now), value=data, inline=False)
                self.stone_2_max -= 1
                if self.stone_2_max == 0:
                    self.children[1].label = "세공 완료"
                    self.children[1].disabled = True
                await interaction.response.edit_message(embeds=[self.embed], view=self)
        else:
            await interaction.response.send_message("본인 돌이 아니면 세공할 수 없습니다.", ephemeral=True)

    @discord.ui.button(label="디버프 각인 세공", custom_id="stone_3_button", style=discord.ButtonStyle.danger)
    async def cancel_button_callback(self, button, interaction):
        if interaction.user == self.ctx.author:
            if self.stone_3_max > 0:
                dic = self.embed.to_dict()
                if self.stone_3_name == None:
                    self.stone_3_name = str(dic['fields'][3]['name'])
                chance = str(dic['fields'][0]['value'])[:-1]
                stone_data = self.data[2]
                cutting_data, cutting_chance, times = Cutting(stone_data, int(chance))
                self.data[2] = cutting_data
                self.stone_3_now += times
                ansi_data = ReplaceStr(cutting_data)
                data = self.ansi_start + ansi_data + self.ansi_end
                self.embed.set_field_at(index=0, name="확률", value=cutting_chance, inline=False)
                self.embed.set_field_at(index=3, name=self.stone_3_name + " " + str(self.stone_3_now), value=data, inline=False)
                self.stone_3_max -= 1
                if self.stone_3_max == 0:
                    self.children[2].label = "세공 완료"
                    self.children[2].disabled = True
                await interaction.response.edit_message(embeds=[self.embed], view=self)
        else:
            await interaction.response.send_message("본인 돌이 아니면 세공할 수 없습니다.", ephemeral=True)


class PartyView(View):
    def __init__(self, *items: Item):
        super().__init__(*items, timeout=None)
        self.ctx = None
        self.embed = None
    
    def set_value(self, ctx, embed):
        self.ctx = ctx
        self.embed = embed

    @discord.ui.button(label="파티 참가", custom_id="party_in_button", style=discord.ButtonStyle.primary)
    async def party_in_button_callback(self, button, interaction):
        if interaction.user != self.ctx.author:
            dic = self.embed.to_dict()
            members = str(dic['fields'][3]['value']).split("\n")
            if str(interaction.user) in members:
                await interaction.response.send_message("이미 있으시네요", ephemeral=True)
            else:
                modal = discord.ui.Modal(title="참가신청")
                modal.add_item(discord.ui.InputText(label="캐릭명"))

                async def callback(interactions):
                    job, level, error = get_job(key, str(modal.children[0].value))
                    if error:
                        await interaction.response.send_message("오류입니다. 입력값을 확인하거나 다시 입력해 주세요.", ephemeral=True)
                    else:
                        values = str(dic['fields'][3]['value']) + "\n" + str(modal.children[0].value) + " - " + level + " - " + job
                        self.embed.set_field_at(index=3, name="공대원", value=values, inline=False)
                        await interactions.response.edit_message(embeds=[self.embed], view=self)
                modal.callback = callback
                await interaction.response.send_modal(modal)
        else:
            await interaction.response.send_message("공대장은 추가로 참가할 수 없습니다.", ephemeral=True)


    @discord.ui.button(label="참가 취소", custom_id="party_out_button", style=discord.ButtonStyle.primary)
    async def party_out_button_callback(self, button, interaction):
        if interaction.user != self.ctx.author:
            dic = self.embed.to_dict()
            members = str(dic['fields'][3]['value']).split("\n")

            modal = discord.ui.Modal(title="취소신청")
            modal.add_item(discord.ui.InputText(label="캐릭명"))

            async def callback(interactions):
                job, level = get_job(key, str(modal.children[0].value))
                if str(str(modal.children[0].value) + " - " + level + " - " + job) in members:
                    members.remove(str(str(modal.children[0].value) + " - " + level + " - " + job))
                    values = "\n".join(members)
                    self.embed.set_field_at(index=3, name="공대원", value=values, inline=False)
                    await interactions.response.edit_message(embeds=[self.embed], view=self)
                else:
                    await interactions.response.send_message("파티에 없습니다", ephemeral=True)

            modal.callback = callback
            await interaction.response.send_modal(modal)
        else:
            await interaction.response.send_message("공대장은 참가 취소할 수 없습니다. 모집 취소를 해 주세요.", ephemeral=True)

    @discord.ui.button(label="모집 취소", custom_id="cancel_button", style=discord.ButtonStyle.danger)
    async def cancel_button_callback(self, button, interaction):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("권한 없음!", ephemeral=True)
        else:
            for i in self.children:
                i.label = "취소됨"
                i.disabled = True
            await interaction.response.edit_message(view=self)


class StoneMaking(discord.ui.Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.add_item(discord.ui.InputText(label="각인 1"))
        self.add_item(discord.ui.InputText(label="각인 2"))
        self.add_item(discord.ui.InputText(label="감소 각인"))
        self.ctx = None
        
    def set_ctx(self, ctx):
        self.ctx = ctx

    async def callback(self, interactions):
        embed = discord.Embed(title=f"{self.ctx.author.display_name}님의 돌")
        embed.set_author(name="돌 깎기 시뮬레이터", icon_url=self.ctx.author.display_avatar)
        embed.add_field(name="확률", value="75%", inline=False)
        embed.add_field(name=str(self.children[0].value), value="```ansi\n឵\u001b[1;34m◇◇◇◇◇◇◇◇◇◇\u001b[0m\n```", inline=False)
        embed.add_field(name=str(self.children[1].value), value="```ansi\n឵\u001b[1;34m◇◇◇◇◇◇◇◇◇◇\u001b[0m\n```", inline=False)
        embed.add_field(name=str(self.children[2].value), value="```ansi\n឵\u001b[1;34m◇◇◇◇◇◇◇◇◇◇\u001b[0m\n```", inline=False)
        
        view = StoneView()
        stone_data = ["0000000000", "0000000000", "0000000000"]
        view.set_value(self.ctx, embed, stone_data)
        
        await interactions.response.send_message(embeds=[embed], view=view)


class PartyMaking(discord.ui.Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.add_item(discord.ui.InputText(label="캐릭명"))
        self.add_item(discord.ui.InputText(label="목표"))
        self.add_item(discord.ui.InputText(label="출발 시각"))
        self.ctx = None
        
    def set_ctx(self, ctx):
        self.ctx = ctx
    
    async def callback(self, interactions):
        job, level, error = get_job(key, str(self.children[0].value))
        if error:
            await interactions.response.send_message("오류입니다. 입력값을 확인하거나 다시 입력해 주세요.", ephemeral=True)
        else:
            value = str(self.children[0].value) + " - " + level + " - " + job
            embed = discord.Embed(title="레이드 모집")
            embed.set_author(name=f"{self.ctx.author.display_name}님의 파티", icon_url=self.ctx.author.display_avatar)
            embed.add_field(name="레이드 목표", value=str(self.children[1].value), inline=False)
            embed.add_field(name="공대장 이름", value=str(self.children[0].value), inline=False)
            embed.add_field(name="출발시각", value=str(self.children[2].value), inline=False)
            embed.add_field(name="공대원", value=value, inline=False)

            view = PartyView()
            view.set_value(self.ctx, embed)

            await interactions.response.send_message(embeds=[embed], view=view)
    

def Cutting(data: str, chance: int):
    rand_data = random.randrange(1, 101)
    chance_data = chance
    cutting_option = True
    times = 0
    tmp = ""
    for i in data:
        if i == "0" and cutting_option:
            if rand_data <= chance_data:
                tmp += "1"
                if chance_data != 25:
                    chance_data -= 10
                times = 1
            else:
                tmp += "2"
                if chance_data != 75:
                    chance_data += 10
            cutting_option = False
        else:
            tmp += i
    chance_data = str(chance_data) + "%"
    return tmp, chance_data, times


def ReplaceStr(data: str):
    tmp = ""
    for i in data:
        if i == "0":
            tmp += "\u001b[1;34m◇\u001b[0m"
        elif i == "1":
            tmp += "\u001b[1;34m◆\u001b[0m"
        elif i == "2":
            tmp += "\u001b[1;31m◆\u001b[0m"
    return tmp


def auction(input_gold):
    target = input_gold
    gold = int(target * 0.83 - 1)
    profit = int((target - gold) - (target * 0.125))

    beat_gold = int(gold * 0.9090909) + 1
    after_gold = int(beat_gold * 1.1)

    result = ">>> **경매장 가격 : " + str(target) + "G\n\n추천 입찰가 : " + str(gold) + "G\n순이익 : " + str(
        profit) + "G\n\n선점 입찰가 : " + str(beat_gold) + "G\n다음 입찰가 : " + str(after_gold) + "G**"
    return result


def get_gold(level_data: float):
    gold = 0
    gold_list = []
    raid_counter = 3
    if level_data < 1370:
        if 340 <= level_data < 840:
            gold += 80
            gold_list.append("(어비스 던전)고대유적 엘베리아")

        if 460 <= level_data < 960:
            gold += 80
            gold_list.append("(어비스 던전)몽환의 궁전")

        if 840 <= level_data < 1325:
            gold += 100
            gold_list.append("(어비스 던전)오만의 방주")

        if 960 <= level_data < 1370:
            gold += 100
            gold_list.append("(어비스 던전)낙원의 문")

        if 1325 <= level_data < 1370:
            gold += 500
            gold_list.append("(어비스 던전)오레하의 우물 노말")

    else:
        if 1370 <= level_data < 1415:
            gold += 700
            gold_list.append("(어비스 던전)오레하의 우물 하드")

        if 1385 <= level_data < 1475:
            gold += 1000
            gold_list.append("(어비스 레이드)아르고스")

        # 볼다이크
        if 1600 <= level_data:
            if 1620 <= level_data:
                gold += 11000
                gold_list.append("(어비스 던전)볼다이크 하드")
            else:
                gold += 7500
                gold_list.append("(어비스 던전)볼다이크 노말")
            raid_counter -= 1

        # 일리아칸
        if 1580 <= level_data:
            if 1600 <= level_data:
                gold += 7500
                gold_list.append("(군단장 레이드)일리아칸 하드")
            elif 1580 <= level_data < 1600:
                gold += 5500
                gold_list.append("(군단장 레이드)일리아칸 노말")
            raid_counter -= 1

        # 카양겔
        if 1540 <= level_data:
            if 1580 <= level_data:
                gold += 5500
                gold_list.append("(어비스 던전)카양겔 하드")
            else:
                gold += 4500
                gold_list.append("(어비스 던전)카양겔 노말")
            raid_counter -= 1

        # 아브렐슈드
        if 1490 <= level_data:
            if 1540 <= level_data:
                gold += 5500
                gold_list.append("(군단장 레이드)아브렐슈드 1~2관문 하드")
            elif 1490 <= level_data:
                gold += 4500
                gold_list.append("(군단장 레이드)아브렐슈드 1~2관문 노말")

            if 1550 <= level_data:
                gold += 2000
                gold_list.append("(군단장 레이드)아브렐슈드 3~4관문 하드")
            elif 1500 <= level_data:
                gold += 1500
                gold_list.append("(군단장 레이드)아브렐슈드 3~4관문 노말")

            if 1560 <= level_data:
                gold += 3000
                gold_list.append("(군단장 레이드)아브렐슈드 5~6관문 하드")
            elif 1520 <= level_data:
                gold += 2500
                gold_list.append("(군단장 레이드)아브렐슈드 5~6관문 노말")
            raid_counter -= 1

        # 쿠크세이튼
        if 1475 <= level_data and raid_counter > 0:
            gold += 4500
            gold_list.append("(군단장 레이드)쿠크세이튼 노말")
            raid_counter -= 1

        # 비아키스
        if 1430 <= level_data and raid_counter > 0:
            if 1460 <= level_data:
                gold += 2400
                gold_list.append("(군단장 레이드)비아키스 하드")
                raid_counter -= 1
            else:
                gold += 1600
                gold_list.append("(군단장 레이드)비아키스 노말")

        # 발탄
        if 1415 <= level_data and raid_counter > 0:
            if 1445 <= level_data:
                gold += 1800
                gold_list.append("(군단장 레이드)발탄 하드")
            else:
                gold += 1200
                gold_list.append("(군단장 레이드)발탄 노말")

    return gold, gold_list


def get_job(key, name):
    out_list = []
    url = "https://developer-lostark.game.onstove.com/armories/characters/" + name + "/profiles"
    header = {"accept": "application/json", "authorization": key}
    req = requests.get(url=url, headers=header, verify=False)
    if req.status_code == 200:
        data = req.json()
        if data != None:
            return str(data["CharacterClassName"]), str(data["ItemAvgLevel"]), False
    return "0", "0", True


def get_level(key, name, usr_server: str):
    out_list = []
    url = "https://developer-lostark.game.onstove.com/characters/" + name + "/siblings"
    header = {"accept": "application/json", "authorization": key}
    req = requests.get(url=url, headers=header, verify=False).json()
    for i in req:
        if i["ServerName"] == usr_server:
            character_name = i["CharacterName"]
            level = float(i["ItemAvgLevel"].replace(",", ""))
            gold, gold_list = get_gold(level)
            if gold != 0:
                out_list.append([character_name, level, gold, gold_list])

    return out_list


def weekly_gold(name):
    url = "https://developer-lostark.game.onstove.com/armories/characters/" + name + "/profiles"
    header = {"accept": "application/json", "authorization": key}
    out_text = ">>> **" + name + "님의 주간 원정대 수입**\n" + name + "님의 주간 예상 원정대 수입 (레벨 순 상위 6개)은 "
    gold = 0
    req = requests.get(url=url, headers=header, verify=False)
    if req.status_code == 200:
        data = req.json()
        if data != None:
            result = get_level(key, name, data["ServerName"])
            result.sort(key=lambda x: -x[1])
            if len(result) > 6:
                out = result[:6]
            else:
                out = result
            for i in out:
                gold += i[2]
            out_text = out_text + str(gold) + "골드 입니다.\n\n원정대\n"
            for i in out:
                text = i[0] + " Lv." + str(i[1]) + " " + str(i[2]) + "골드\n```" + ", ".join(i[3]) + "```"
                out_text += text
            return out_text, False
        
    return "0", True


def oreha_in_market(key):
    header = {"accept": "application/json", "authorization": key}
    out_list = []
    value = {
        "Sort": "GRADE",
        "CategoryCode": 50010,
        "ItemTier": 0,
        "ItemName": "오레하",
        "SortCondition": "ASC"
    }
    url = "https://developer-lostark.game.onstove.com/markets/items"
    req = requests.post(url=url, headers=header, data=value, verify=False)
    data = req.json()
    for i in data["Items"]:
        tmp_list = [i['Name'], i['Icon'], i['YDayAvgPrice'], i['RecentPrice'], i['CurrentMinPrice']]
        out_list.append(tmp_list)
    return out_list


def valtan():
    with open("raid/valtan1", "r") as f:
        raid1 = f.read()
        
    with open("raid/valtan2", "r") as f:
        raid2 = f.read()
        
    valtan_embead = discord.Embed()
    valtan_embead.set_author(name="마수군단장 발탄", icon_url="https://i.imgur.com/7yOE56T.jpg")
    valtan_embead.add_field(name="1관문", value="검은 산의 포식자", inline=False)
    valtan_embead.add_field(name="추천 배틀 아이템", value="회오리 수류탄, 만능 물약", inline=False)
    valtan_embead.add_field(name="패턴 타임라인", value=raid1, inline=False)
    valtan_embead.add_field(name="공략 영상", value="https://www.youtube.com/watch?v=YNf2my7id-A", inline=False)
    valtan_embead.add_field(name="2관문", value="마수군단장 발탄", inline=False)
    valtan_embead.add_field(name="추천 배틀 아이템", value="파괴 폭탄 or 부식 폭탄, 화염 수류탄, 시간 정지 물약", inline=False)
    valtan_embead.add_field(name="패턴 타임라인", value=raid2, inline=False)
    valtan_embead.add_field(name="공략 영상", value="https://www.youtube.com/watch?v=LakcTJ7lmgw", inline=False)
    
    return valtan_embead, False


def viakiss():
    with open("raid/viakiss1", "r") as f:
        raid1 = f.read()
        
    with open("raid/viakiss2", "r") as f:
        raid2 = f.read()
        
    with open("raid/viakiss3", "r") as f:
        raid3 = f.read()
    
    viakiss_embead = discord.Embed()
    viakiss_embead.set_author(name="욕망군단장 비아키스", icon_url="https://i.imgur.com/DHPoaev.jpg")
    viakiss_embead.add_field(name="1관문", value="인큐버스 모르페", inline=False)
    viakiss_embead.add_field(name="추천 배틀 아이템", value="회오리 수류탄, 신속 로브", inline=False)
    viakiss_embead.add_field(name="패턴 타임라인", value=raid1, inline=False)
    viakiss_embead.add_field(name="공략 영상", value="https://www.youtube.com/watch?v=RRxHRHWyp-Q", inline=False)
    viakiss_embead.add_field(name="2관문", value="욕망의 탐식자 비아키스", inline=False)
    viakiss_embead.add_field(name="추천 배틀 아이템", value="화염 수류탄, 시간 정지 물약", inline=False)
    viakiss_embead.add_field(name="패턴 타임라인", value=raid2, inline=False)
    viakiss_embead.add_field(name="공략 영상", value="https://www.youtube.com/watch?v=lLgvOOt3DSA", inline=False)
    viakiss_embead.add_field(name="3관문", value="욕망군단장 비아키스", inline=False)
    viakiss_embead.add_field(name="추천 배틀 아이템", value="회오리 수류탄, 시간 정지 물약, 수면 폭탄", inline=False)
    viakiss_embead.add_field(name="패턴 타임라인", value=raid3, inline=False)
    viakiss_embead.add_field(name="공략 영상", value="https://www.youtube.com/watch?v=GtVyd7N9M2Q", inline=False)

    return viakiss_embead, False


def patch():
    with open("note.txt", "r") as f:
        note = f.read()
    return note


class TodoView(View):
    def __init__(self, *items: Item):
        super().__init__(*items, timeout=None)
        self.embed_list = None
        self.embed_number = 0
    
    def set_value(self, embed_list):
        self.embed_list = embed_list

    @discord.ui.button(label="모험섬", custom_id="prev_button", style=discord.ButtonStyle.primary, disabled = True)
    async def prev_button_callback(self, button, interaction):
        self.children[self.embed_number].disabled = False
        self.embed_number = 0
        self.children[self.embed_number].disabled = True
        await interaction.response.edit_message(embeds=self.embed_list[self.embed_number], view=self)


    @discord.ui.button(label="필보/유령선/카게", custom_id="next_button", style=discord.ButtonStyle.primary)
    async def next_button_callback(self, button, interaction):
        self.children[self.embed_number].disabled = False
        self.embed_number = 1
        self.children[self.embed_number].disabled = True
        await interaction.response.edit_message(embeds=self.embed_list[self.embed_number], view=self)
        
    @discord.ui.button(label="새로고침", custom_id="refresh_button", style=discord.ButtonStyle.danger)
    async def refresh_button_callback(self, button, interaction):
        self.embed_list = todo()
        await interaction.response.edit_message(embeds=self.embed_list[self.embed_number], view=self)
    
    
def todo():
    import firebase_api
    dict_today = {0: "카", 1: "필유", 2: "", 3: "유카", 4: "필", 5: "유카", 6: "필카"}
    KST = datetime.timezone(datetime.timedelta(hours=9))
    now = datetime.datetime.now(KST)
    hour = now.hour
    if hour < 10:
        hour = "0" + str(hour)
    else:
        hour = str(hour)

    minute = now.minute
    if minute < 10:
        minute = "0" + str(minute)
    else:
        minute = str(minute)

    second = now.second
    if second < 10:
        second = "0" + str(second)
    else:
        second = str(second)
        
    week = now.weekday()
    if int(hour) < 5:
        week -= 1

    dict_todo = {}
    for i in range(0, 24):
        if 10 < i:
            dict_todo[i] = str(i + 1) + ":00:00"
        elif i < 5:
            dict_todo[i] = "0" + str(i + 1) + ":00:00"
        else:
            dict_todo[i] = "11:00:00"

    if now.hour == 23:
        hour = "22"
    time2 = datetime.datetime.strptime(dict_todo[int(hour)], "%H:%M:%S")
    time1 = datetime.datetime.strptime(hour + ":" + minute + ":" + second, "%H:%M:%S")
    diff = time2 - time1
    
    today_list = []
    for i in range(3):
        if i == 0:
            name = "필드보스"
            if "필" in dict_today[week]:
                times = str(diff)
            else:
                times = "오늘 없음"
            img = "https://i.imgur.com/IvBAKCh.png"
        elif i == 1:
            name = "유령선"
            if "유" in dict_today[week]:
                times = str(diff)
            else:
                times = "오늘 없음"
            img = "https://i.imgur.com/SZJLz8j.png"
        else:
            name = "카오스게이트"
            if "카" in dict_today[week]:
                times = str(diff)
            else:
                times = "오늘 없음"
            img = "https://i.imgur.com/tSykKdk.png"
        
        embed = discord.Embed()
        embed.set_author(name=name, icon_url=img)
        embed.add_field(name="남은 시간", value=times)
        today_list.append(embed)
    
    island_list = firebase_api.get_island_embed()
    todo_list = [island_list, today_list]
    return todo_list


def Character_search(name: str):
    default_url = "https://developer-lostark.game.onstove.com/armories/characters/"
    url = default_url + name + "/profiles"
    header = {"accept": "application/json", "authorization": key}
    req = requests.get(url=url, headers=header, verify=False)
    if req.status_code == 200:
        json_data = req.json()
        image = json_data["CharacterImage"]       
        embed = discord.Embed()
        embed.set_author(name=name + " 님의 정보")
        embed.add_field(name="원졍대 레벨", value=json_data["ExpeditionLevel"])
        embed.add_field(name="직업", value=json_data["CharacterClassName"])
        embed.add_field(name="칭호", value=json_data["Title"])
        embed.add_field(name = chr(173), value = chr(173), inline=False)
        embed.add_field(name="평균 아이템 레벨", value=json_data["ItemAvgLevel"])
        embed.add_field(name="아이템 최고 레벨", value=json_data["ItemMaxLevel"])
        embed.add_field(name = chr(173), value = chr(173), inline=False)
        embed.add_field(name="영지 이름", value=json_data["TownName"])
        embed.add_field(name="영지 레벨", value=json_data["TownLevel"])
        embed.add_field(name = chr(173), value = chr(173), inline=False)
        embed.add_field(name="치명", value=json_data["Stats"][0]["Value"])
        embed.add_field(name="특화", value=json_data["Stats"][1]["Value"])
        embed.add_field(name="신속", value=json_data["Stats"][3]["Value"])
        embed.add_field(name = chr(173), value = chr(173), inline=False)
        embed.add_field(name="제압", value=json_data["Stats"][2]["Value"])
        embed.add_field(name="인내", value=json_data["Stats"][4]["Value"])
        embed.add_field(name="숙련", value=json_data["Stats"][5]["Value"])
        embed.add_field(name = chr(173), value = chr(173), inline=False)
        embed.add_field(name="최대 생명력", value=json_data["Stats"][6]["Value"])
        embed.add_field(name="공격력", value=json_data["Stats"][7]["Value"])
        embed.set_image(url=image)
    
        return embed, True
    else:
        return None, False


def command_list():
    embed = discord.Embed()
    embed.set_author(name="로스트아크 기능 도움말", icon_url="https://cdn-lostark.game.onstove.com/2018/obt/assets/images/common/icon/favicon-192.png?v=20230208080752")
    embed.add_field(name="수입 :moneybag:", value="예상 주간 원정대 수입을 알려드립니다.", inline=False)
    embed.add_field(name="파티 :crossed_swords:", value="파티 모집 게시글을 작성합니다.", inline=False)
    embed.add_field(name="경매 :judge:", value="전리품 경매 시 입찰을 돕기 위해 손익분기점을 알려드립니다.", inline=False)
    embed.add_field(name="일정 :calendar:", value="오늘의 일정을 알려드립니다.", inline=False)
    embed.add_field(name="돌파고 :bricks:", value="어빌리티 스톤을 깎는 연습을 할 수 있습니다.", inline=False)
    embed.add_field(name="공략 :receipt:", value="원하시는 레이드에 대한 공략을 요약해 알려드립니다.", inline=False)
    embed.add_field(name="오레하 :coin:", value="현재 오레하의 가격을 알려드립니다.", inline=False)
    embed.add_field(name="캐릭터 :bust_in_silhouette: ", value="해당 캐릭터의 정보를 알려드립니다.", inline=False)
    return embed