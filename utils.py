import os
import pandas as pd

from random import sample
from linebot import LineBotApi, WebhookParser
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage \
    , TemplateSendMessage, ButtonsTemplate


channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", None)


def send_text_message(reply_token, text):
    line_bot_api = LineBotApi(channel_access_token)
    line_bot_api.reply_message(reply_token, TextSendMessage(text=text))

    return "OK"

def send_image_url(id, img_url):
    line_bot_api = LineBotApi(channel_access_token)
    message = ImageSendMessage(
        original_content_url = img_url,
        preview_image_url = img_url
    )
    line_bot_api.reply_message(id, message)

    return "OK"

def send_button_message(reply_token, title, text, btn):
    line_bot_api = LineBotApi(channel_access_token)
    message = TemplateSendMessage(
        alt_text='Button!',
        template = ButtonsTemplate(
            title = title,
            text = text,
            actions = btn
        )
    )
    line_bot_api.reply_message(reply_token, message)

    return "OK"

'''
以下是"推薦功能"的函式
'''
path = "data.csv"

def df2text(res):
    try:
        res = res.drop(["ID"], axis=1)
    except:
        pass
    text = "我們推薦這幾家餐廳給你！\n"
    for idx in res.index:
        tmp = res.iloc[idx][0]
        tmp_link = res.iloc[idx]["Link"]
        text += str(idx+1) + ". " + tmp + " " + tmp_link + "\n"
    return text

def output_filter(df_data, level):
    if level == "no":
        return pd.Series([True for i in range(df_data.shape[0])])
    else:
        return df_data == level

def food_recommend_text(level_list):
    df = pd.read_csv(path)
    food_str, cost_str, place_str = level_list[0], level_list[1], level_list[2]

    ffood = output_filter(df.Food, food_str)
    fcost = output_filter(df.Cost, cost_str)
    fplace = output_filter(df.Place, place_str)
    filter = (ffood & fcost & fplace)
    res = pd.DataFrame(df[filter]).reset_index(drop=True)
    text = df2text(res)
    return text

'''
The following code is about "View" funcion
'''
def view_func():
    df = pd.read_csv(path)
    text = f"現在你的美食清單共有 {df.shape[0]} 家餐廳，你想對他做甚麼動作呢?"
    return text

def view_list_func(flag):
    df = pd.read_csv(path)
    if flag:
        res = df
    else:
        lst = sample(list(df.index), 5)
        res = df.iloc[lst, :].reset_index(drop=True)

    text = df2text(res)
    return text
    
def view_done_func(new_data):
    df = pd.read_csv(path)
    new_df = df.append(new_data, ignore_index=True)
    new_df.to_csv(path, index=False, encoding='utf_8_sig')

"""
def send_button_message(id, text, buttons):
    pass
"""
