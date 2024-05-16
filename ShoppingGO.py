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
db_user = 'postgres'      # 請更換為你的資料庫用戶名
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

def get_districts():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM groups;")
    rows = cursor.fetchall()
    districts = [r[2].split('區')[0].split('市')[-1] + '區' for r in rows]
    group_idx = [r[0] for r in rows]
    cursor.close()
    return districts, group_idx

def get_goods_from_group(group_name, group_dict):
    # group_id (大安區) --> seller_participation --> seller_id --> goods
    grp_id = group_dict[group_name]
    cursor = conn.cursor()
    query = "SELECT seller_id FROM seller_participation WHERE group_id = %s;"
    cursor.execute(query, (grp_id,))
    row = cursor.fetchone()  # seller_id

    # Get goods by seller id
    if row:
        cursor = conn.cursor()
        query = "SELECT goods.goods_picture, goods.tag, goods.goods_name, goods.unite_price, goods.min_quantity, goods.goods_description\
                FROM goods\
                WHERE goods.seller_id = %s;"
        cursor.execute(query, (row[0],))
        rows = cursor.fetchall()
        return rows
    return []
        


def create_order():
    # create go activity
    return 0


"""Global variables"""
line_bot_api = LineBotApi('/RP5ONQZb3KjMUm1bPhGSaZRufUgaCi01uptj6/eNAHlCy4uQMfwrsHo2O0IX5sTpq+wiuI3VgCiQSXj/xShEAYpkal+uqQwL19a1ZBPTQidWbiU6782KJUUEIm/2ljUCggyZWLYns68otxtJcdbTAdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('b4db5feb35a9390ea7b07008b1abdcd7')# b4db5feb35a9390ea7b07008b1abdcd7
areas, group_ids = get_districts()
group_dict = {area: group_id for area, group_id in zip(areas, group_ids)}


"""App functions"""
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

    if mtext in areas:
        try:
            # Get group's goods by seller_participation
            data = get_goods_from_group(mtext, group_dict)
            
            # Set reply messages    
            if data == []:
                reply_message = "沒有商品"
            else:
                reply_message = f"以下是正在{mtext}團購的商品:\n"
                for row in data:
                    reply_message += f"商品名: {row[2]}\n商品標籤: {row[1]}\n商品價錢: {row[3]}\n最低開團人數下限: {row[4]}\n"
                columns = []
                for row in data:
                    columns.append(
                        CarouselColumn(
                            thumbnail_image_url='https://i.imgur.com/4QfKuz1.png', 
                            title=f'商品名: {row[2]}',  
                            text=f'商品類型: {row[1]}\n價格: {row[3]}\n最低開團人數下限: {row[4]}\n', 
                            
                            actions=[
                                PostbackTemplateAction(
                                    label='購買此商品',
                                    data=f'action=buy&item={row[1]}'  # Adjust as necessary
                                ),
                                URITemplateAction(
                                    label='更多資訊',
                                    uri='http://www.example.com'  # Replace with actual URL if available
                                ),
                                PostbackTemplateAction(
                                    label='加入購物車',
                                    data=f'action=add_to_cart&item={row[1]}'  # Adjust as necessary
                                )
                            ]
                        )
                    )
                sendCarousel(event, columns)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_message))
        except Exception as e:
            print(f"Error fetching data from database: {e}")
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='發生錯誤！'))

    if mtext == '@轉盤樣板':
        sendCarousel(event)

    if mtext == '@獲取商品':
        try:
            items = [
                QuickReplyButton(
                    action=MessageAction(label=area, text=area)
                ) for area in areas
            ]
            message = TextSendMessage(
                text='請選擇地區',
                quick_reply=QuickReply(items=items)
            )
            line_bot_api.reply_message(event.reply_token, message)
        except Exception as e:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='發生錯誤：' + str(e)))
            
            
            
def sendCarousel(event, columns):  #轉盤樣板
    try:
        message = TemplateSendMessage(
            alt_text='商品轉盤',
            template=CarouselTemplate(columns=columns)
        )
        line_bot_api.reply_message(event.reply_token,message)
    except:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text='發生錯誤！'))
        
        
if __name__ == '__main__':
    app.run()