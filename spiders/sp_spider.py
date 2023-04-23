# -*- coding: utf-8 -*-
"""
Created on 2023-04-07 11:30:21
---------
@summary:
---------
@author: 逢高SAMA
"""

import re
import json
import random

import feapder
from setting import CUSTOM_PROXY
from feapder.core.parser_control import ParserControl
from feapder.db.redisdb import RedisDB
from feapder.utils.log import log


class SpSpider(feapder.Spider):
    # 自定义数据库，若项目中有setting.py文件，此自定义可删除
    # __custom_setting__ = dict(
    #     REDISDB_IP_PORTS="localhost:6379", REDISDB_USER_PASS="", REDISDB_DB=0
    # )

    def __init__(self, redis_key=None, min_task_count=1, check_task_interval=5, thread_count=None, begin_callback=None, end_callback=None, delete_keys=..., keep_alive=None, auto_start_requests=None, batch_interval=0, wait_lock=True, **kwargs):
        self.success_table = "{}:success_request".format(redis_key)
        self.count_table = "{}:count_vote".format(redis_key)
        self.redis_db_ = RedisDB()
        super().__init__(redis_key, min_task_count, check_task_interval, thread_count, begin_callback, end_callback, delete_keys, keep_alive, auto_start_requests, batch_interval, wait_lock, **kwargs)

    def start_requests(self):

        url = "https://questant.jp/q/FLAME#basic"

        for i in range(5000):

            yield feapder.Request(url, callback=self.get_params, count=i)

    def download_midware(self, request):

        # request.proxies = CUSTOM_PROXY
        return request

    def get_params(self, request, response):
        
        cookie = ";".join([i.split(";")[0] for i in response.headers["set-cookie"].split(",")])
        enquete_id = re.findall(r"enquete_data = \{\"id\": \"(.*?)\"", response.text)[0]
        publish_id = int(re.findall(r"data-publish-id=\"(.*?)\"", response.text)[0])
        questions_id = re.findall(r"\"question_order\": \[\[(.*?)\]\]", response.text)[0].split(",")
        answer_started_at = re.findall(r"\"answer_started_at\": \"(.*?)\"", response.text)[0]

        vote1 = [0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        vote2 = [0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        vote3 = [0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        vote4 = [0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        vote5 = [0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        vote6 = [0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

        vote = random.choice([vote1, vote2, vote3, vote4, vote5, vote6])
        vote_code = ["" if i==0 else None for i in vote]



        headers = {
            "authority": "questant.jp",
            "accept": "application/json, text/javascript, */*; q=0.01",
            "accept-language": "zh-CN,zh;q=0.9",
            "cache-control": "no-cache",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "origin": "https://questant.jp",
            "pragma": "no-cache",
            "referer": "https://questant.jp/q/FLAME",
            "sec-ch-ua": "\"Google Chrome\";v=\"111\", \"Not(A:Brand\";v=\"8\", \"Chromium\";v=\"111\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "cookie": cookie,
            "x-requested-with": "XMLHttpRequest"
        }

        data = {
            "enquete_id": enquete_id,
            "publish_id": publish_id,
            "basic_information": {
                "gender": "m",
                "prefecture": "code27",
                "age": "age1",
                "city": ""
            },
            "questions": [
                {
                    "id": questions_id[0].strip(),
                    "qtype": "choiceimage-checkbox",
                    "answers": vote,
                    "free_answers": vote_code
                },
                {
                    "id": questions_id[1].strip(),
                    "qtype": "textbox",
                    "answers": [""]
                }
            ],
            "answer_started_at": answer_started_at,
            "logic_disp": {},
            "airs_attrs": None,
            "pr_attrs": None,
            "yid": None,
            "answer_session_id": "0"
        }
        data = json.dumps(data, separators=(',', ':'))

        url = "https://questant.jp/q/FLAME/save?as_id=0"
        yield feapder.Request(url, callback=self.parse, headers=headers, data=data, method="POST", request_sync=True, vote=vote)

    def parse(self, request, response):
        
        log.info(request.data)
        log.info(response.text)
        for idx, vote in enumerate(request.vote):
            if vote == 1:
                if idx == 0:
                    self.redis_db_.hincrby(self.count_table, "light", 1)
                elif idx == 8:
                    self.redis_db_.hincrby(self.count_table, "wing", 1)
                elif idx == 9:
                    self.redis_db_.hincrby(self.count_table, "wingy", 1)
        self.redis_db_.hincrby(self.success_table, "success_count", 1)


    def end_callback(self):
        success_count = self.redis_db_.hgetall(self.success_table)
        vote_count = self.redis_db_.hgetall(self.count_table)
        print(success_count)
        print(vote_count)
        return super().end_callback()
        


if __name__ == "__main__":
    SpSpider(redis_key="test:flame_sp", delete_keys=True, thread_count=32).start()
