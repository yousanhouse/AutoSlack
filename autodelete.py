
from datetime import datetime #日付を扱うため
from time import sleep # 処理を一旦停止するため
import json # json形式のデータを扱うため
import re #正規表現の操作を行うため
import sys # システムに関する処理を行うため
import urllib.parse #URLを解析して構成要素を得るため
import urllib.request #URLを開くため

DELETE_URL = "https://slack.com/api/chat.delete" #メッセージを削除するためのSlackのAPIのURL
HISTORY_URL = "https://slack.com/api/conversations.history" #メッセージの履歴を得るためのSlackのAPIのURL
API_TOKEN = 'xoxb-277276900005-2137822248932-GcL8KAGwB9pAJSFoZ5dEDvnh' #メッセージに対する操作をする際に必要となるAPI_TOKEN
TERM = 60 * 60 * 24 * 7  #1週間なので7を指定。ここの数字を変更することで、削除対象のメッセージの期間を変更できる

def clean_old_message(channel_id): #メッセージを削除するための関数
    print('Start cleaning message at channel "{}".'.format(channel_id))  # どのチャンネルのメッセージを削除するのか表示する
    current_ts = int(datetime.now().strftime('%s')) #現在の時刻を取得 [OK]
    


    messages = get_message_history(channel_id) #channel_idで指定したchannelのメッセージを取得する *チャンネルのメッセージが取得できていない

    print(messages)

    for message in messages: #このfor文である期間以上より前のメッセージを自動的に削除する
        if current_ts - int(re.sub(r'\.\d+$', '', message['ts'])) > TERM:
            delete_message(channel_id, message['ts'])
            sleep(1)
    



def get_message_history(channel_id): #メッセージの履歴を取得するための関数
    params = {
        'token': API_TOKEN,  #使用するAPI_TOKENを指定する
        'channel': channel_id, # メッセージ履歴を取得するchannelのidを指定する
        'limit': 500    #メッセージを取得する件数の数を指定する
    }

    req_url = '{}?{}'.format(HISTORY_URL, urllib.parse.urlencode(params)) #HTTP requestを投げるためのURLを構成する *リクエストurlが取れていない

    req = urllib.request.Request(req_url) #実際にそのURLにrequestを投げる

    message_history = []
    with urllib.request.urlopen(req) as res:
        data = json.loads(res.read().decode("utf-8")) #utf-8でjsonのデータをデコードする
        if 'messages' in data: # dataがレスポンスの文言に含まれているか確認する
            message_history = data['messages']

    return message_history


def delete_message(channel_id, message_ts): #メッセージを削除する関数
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    params = {
        'token': API_TOKEN,  #使用するAPI_TOKENを指定する
        'channel': channel_id, # メッセージ履歴を削除するchannelのidを指定する
        'ts': message_ts # 削除するメッセージのタイムスタンプを指定する
    }

    req_url = '{}?{}'.format(DELETE_URL, urllib.parse.urlencode(params)) #URLを構成する文字列を定義する
    req = urllib.request.Request(req_url, headers=headers) # requestを投げる
    with urllib.request.urlopen(req) as res:
        data = json.loads(res.read().decode("utf-8"))
        if 'ok' not in data or data['ok'] is not True:
            print('Failed to delete message. ts: {}'.format(message_ts))


if __name__ == "__main__":
    args = sys.argv
    if len(args) < 2:
        print("The first parameter for slack channel id is required.")
    else:
        clean_old_message(args[1])