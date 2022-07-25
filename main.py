import discord
import random
import pandas as pd
from helper.post import *
from helper.util import *
from constant.messages import *
from constant.tokens import *
from constant.paths import *
from constant.values import *

CLIENT = discord.Client()

def decideAction(text):
    actions = {"date":1, "bool":1, "num":1, "words":1, "google":1, "wiki":1, "man":1, "meme":1, "porn":1, "stock":1}
    df = pd.read_csv("data/memory.csv")
    for word in text.split():
        data = df[df['Word'] == word]
        for index, row in data.iterrows():
            startingValue = actions.get(row["Action"])
            newValue = startingValue + row["Value"]
            actions.update({row["Action"]:newValue})
    weights = list(actions.values())
    if min(weights) < 1:
        low = abs(min(weights)) + 1
        weights = [x+low for x in weights]
    return [random.choices(list(actions.keys()), weights=weights, k=1)[0], ""]

async def respondToMessage(message, text):
    print("### Responding to {0} ###".format(text))
    res = decideAction(text)
    action = res[0]
    keys = res[1]
    if action == "date":
        await postText(message, "date " + getRandomDateTimeString())
    elif action == "bool":
        await postText(message, "bool " + random.choice(MAGIC_EIGHT_BALL_MESSAGES))
    elif action == "num":
        await postText(message, "num " + str(random.randint(-MAX_RANDOM_NUMBER,MAX_RANDOM_NUMBER)))
    elif action == "words":
        await postText(message, "words " + getRandomWords())
    elif action == "google":
        await postGoogleSearchUrl(message, keys)
    elif action == "wiki":
        await postWikiUrl(message, keys)
    elif action == "man":
        await postManPageUrl(message, keys)
    elif action == "meme":
        await postImageFromCollection(message, 1, keys)
    elif action == "porn":
        await postPornUrl(message, 1, keys)
    elif action == "stock":
        await postUnsplashUrl(message, keys)
    print("### Responded to {0} ###\n".format(text))

@CLIENT.event
async def on_ready():
    print('We have logged in as {0.user}\n'.format(CLIENT))

@CLIENT.event
async def on_message(message):
    if message.author == CLIENT.user:
        return
    text = message.content.lower()
    if not text.startswith("momo"):
        return
    text = trimFirstWord(text)
    try:
        await respondToMessage(message, text)
    except:
        print("### An exception was thrown ###\n")
        await postText(message, ERROR_EXCEPTION_MESSAGE)

@CLIENT.event
async def on_reaction_add(reaction, user):
    if reaction.message.author != CLIENT.user:
        return
    if reaction.custom_emoji:
        return
    if reaction.emoji == "👍" or reaction.emoji == "👎":
        text = trimFirstWord(reaction.message.reference.cached_message.content)
        action = reaction.message.content.split()[0]
        df = pd.read_csv("data/memory.csv")
        for word in text.split():
            val = df.loc[(df['Word']==word) & (df['Action']==action), 'Value']
            if not val.empty:
                if reaction.emoji == "👍":
                    df.loc[(df['Word']==word) & (df['Action']==action), 'Value'] = val.iloc[0] + 2
                else:
                    df.loc[(df['Word']==word) & (df['Action']==action), 'Value'] = val.iloc[0] - 2
            else:
                if reaction.emoji == "👍":
                    newDf = {"Word":word, "Action":action, "Value":2}
                else:
                    newDf = {"Word":word, "Action":action, "Value":-2}
                df = df.append(newDf, ignore_index=True)
            df.to_csv("data/memory.csv", index=False)

CLIENT.run(BOT_TOKEN)