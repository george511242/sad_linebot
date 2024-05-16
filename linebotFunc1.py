from flask import Flask
app = Flask(__name__)

from flask import request, abort
from linebot import  LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage,TextSendMessage, ImageSendMessage, StickerSendMessage, LocationSendMessage, QuickReply, QuickReplyButton, MessageAction
import psycopg2
from linebot.models import MessageEvent, TextMessage, PostbackEvent, TextSendMessage, TemplateSendMessage, ConfirmTemplate, MessageTemplateAction, ButtonsTemplate, PostbackTemplateAction, URITemplateAction, CarouselTemplate, CarouselColumn, ImageCarouselTemplate, ImageCarouselColumn
from urllib.parse import parse_qsl


# 讀取資料庫密碼
with open('db_password.txt', 'r') as file:
    db_password = file.read().strip()

# 資料庫連接設定
dbname = 'ShoppingGO'
db_user = 'postgres'  # 請更換為你的資料庫用戶名
db_host = 'localhost'     # 如果資料庫在本地，否則更換為相應的主機名
db_port = '5432'          # 資料庫服務器端口，預設為5432

# 建立資料庫連接
conn = psycopg2.connect(dbname=dbname, user=db_user, password=db_password, host=db_host, port=db_port)

def fetch_data_from_db():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM goods;")
    rows = cursor.fetchall()
    cursor.close()
    return rows

line_bot_api = LineBotApi('/RP5ONQZb3KjMUm1bPhGSaZRufUgaCi01uptj6/eNAHlCy4uQMfwrsHo2O0IX5sTpq+wiuI3VgCiQSXj/xShEAYpkal+uqQwL19a1ZBPTQidWbiU6782KJUUEIm/2ljUCggyZWLYns68otxtJcdbTAdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('b4db5feb35a9390ea7b07008b1abdcd7')

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature'] 
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    mtext = event.message.text
    if mtext == '@傳送文字':
        try:
            message = TextSendMessage(  
                text = "我是 李冠緯海軍陸戰隊，\n您好！"
            )
            line_bot_api.reply_message(event.reply_token,message)
        except:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text='發生錯誤！'))

    if mtext == '大安區':
        try:
            data = fetch_data_from_db()
            reply_message = "以下是正在大安區團購的商品:\n"
            for row in data:
                reply_message += f"商品ID: {row[0]}, 商品名: {row[1]}, 聯絡方式: {row[2]}\n"
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_message))
        except Exception as e:
            print(f"Error fetching data from database: {e}")
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='發生錯誤！'))

    if mtext == '@轉盤樣板':
        sendCarousel(event)

    if mtext == '@獲取商品資訊':
        try:
            message = TextSendMessage(
                text='請選擇地區',
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(
                            action=MessageAction(label="大安區", text="大安區")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="信義區", text="工程師")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="文山區", text="森林伐木工")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="新店區", text="半手李")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="淡水區", text="半手李")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="大安區", text="大安區")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="信義區", text="工程師")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="文山區", text="森林伐木工")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="新店區", text="半手李")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="淡水區", text="半手李")
                        ),
                    ]
                )
            )
            line_bot_api.reply_message(event.reply_token,message)
        except:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text='發生錯誤！'))

def sendCarousel(event):  #轉盤樣板
    try:
        message = TemplateSendMessage(
            alt_text='轉盤樣板',
            template=CarouselTemplate(
                columns=[
                    CarouselColumn(
                        thumbnail_image_url='https://i.imgur.com/4QfKuz1.png',
                        title='這是樣板一',
                        text='第一個轉盤樣板',
                        actions=[
                            MessageTemplateAction(
                                label='文字訊息一',
                                text='賣披薩'
                            ),
                            URITemplateAction(
                                label='連結文淵閣網頁',
                                uri='http://www.e-happy.com.tw'
                            ),
                            PostbackTemplateAction(
                                label='回傳訊息一',
                                data='action=sell&item=披薩'
                            ),
                        ]
                    ),
                    CarouselColumn(
                        thumbnail_image_url='https://i.imgur.com/qaAdBkR.png',
                        title='這是樣板二',
                        text='第二個轉盤樣板',
                        actions=[
                            MessageTemplateAction(
                                label='文字訊息二',
                                text='賣飲料'
                            ),
                            URITemplateAction(
                                label='連結台大網頁',
                                uri='http://www.ntu.edu.tw'
                            ),
                            PostbackTemplateAction(
                                label='回傳訊息二',
                                data='action=sell&item=飲料'
                            ),
                        ]
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token,message)
    except:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text='發生錯誤！'))


if __name__ == '__main__':
    app.run()
