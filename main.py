import discord
from discord.commands import Option
from discord.ui import Button, View, Item
from api import *


key = "LostArk API Key"
token = "Discord Bot Token"

bot = discord.Bot()


@bot.event
async def on_ready():
    bot.add_view(TodoView())


@bot.slash_command(description="주간 기대 수입")
async def 수입(ctx, name: Option(str, "캐릭터 이름"), ):
    text, error = weekly_gold(name)
    if error:
        await ctx.respond("오류입니다. 입력값을 확인하거나 다시 입력해 주세요.", ephemeral=True)
    else:
        await ctx.respond(text)

@bot.slash_command(description="쌀산기")
async def 경매(ctx, gold: Option(int, "경매장 골드"), ):
    text = auction(gold)
    await ctx.respond(text)

@bot.slash_command(description="파티모집")
async def 파티(ctx):
    modal = PartyMaking(title="파티 생성")
    modal.set_ctx(ctx)
    await ctx.send_modal(modal)
    
@bot.slash_command(description="오레하 가격")
async def 오레하(ctx):
    data = oreha_in_market(key)
    oreha_list = []
    for i in data:
        tmp = discord.Embed()
        tmp.set_author(name=i[0], icon_url=i[1])
        tmp.add_field(name="전날 평균", value=str(i[2]) + "G")
        tmp.add_field(name="현재 가격", value=str(i[3]) + "G")
        tmp.add_field(name="최저 가격", value=str(i[4]) + "G")
        oreha_list.append(tmp)
    
    await ctx.respond(embeds=oreha_list)
    
@bot.slash_command(description="공략")
async def 공략(ctx, name: Option(str, "레이드 목표")):
    error = True
    
    if name == "발탄":
        result, error = valtan()
    elif name == "비아키스" or name == "비아":
        result, error = viakiss()
        
    if error:
        await ctx.respond("미구현이거나 없는 레이드입니다.", ephemeral=True)
    else:
        await ctx.respond(embed=result)
        
@bot.slash_command(description="돌깎기 시뮬레이터")
async def 돌파고(ctx):
    modal = StoneMaking(title="돌 설정")
    modal.set_ctx(ctx)
    await ctx.send_modal(modal)
    
@bot.slash_command(description="오늘의 일정")
async def 일정(ctx):
    todo_view = TodoView()
    list_todo = todo()
    todo_view.set_value(list_todo)
    await ctx.respond(embeds=list_todo[0], view=todo_view)
    
@bot.slash_command(description="캐릭터 정보를 검색합니다.")
async def 캐릭터(ctx, name: Option(str, "이름")):
    character_data, option = Character_search(name)
    if option:
        await ctx.respond(embed=character_data)
    else:
        await ctx.respond("오류입니다. 입력값을 확인하시거나 다시 입력해 주세요.", ephemeral=True)
    
@bot.slash_command(description="패치 노트")
async def 패치노트(ctx):
    note = patch()
    await ctx.respond(note)

@bot.slash_command(description="사용 가능한 명령어를 보여줍니다.")
async def 도움말(ctx):
    bot_commands = command_list()
    await ctx.respond(embed=bot_commands)
    
@bot.slash_command(description="개발자 테스트용")
async def 테스트(ctx):
    await ctx.respond("테스트중입니다", ephemeral=True)
    

bot.run(token)