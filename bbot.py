#!/usr/local/bin/python3

from datetime import datetime, timezone
import os
import requests
import random
import json
import re
import pickle
import copy
import time
from urllib.parse import unquote,urlparse
import http.cookiejar
import argparse

pwd = os.path.dirname(os.path.realpath(__file__))

def display_session_cookies(s):
    for x in s.cookies:
        print(f"{x}")

DM_HEADERS = {
                "accept": "*/*",
                "accept-language": "en-US,en;q=0.9,fr;q=0.8,zh-CN;q=0.7,zh;q=0.6,zh-TW;q=0.5,ja;q=0.4,es;q=0.3",
                "cache-control": "no-cache",
                "dnt": "1",
                "origin": "https://message.bilibili.com",
                "pragma": "no-cache",
                "priority": "u=1, i",
                "referer": "https://message.bilibili.com/",
                "sec-ch-ua": '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"macOS"',
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-site",
                "sec-gpc": "1",
                "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
            }

class BBot:
    def __init__(self):
            self._session = requests.Session()
            self._contacts = dict()
            # default cookie: txt cookies exported via https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc?hl=en
            self._cookie_path = os.path.join(pwd, "message.bilibili.com_cookies.txt")
            self._headers  = copy.deepcopy(DM_HEADERS)

            try:
                self._load_cookies()
            except:
                print("error loading cookie")
    
    def _load_cookies(self):
        if self._cookie_path.endswith(".pkl"):
            cookies = pickle.load(open(self._cookie_path, "rb"))
        elif self._cookie_path.endswith(".txt"):
            self.set_cookies_from_netscape_txt(self._cookie_path)

    def set_cookies_from_netscape_txt(self, cookie_path):
        print(f"loading cookie from {cookie_path}")
        cj = http.cookiejar.MozillaCookieJar(cookie_path)
        cj.load()
        self._session.cookies.update(cj)
        print("finish updating cookie using txt info")

    def download_img(self, image_url, folder_path):
        """
        download img to folder given url
        """

        # Send a GET request to the image URL
        response = requests.get(image_url)

        parsed_url = urlparse(image_url)
        # Extract the file name from the path
        image_name = parsed_url.path.split('/')[-1]
        image_path = os.path.join(folder_path,image_name)

        # Check if the image already exists
        if os.path.exists(image_path):
            print("Image already exists, skipping download.")
            return

        # Check if the request was successful
        if response.status_code == 200:
            # Open a file in binary write mode and save the image
            with open(image_path, "wb") as file:
                file.write(response.content)
            print("Image downloaded successfully.")
        else:
            print(f"Failed to download image. Status code: {response.status_code}")

    def save_chat(self, contact_id = 0, save_format = "html"):
        """
        save chats as html file.
        """
        url = "https://api.vc.bilibili.com/svr_sync/v1/svr_sync/fetch_session_msgs"

        # create folder to save files
        save_dir = os.path.join(pwd, "saved", str(contact_id))
        os.makedirs(save_dir, exist_ok=True)

        form = {
            "talker_id": str(contact_id),
            "session_type": "1",
            "size": "100",
            "begin_seqno": "0",
            "sender_device_id": "1",
            "build": "0",
            "mobi_app": "web",
        }
        total_count = 0
        saved = []

        # collect chats from latest to oldest
        while True:
            r = self._session.get(url=url, headers=self._headers, params=form)
            response = r.json()
            data = response["data"]
            dms = data["messages"]
            total_count+=len(dms)
            if len(dms)==0:
                break
            for msg in dms:
                content = msg["content"]
                ts_str = datetime.fromtimestamp(msg["timestamp"]).strftime('%Y-%m-%d %H:%M:%S')
                sender = msg["sender_uid"]
                content = json.loads(content)
                # ignore if the content only contains an integer
                if isinstance(content, dict):
                    if "content" in content:
                        print(sender, ts_str, content["content"])
                        saved.append(("text",sender, ts_str, content["content"]))
                    else:
                        print(sender, ts_str, content["url"])
                        self.download_img(content["url"], save_dir)
                        saved.append(("img",sender, ts_str, content["url"]))

            print(f"{total_count} messages fetched")
            if int(data["has_more"]) == 0 :
                break
            form["end_seqno"] = data["min_seqno"]

        if save_format == "html":
            self.write_html(saved, save_dir)

    def write_html(self, saved, save_dir):
        """
        save the chats as html file
        """
        filepath = os.path.join(save_dir, "chat.html")
        f = open(filepath,'w')  
        print('writing to...',filepath)     

        message_head = """<html>
        <head><meta charset='utf-8'>
        <style>.holder img {max-height: 250px;max-width: 250px;}</style>
        <body>
        """

        message_tail="</body></html>"
        message_body=""

        for msg in reversed(saved):
            title=str(msg[1])
            content_type=msg[0]
            timestamp = msg[2]
            message_body+= f"<p> <pre>{title:<13} {timestamp} </pre> \n"

            if content_type=="img":
                image_url = msg[3]
                parsed_url = urlparse(image_url)
                image_name = parsed_url.path.split('/')[-1]
                filename = os.path.join(save_dir, image_name)
                message_body+= f'''<figure class="holder"><img src="{filename}"></figure></p>\n'''

            if content_type=="text":  
                message_body+=f"{msg[3]}</p> \n"
        message=message_head+message_body+message_tail
        f.write(message)
        f.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Save chat by contact ID")
    parser.add_argument('contact_id', type=str, help='Contact ID to save chat for')
    args = parser.parse_args()
    b=BBot()
    b.save_chat(contact_id=args.contact_id)