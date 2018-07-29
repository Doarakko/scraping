#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, os, time, re, json
import requests
from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.request import urlretrieve
from urllib.request import quote

team = "ys"

#選手の詳細ページのURLを取得する関数
def get_player_page_url_list():
    #投手
    endpoint = 'https://www.yakult-swallows.co.jp/players/category/pitcher'
    #捕手
    #endpoint = 'https://www.yakult-swallows.co.jp/players/category/catcher'
    #内野手
    #endpoint = 'https://www.yakult-swallows.co.jp/players/category/infielder'
    #外野手
    #endpoint = 'https://www.yakult-swallows.co.jp/players/category/outfielder'

    request = endpoint
    response = urlopen(request)
    resources = response.read()
    html = BeautifulSoup(resources, "html.parser")
    
    #画像のURLを入れるリストを準備
    url_list = []
    #選手の詳細ページのURLを抜き取る
    for player in html.find_all(attrs={"class":"md-3-1"}):
        for a_tag in player.find_all("a"):
            url =  a_tag.get("href")
            if url != None and url.find("detail") != -1:
                url_list.append("https://www.yakult-swallows.co.jp" + url)
    #デバック
    print("[Get] player page url")
    #画像のURLのリストを返す
    return url_list
    
#画像のURLを取得する関数
def get_player_image_url(player_page_url):
    request = player_page_url
    response = urlopen(request)
    resources = response.read()
    html = BeautifulSoup(resources, "html.parser")

    #画像のURLを抜き取る
    for image in html.find_all(attrs={"class":"md-6-1"}): 
        for img_tag in image.find_all("img"):
            url = img_tag.get("src")
            if url != None:
                return url 
            else:
                return []

#選手データを取得する関数
def get_player_data(player_page_url):
    request = player_page_url
    response = urlopen(request)
    resources = response.read()
    html = BeautifulSoup(resources, "html.parser")

    player_data = []
    #選手名を抜き取る
    for h1 in html.find_all(attrs={"class":"title-profile"}): 
        for strong in h1.find_all("strong"):
            player_data.append(strong.string)

    #選手データを抜き取る
    for table in html.find_all(attrs={"class":"tbl-profile"}): 
        for td_tag in table.find_all("td"):
            player_data.append(td_tag.string)
    return player_data

#画像の名前を取得する関数
def get_image_name(img_url):
    img_name = re.search(r'https://s3-ap-northeast-1.amazonaws.com/yklt-static/hp/img/players/2017/(.+).jpg', img_url)
    img_name = img_name.group(1)
    return img_name


#画像をダウンロードする関数
def download_image(img_url):
    #画像の名前を取得
    img_name = get_image_name(img_url)

    save_dir = "./image/" + team + "/"
    #ファイルを保存するディレクトリを作成
    if not os.path.exists(save_dir): os.makedirs(save_dir)
    save_path = save_dir + img_name + ".jpg"

    try:
        #写真をダウンロード
        urlretrieve(img_url, save_path)
        #1秒スリープ
        time.sleep(1) 
        #デバック
        print("[Download] {0}.jpg".format(img_name))
    except Exception as e:
        #デバック
        print("[Error] {0}".format(img_url))

#選手データのリストを辞書に変換する関数
def convert_to_dic(player_data, file_name):
    #辞書を準備
    player_dic = {}
    #リストの末尾を削除
    player_data.pop()
    key_list = ["name", "hurigana", "position", "birthday", "height", "weight", "home", "pb", "year"]

    for (key, player) in zip(key_list, player_data):
        player_dic[key] = player

    save_dir = "./data/" + team + "/"
    #ファイルを保存するディレクトリを作成
    if not os.path.exists(save_dir): os.makedirs(save_dir)
    #jsonファイルを保存するパス
    save_path = save_dir + file_name + ".json"
    #辞書をjsonで保存
    with open(save_path, "w") as f: 
        player_json = json.dumps(player_dic)
        json.dump(player_json, f)
    #デバック
    print("[Save] {0}".format(save_path))
    return player_dic

if __name__ == '__main__':
    #選手の詳細ページのURLを取得
    player_page_url_list = get_player_page_url_list()
    for player_page_url in player_page_url_list:
        #画像のURLを取得
        player_image_url = get_player_image_url(player_page_url)
        if player_image_url != None:
            #画像をダウンロード
            #download_image(player_image_url)
            #選手データを取得
            player_data = get_player_data(player_page_url)
            #画像の名前を取得
            file_name = get_image_name(player_image_url)
            #選手データのリストを辞書に変換
            player_dic = convert_to_dic(player_data, file_name)