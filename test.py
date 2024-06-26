import uuid
import ast
import datetime
import shortuuid
import psycopg2
from flask import Flask, request, abort, redirect, session, url_for, render_template_string
from linebot import LineBotApi, WebhookHandler, WebhookParser
from linebot.exceptions import InvalidSignatureError

from linebot.models import (
    MessageEvent, TextMessage, PostbackEvent, TextSendMessage, TemplateSendMessage, 
    ConfirmTemplate, MessageTemplateAction, ButtonsTemplate, 
    PostbackTemplateAction, URITemplateAction, CarouselTemplate, CarouselColumn, ImageCarouselTemplate, ImageCarouselColumn, 
    QuickReply, QuickReplyButton, MessageAction, ButtonsTemplate, URIAction)
from urllib.parse import parse_qsl


# 讀取資料庫密碼
app = Flask(__name__)
with open('db_password.txt', 'r') as file:
    db_password = file.read().strip()


# 資料庫連接設定
dbname = 'ShoppingGO'
db_user = 'postgres'      # 請更換為你的資料庫用戶名
db_host = 'localhost'     # 如果資料庫在本地，否則更換為相應的主機名
db_port = '5432'          # 資料庫服務器端口，預設為5432


# 建立資料庫連接
conn = psycopg2.connect(dbname=dbname, user=db_user, password=db_password, host=db_host, port=db_port)


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
        query = "SELECT goods.goods_picture, goods.tag, goods.goods_name, go_activity.unite_price, \
                go_activity.min_quantity, go_activity.group_id, goods.goods_id, go_activity.seller_id, go_activity.activity_id FROM goods \
                JOIN go_activity ON goods.goods_id = go_activity.goods_id \
                WHERE go_activity.seller_id = %s;"
        cursor.execute(query, (row[0],))
        rows = cursor.fetchall()
        return rows
    return []
        


"""Global variables"""
line_bot_api = LineBotApi('/RP5ONQZb3KjMUm1bPhGSaZRufUgaCi01uptj6/eNAHlCy4uQMfwrsHo2O0IX5sTpq+wiuI3VgCiQSXj/xShEAYpkal+uqQwL19a1ZBPTQidWbiU6782KJUUEIm/2ljUCggyZWLYns68otxtJcdbTAdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('b4db5feb35a9390ea7b07008b1abdcd7')# b4db5feb35a9390ea7b07008b1abdcd7
parser = WebhookParser('b4db5feb35a9390ea7b07008b1abdcd7')# b4db5feb35a9390ea7b07008b1abdcd7
user_states = {}
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

    events = parser.parse(body, signature)
    for event in events:
        if isinstance(event, PostbackEvent):
            handle_postback(event)
    return 'OK'


def handle_event(event):
    if isinstance(event, PostbackEvent):
        handle_postback(event)



def handle_postback(event):
    data = event.postback.data
        
    # Assuming the data is in the format 'action=buy&item=item_name'
    action, item = data.split('&')
    _, action_value = action.split('=')
    _, item_name = item.split('=')

    if action_value == 'buy':
        process_purchase(event, list(ast.literal_eval(item_name)))


def process_purchase(event, row):
    # Insert into database "order"
    cursor = conn.cursor()
    query = "INSERT INTO orders (buyer_id, activity_id, quantity, order_time, order_status, comment, star_rating) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    user_id = event.source.user_id
    q_data = ('Buffet@gmail.com.tw', row[8], 3, datetime.datetime.now(), '已下單', '', 3) 
    cursor.execute(query, q_data)
    conn.commit()
    
    # Sending a confirmation message to the user
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=f"Thank you for purchasing {row[2]}!")
    )


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

    elif mtext in areas: # Deal with the data in districts picked
        try:
            # Get group's goods by seller_participation
            data = get_goods_from_group(mtext, group_dict)
            
            # Set reply messages    
            if data == []:
                reply_message = "沒有商品"
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_message))
            else:
                columns = []
                for row in data:
                    columns.append(
                        CarouselColumn(
                            thumbnail_image_url='https://i.imgur.com/4QfKuz1.png', 
                            title=f'商品名: {row[2]}',  
                            text=f'商品類型: {row[1]}\n價格: {row[3]}\n最低開團人數下限: {row[4]}\n', 
                            
                            actions=[
                                PostbackTemplateAction(
                                    label='下單',
                                    data=f'action=buy&item={row}'
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
                
        except Exception as e:
            print(f"Error fetching data from database: {e}")
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='發生錯誤！'))
            
            
    elif mtext == '@獲取商品':
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
           
           
    elif mtext == '@登入會員':
        buttons_template = ButtonsTemplate(
            title='登入', text='點擊下方登入', actions=[
                URIAction(label='登入', uri='https://your-auth-server.com/login')
            ]
        )
        template_message = TemplateSendMessage(alt_text='登入', template=buttons_template)
        line_bot_api.reply_message(event.reply_token, template_message)

            
"""Design for 轉盤"""            
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