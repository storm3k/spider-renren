# !usr/bin/python
# -*- coding:utf-8 -*-


import os
import time
import schedule
import logging
import logging

logger = logging.getLogger(__name__)
# 日志等级
logger.setLevel(level=logging.DEBUG)

# 记录日志
handler = logging.FileHandler("log.txt")
handler.setLevel(logging.DEBUG)

# 格式化日志
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

SPIDER_NAME = 'renphoto001'


def job():
    # print("{} 的脚本已经开始运行".format(SPIDER_NAME))

    # ps 查询进程
    p = os.popen('ps -ef | grep python')
    x = p.read()
    m = x.find(SPIDER_NAME)

    # 如果没有找到爬虫名字，则爬虫停止
    if m == -1:
        logger.debug("启动爬虫")
        os.system('cp /dev/null nohup.out')

        # 启动爬虫
        os.system('nohup scrapy crawl {} &'.format(SPIDER_NAME))
        time.sleep(5)
        # os.system('nohup scrapy crawl {} &'.format(SPIDER_NAME))


# 首先执行
job()
schedule.every(10).minutes.do(job)
while True:
    # run_pending：运行所有可以运行的任务
    schedule.run_pending()
    time.sleep(1)
