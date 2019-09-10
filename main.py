# coding: UTF-8
from bs4 import BeautifulSoup
import urllib.request, urllib.error
import re
import datetime
import slackweb
import pymysql.cursors  # dictionary objを受け取る
import json

OFFICIAL_SCHEDULE_URL = "https://www.giants.jp/smartphone/G/schedule/"

def parse_config():
  f = open('config.json', 'r')
  json_data = json.load(f)
  return json_data

def connect_db(events_datetime, config_json):
  # データベースへの接続とカーソルの生成
  connection = pymysql.connect(
    host      = config_json['db_connection']['host'],
    user      = config_json['db_connection']['user'],
    password  = config_json['db_connection']['password'],
    db        = config_json['db_connection']['db'],
    charset   = config_json['db_connection']['charset'],
    cursorclass = pymysql.cursors.DictCursor
  )
  cursor = connection.cursor()
  
  try:
    with connection.cursor() as cursor:
        # sample Update Query
        sql = "UPDATE giants " \
              + "SET " \
              + "created_at = %s, " \
              + "updated_at = %s " \
              + "WHERE id = 5"
        # send_to_slack(sql % (events_datetime[0], events_datetime[1]))
        cursor.execute(sql, (events_datetime[0], events_datetime[1]))
        result = cursor.fetchall()
        connection.commit()
  finally:
    connection.close()
  return

def send_to_slack(messages):
  slack = slackweb.Slack(url = parse_config()['slack'])
  slack.notify(text = messages)

def main(bsoup):
  tr_tags = bsoup.find_all("tr")

  date_pattern = '[0-9]+'
  time_pattern = '[0-9]+:[0-9]+'

  slack_messages = []

  for tr in tr_tags:
    if not tr.find('span', class_="home-game giants"): 
      continue

    time_result = re.search(time_pattern, tr.td.text)
    date_result = re.search(date_pattern, tr.th.span.text)
    
    # 試合日がすぎた日付は開始時間が消えるので正規表現に合致しなくなる
    if not isinstance(time_result, re.Match) or not isinstance(date_result, re.Match):
      continue

    now = datetime.datetime.now()
    event_date = datetime.datetime.strptime(
      str(now.year) + '-' + str(now.month) + '-' + date_result.group(0) + ' ' + time_result.group(0) + ':00',
      '%Y-%m-%d %H:%M:%S'
    )
    slack_messages.append(event_date)

  connect_db(slack_messages, parse_config())

def request_official_schedule():
  try:
    # アクセスするURL(パラメタなしなら当月のGiantsスケジュールが帰ってくる)
    html = urllib.request.urlopen(url = OFFICIAL_SCHEDULE_URL)
  except:
    # TODO: エラーログ出力
    send_to_slack("スケジュールを取得できませんでした")
  return BeautifulSoup(html, "lxml")

# Entry Point
if __name__ == "__main__":
  bsoup = request_official_schedule()
  
  if bsoup:
    main(bsoup)
  else:
    send_to_slack("Giants Schedule not found.")