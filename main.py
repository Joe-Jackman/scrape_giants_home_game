# coding: UTF-8
from bs4 import BeautifulSoup
import urllib.request, urllib.error
import re
import datetime
import slackweb

# アクセスするURL(パラメタなしなら当月のGiantsスケジュールが帰ってくる)
url = "https://www.giants.jp/smartphone/G/schedule/"

# URLにアクセス
html = urllib.request.urlopen(url=url)

soup = BeautifulSoup(html, "lxml")
tr_tags = soup.find_all("tr")

date_pattern = '[0-9]+'
time_pattern = '[0-9]+:[0-9]+'

send_to_slack = []
slack = slackweb.Slack(url="https://hooks.slack.com/services/トークン")

for tr in tr_tags:
  if not tr.find('span', class_="home-game giants"): 
    continue

  time_result = re.search(time_pattern, tr.td.text)
  date_result = re.search(date_pattern, tr.th.span.text)

  now = datetime.datetime.now()
  # event_date = datetime.datetime.strptime(
  #   str(now.year) + '-' + str(now.month) + '-' + date_result.group(0) + ' ' + time_result.group(0) + ':' + '00',
  #   '%Y-%m-%d %H:%M:%S'
  #   )
  send_to_slack.append(str(now.year) + '-' + str(now.month) + '-' + date_result.group(0) + ' ' + time_result.group(0) + ':' + '00')
  slack.notify(text=str(now.year) + '-' + str(now.month) + '-' + date_result.group(0) + ' ' + time_result.group(0) + ':' + '00')
