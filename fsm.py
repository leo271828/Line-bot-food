from transitions.extensions import GraphMachine
from linebot.models import MessageTemplateAction

from utils import *
import pandas as pd


class TocMachine(GraphMachine):
    def __init__(self, **machine_configs):
        self.machine = GraphMachine(model=self, **machine_configs)
        self.food, self.cost, self.place = "", "", ""
        self.flag = 0
        self.view_dict = {
            "Restaurant": "",
            "Food": "",
            "Cost": "",
            "Place": "",
            "Link": "",
        }
        self.path = 'data.csv'
        self.food_dict = {"breakfast":"早餐", "sweet":"甜食", "meal":"這一餐", "no":"這餐"}

    def is_going_to_menu(self, event):
        text = event.message.text
        return text.lower().strip() == "menu"

    def is_going_to_view(self, event):
        text = event.message.text
        return text.lower() == "view"

    def is_going_to_food(self, event):
        self.food, self.cost, self.place = "", "", "" # initialize

        text = event.message.text
        if self.flag : # if view_new is trigger then here is input the new restaurant name
            self.view_dict["Restaurant"] = text
            return True
        else:
            return text.lower() == "food"

    def is_going_to_cost(self, event):
        text = event.message.text
        if text.lower() in ["breakfast", "meal", "sweet", "no"]:
            self.food = text.lower()
            if self.flag :
                self.view_dict["Food"] = text.lower()
            return True
        else:
            return False

    def is_going_to_place(self, event):
        text = event.message.text
        if text.lower() in ["poor", "medium", "high", "no"]:
            self.cost = text.lower()
            if self.flag :
                self.view_dict["Cost"] = text.lower()
            return True
        else:
            return False
    
    def is_going_to_commend(self, event):
        text = event.message.text
        if (self.flag == 0) and (text.lower() in ["nearby", "middle", "far", "no"]):
            self.place = text.lower()
            return True
        else:
            return False
                
    def is_going_to_view_list(self, event):
        text = event.message.text
        if text.lower() == "all":
            self.flag = 1
            return True
        elif text.lower() == "five":
            self.flag = 0
            return True
        else:
            return False

    def is_going_to_view_new(self, event):
        text = event.message.text
        return text.lower() == "view_new"

    def is_going_to_view_link(self, event):
        text = event.message.text
        if (self.flag == 1) and (text.lower() in ["nearby", "middle", "far"]):
            if self.flag :
                self.view_dict["Place"] = text.lower()
            return True
        else:
            return False

    def is_going_to_view_done(self, event):
        text = event.message.text
        if (text.lower() != "back") and ('https://' in text) :
            pos = text.find("https")
            self.view_dict["Link"] = text[pos:]

            self.flag = 0
            return True
        else:
            self.flag = 0
            return False

# ----------------------------------------------------------
    def on_enter_menu(self, event):
        print("I'm entering menu")
        title = 'Menu'
        text = '請選擇你想要的功能吧'
        btn = [
            MessageTemplateAction(
                label = '美食推薦',
                text = 'food'
            ),
            MessageTemplateAction(
                label = '美食名單',
                text = 'view'
            ),
            MessageTemplateAction(
                label = 'Menu',
                text = 'menu'
            ),
            MessageTemplateAction(
                label = 'FSM',
                text = 'fsm'
            )
        ]
        send_button_message(event.reply_token, title, text, btn)

    # def on_exit_menu(self, tmp):
    #     print(tmp)
    #     print("Leaving menu")

    def on_enter_food(self, event):
        print("I'm entering food")
        title = 'Food - Meal'
        text = '你的新餐廳，是要吃哪一餐的呢?'
        btn = [
            MessageTemplateAction(
                label = '早餐',
                text = 'breakfast'
            ),
            MessageTemplateAction(
                label = '正餐',
                text = 'meal'
            ),
            MessageTemplateAction(
                label = '甜食',
                text = 'sweet'
            )
        ]
        if self.flag == 0: # is food path
            text = '你想吃哪一餐呢?'
            btn.append(
                MessageTemplateAction(
                    label = '都可以！',
                    text = 'no'
                )
            )
        
        send_button_message(event.reply_token, title, text, btn)

    def on_enter_cost(self, event):
        print("I'm entering meal")
        title = 'Food - Cost'
        text = f'你的新餐廳，價位大概落在哪呢?'
        btn = [
            MessageTemplateAction(
                label = '150 ↑',
                text = 'high'
            ),
            MessageTemplateAction(
                label = '100~150',
                text = 'medium'
            ),
            MessageTemplateAction(
                label = '100 ↓',
                text = 'poor'
            )
        ]
        if self.flag == 0: # is food path
            text = f'你的{self.food_dict[self.food]}想吃多少錢的呢?'
            btn.append(
                MessageTemplateAction(
                    label = '都可以！',
                    text = 'no'
                )
            )
        send_button_message(event.reply_token, title, text, btn)

    def on_enter_place(self, event):
        print("I'm entering place")

        title = 'Food - Place'
        text = '你的新餐廳，大概距離成大多遠呢？'
        btn = [
            MessageTemplateAction(
                label = '近的',
                text = 'nearby'
            ),
            MessageTemplateAction(
                label = '距離剛剛好的',
                text = 'middle'
            ),
            MessageTemplateAction(
                label = '遠的',
                text = 'far'
            )
        ]
        if self.flag == 0: # is food path
            text = '你想吃哪邊的餐廳呢？請以成大為中心！'
            btn.append(
                MessageTemplateAction(
                    label = '都可以！',
                    text = 'no'
                )
            )
        send_button_message(event.reply_token, title, text, btn)
        
    def on_enter_commend(self, event):
        print("I'm entering commend")

        reply_token = event.reply_token
        reply_text = food_recommend_text([self.food, self.cost, self.place])
        send_text_message(reply_token, reply_text)
        self.go_back()

    def on_enter_view(self, event):
        print("I'm entering view")

        reply_token = event.reply_token
        reply_text = view_func()
        title = "View"
        btn = [
            MessageTemplateAction(
                label = '我要看全部的餐廳名單！',
                text = 'all'
            ),
            MessageTemplateAction(
                label = '我要看隨機的 5 家餐廳',
                text = 'five'
            ),
            MessageTemplateAction(
                label = '我想新增新的餐廳',
                text = 'view_new'
            )
        ]
        send_button_message(reply_token, title, reply_text, btn)

    def on_enter_view_list(self, event):
        reply_token = event.reply_token
        reply_text = view_list_func(self.flag)
        send_text_message(reply_token, reply_text)
        self.flag = 0
        self.go_back()

    def on_enter_view_new(self, event):
        reply_token = event.reply_token
        reply_text = "請你輸入新餐廳的名字："

        self.flag = 1
        send_text_message(reply_token, reply_text)

    def on_enter_view_link(self, event):
        reply_token = event.reply_token
        reply_text = "請你貼上新餐廳的 Google map 連結："
        send_text_message(reply_token, reply_text)

    def on_enter_view_done(self, event):
        reply_token = event.reply_token
        reply_text = "新餐廳新增完成！"
        view_done_func(self.view_dict)

        send_text_message(reply_token, reply_text)
        self.go_back()