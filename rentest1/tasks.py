import requests
from datetime import datetime
from celery import Celery

# Celery设置

# worker处理后的返回结果
celery_backend = 'redis://localhost:6379/14'
# 消息传输的中间件
celery_broker = 'redis://localhost:6379/15'

app = Celery('tasks',
             broker=celery_broker,
             backend=celery_backend)


@app.task(name='rentest1.tasks.save_image')
def save_image(image_url, user_name, request_headers, images_path, date_name):
    # date = datetime.now()
    # date_name = date.strftime('%b %d')

    file_name = image_url.replace('/', '_')
    with open((images_path + '{}/{}/{}').format(date_name, user_name, file_name), 'wb+') as f:
        f.write(requests.get(image_url, headers=request_headers, timeout=30).content)
