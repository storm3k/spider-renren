### 工作站爬虫

#### 1. 基本原理

遍历ID，拼接网页，查找相册，异步任务( 使用celery, redis作为后端 )下载

#### 2. 配环境

```python
# 安装redis (需要有 root 权限，工作站基本已安装)
sudo apt-get redis-server

# 创建空文件夹用于挂载
mkdir ws_renren

# 挂载
sshfs XX@XX:/home/XX/renren_env/  ./ws_renren

# 配置1. 安装 anaconda
./ws_renren/Anaconda3-5.3.1-Linux-x86_64

# 配置2. 创建虚拟环境
conda env create -f ./ws_renren/spider.yaml


# 配置3. 复制爬虫文件
cp -r ./ws_renren/ren ./ren


# 修改 账号密码
# 修改 id (每台机子需要独立)
# 修改 pipeline (改存储路径)
# 载入虚拟环境
source activate spider
# 运行异步任务
nohup celery -A tasks worker --loglevel=info &
# 运行脚本(此时爬虫已经运行起来)
nohup python3 run_script.py &

# 取消挂载
fusermount -u ws_renren
```



#### 3. 日常维护

##### 3.1 查询下载量

用户家目录下有 `daily.py` ，直接执行

```python
python3 daily.py 数字
# 数字为从今天起往前几天，默认为昨天，0为今天
```

##### 3.2 关闭`celery`异步任务

```python
ps auxww | grep 'tasks worker' | awk '{print $2}' | xargs kill -9
```

##### 3.3 ID说明

* zz工作站`/home/XX/renren_env`下，`renren_id.zip` 为ID的压缩包
* 根目录下的 txt 为未下载的ID，5000为间隔，共600个起始点。
* 工作站每2~3小时完成5000个ID的遍历。
* ws意思是工作站目录，记录了已经分配的ID

##### 3.4 存储路径说明

* XX工作站挂载253上
* XX挂载在XX工作站上

```bash
# 参考命令
# zqc
sshfs gaoshuai@10.58.122.42:/home1/renren_images_zcq  /home/gaoshuai/images -o reconnect
# zz
sshfs gaoshuai@172.24.1.253:/mnt/data/gaoshuai/renren/ws_zhuzhou  /home/gaoshuai/renren_images -o reconnect

```

注意：

* zz电脑挂载253, 当意外中断，可能会出现IO错误，导致挂载的文件夹不可访问。但下载的图片已经存储在253上，所以不影响。直接重新新建挂载点，修改 pipline 目录即可
* 每天的单台下载量在20~30GB，注意硬盘空间是否够用，如果在238上，还要注意 inode 是否已满( 不建议在238上部署爬虫，经常会遇到inode满的情况，而且使用的人多 )
