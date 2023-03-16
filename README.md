# V2Board Telegram Bot via Python
- [V2Board Telegram Bot via Python](#v2board-telegram-bot-via-python)
  - [现有功能](#现有功能)
  - [现有指令](#现有指令)
  - [常规使用](#常规使用)
  - [申请 Telegram Bot Token](#申请-telegram-bot-token)
  - [Docker部署](#docker部署)
    - [1. 安装Docker](#1-安装docker)
    - [2. 部署容器](#2-部署容器)
      - [2.1 通过docker run部署](#21-通过docker-run部署)
        - [2.1.1 下载配置文件到你喜欢的位置](#211-下载配置文件到你喜欢的位置)
        - [2.1.2 按自己的情况修改config.yaml](#212-按自己的情况修改configyaml)
        - [2.1.3-A 运行容器(不使用SSH密钥)](#213-a-运行容器不使用ssh密钥)
        - [2.1.3-B 运行容器(使用SSH密钥)](#213-b-运行容器使用ssh密钥)
      - [2.2 通过docker compose部署](#22-通过docker-compose部署)
        - [2.2.1 确认docker compose命令](#221-确认docker-compose命令)
        - [2.2.2 下载配置文件及compose文件](#222-下载配置文件及compose文件)
        - [2.2.3-A 使用环境变量进行配置时](#223-a-使用环境变量进行配置时)
        - [2.2.3-B 通过config.yaml文件进行配置时](#223-b-通过configyaml文件进行配置时)
        - [2.2.4 运行容器](#224-运行容器)
      - [2.3 参数说明](#23-参数说明)
      - [2.4 环境变量说明](#24-环境变量说明)
      - [2.5 Image tag说明](#25-image-tag说明)
      - [2.6 特别说明](#26-特别说明)

一个简单的项目，让 V2Board Telegram Bot 支持更丰富的功能。
快速反馈群：[https://t.me/v2board_python_bot](https://t.me/v2board_python_bot)

Python 版本需求 >= 3.8

## 现有功能
- 基于MySQL，支持以SSH方式登录
- 自动删除群聊中信息
- 自动推送订单、工单给管理
- 每日自动推送数据统计
- 支持Bot内绑定、解绑
- 支持获取用户信息、订阅、邀请
- 支持获取套餐并生成购买按钮

## 现有指令
|   指令   |   参数    |         描述         |
| :------: | :-------: | :------------------: |
|   ping   |    无     |     获取聊天的ID     |
|   bind   | 邮箱 密码 | 绑定该邮箱到Telegram |
|  unbind  | 邮箱 密码 | 解绑该邮箱的Telegram |
|  mysub   |    无     | 获取该账号的订阅链接 |
|  myinfo  |    无     | 获取该账号的订阅信息 |
| myusage  |    无     | 获取该账号的流量明细 |
| myinvite |    无     | 获取该账号的邀请信息 |
| buyplan  |    无     |   获取购买套餐链接   |
| website  |    无     |     获取网站链接     |

## 常规使用
```
# apt install git 如果你没有git的话
git clone https://github.com/DyAxy/V2Board_Telegram_Bot.git
# 进程常驻可参考 screen 或 nohup
# 你需要安装好 pip3 的包管理
cd V2Board_Telegram_Bot
pip3 install -r requirements.txt
cp config.yaml.example config.yaml
nano config.yaml
# 编辑 line 2 为你的V2Board地址，最后请不要加 / 符号
# 编辑 line 3 为你的Bot Token
# 编辑 line 4、5 为你的ID和群ID，通过 /ping 获取
# 编辑 line 8~12 为你的MySQL连接信息
# 编辑 line 14 如果你需要SSH连接数据库 则为true
# 编辑 line 15~24 为你的SSH连接信息
python3 bot.py
```

## 申请 Telegram Bot Token

1. 私聊 [https://t.me/BotFather](https://https://t.me/BotFather)
2. 输入 `/newbot`，并为你的bot起一个**响亮**的名字
3. 接着为你的bot设置一个username，但是一定要以bot结尾，例如：`v2board_bot`
4. 最后你就能得到bot的token了，看起来应该像这样：`123456789:gaefadklwdqojdoiqwjdiwqdo`

## Docker部署
**特别需要注意的是，如果v2board_telegram_bot与面板数据库部署于同一主机时，请仔细阅读特别说明**
### 1. 安装Docker  
详细方法参详Linux发行版Wiki 或 [Docker Docs](https://docs.docker.com/desktop/get-started/)  

### 2. 部署容器
**提供两种部署示例，二选一参考使用**
#### 2.1 通过docker run部署  

##### 2.1.1 下载配置文件到你喜欢的位置  
    curl -JL https://github.com/DyAxy/V2Board_Python_Bot/raw/master/config.yaml.example -o config.yaml

##### 2.1.2 按自己的情况修改config.yaml  

##### 2.1.3-A 运行容器(不使用SSH密钥)  
    docker run -d --name v2bpybot -v ./config.yaml:/V2Board_Python_Bot/config.yaml moefaq/v2board_python_bot-docker:latest

##### 2.1.3-B 运行容器(使用SSH密钥)  
    docker run -d --name v2bpybot -v ./config.yaml:/V2Board_Python_Bot/config.yaml \
    -v ./private.key:/V2Board_Python_Bot/private.key moefaq/v2board_python_bot-docker:latest

#### 2.2 通过docker compose部署  
**该部署方式分为两种配置方式，环境变量配置方式更为简便**

##### 2.2.1 确认docker compose命令  
docker-compose命令属于Compose V1使用的独立命令；  
在Compose V2中，该命令已被重写并属于Docker CLI的一部分，即: docker compose  
部署前请先确保您的docker compose命令可用。  
如有问题，请先参详Linux发行版的Wiki 或 [Docker Docs](https://docs.docker.com/compose/install/linux/)  

##### 2.2.2 下载配置文件及compose文件
    curl -JL https://github.com/DyAxy/V2Board_Python_Bot/raw/master/config.yaml.example -o config.yaml
    curl -JL https://github.com/DyAxy/V2Board_Python_Bot/raw/master/docker-compose.yaml.example -o docker-compose.yaml
***通过环境变量配置方式部署时，无需下载config.yaml.examlpe***

##### 2.2.3-A 使用环境变量进行配置时
编辑docker-compose.yaml文件，按照自己的情况将参数值填写到environment下的各项当中。  
同时保持volumes相关内容处于注释状态。
详细说明见[2.4 环境变量说明](#24-环境变量说明)

##### 2.2.3-B 通过config.yaml文件进行配置时
1. 按自己的情况编辑config.yaml  
2. 编辑docker-compose.yaml  

       - "<V2Board_Python_Bot-docker_data>/config.yaml:/V2Board_Python_Bot/config.yaml"  
   <V2Board_Python_Bot-docker_data>/config.yaml修改为config.yaml文件实际路径  

       - "<V2Board_Python_Bot-docker_data>/sshkey.pem:/V2Board_Python_Bot/sshkey.pem"  
   <V2Board_Python_Bot-docker_data>/sshkey.pem修改为sshkey.pem文件实际路径, **不使用SSH密钥时删除该行**  

##### 2.2.4 运行容器
    docker compose -f docker-compose.yaml -p v2bpybot up

#### 2.3 参数说明
<table>
    <tr>
        <th>选项/参数</th>
        <th>说明</th>
    </tr>
    <tr>
        <td>--name v2bpybot</td>
        <td>容器名称设置为: v2bpybot</td>
    </tr>
    <tr>
        <td>-v ./config.yaml:/V2Board_Python_Bot/config.yaml</td>
        <td rowspan="2">将配置文件config.yaml挂载至容器中</td>
    </tr>
    <tr>
        <td>&lt;V2Board_Python_Bot-docker_data&gt;/config.yaml:/V2Board_Python_Bot/config.yaml</td>
    </tr>
    <tr>
        <td>moefaq/v2board_python_bot-docker:latest</td>
        <td>指定镜像, latest为镜像tag, 详见<a href="#25-image-tag%E8%AF%B4%E6%98%8E">2.5 Image tag说明</a></td>
    </tr>
    <tr>
        <td>-v ./private.key:/V2Board_Python_Bot/private.key</td>
        <td rowspan="2">仅使用密钥连接数据库时使用, 将私钥挂载至容器中</td>
    </tr>
    <tr>
        <td>&lt;V2Board_Python_Bot-docker_data&gt;/sshkey.pem:/V2Board_Python_Bot/sshkey.pem</td>
    </tr>
    <tr>
        <td>-f docker-compose.yaml</td>
        <td>指定compose文件</td>
    </tr>
    <tr>
        <td>-p v2bpybot</td>
        <td>指定project名称, 指定后容器名形如v2bpybot-bot-1</td>
    </tr>
</table>

#### 2.4 环境变量说明
容器未挂载config.yaml时，entrypoint.sh会根据环境变量生成config.yml。  
注：distroless构建的镜像暂不支持环境变量生产配置文件。
| 选项/参数              | 说明                                                                                                                                                                                              |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| BOT_WEBSITE            | V2Board地址<br>e.g. https://awesomeV2Board.com                                                                                                                                                    |
| BOT_TOKEN              |                                                                                                                                                                                                   |
| BOT_ADMIN_PATH         | v2board的后台路径<br>e.g. admin                                                                                                                                                                   |
| BOT_ADMIN_ID           | 管理员telegram id，使用半角逗号(,)分隔。<br>e.g. 123456789,321654987,555555,111222                                                                                                                |
| BOT_GROUP_ID           | 群组的telegram id<br>e.g. -147258369                                                                                                                                                              |
| V2BOARD_DB_IP          | 可访问v2board数据库的IP<br>bot与v2board数据库部署于同一主机时，请阅读[2.6 特别说明](#26-特别说明)                                                                                                             |
| V2BOARD_DB_PORT        | 可访问v2board数据库的端口                                                                                                                                                                         |
| V2BOARD_DB_USER        | 可访问v2board数据库的用户名                                                                                                                                                                       |
| V2BOARD_DB_PASS        | 可访问v2board数据库的用户密码                                                                                                                                                                     |
| V2BOARD_DB_NAME        | v2board数据库名称                                                                                                                                                                                 |
| V2BOARD_DB_SSH_ENABLE  | 是否启用ssh进行数据库连接。<br>可选值为：true / false                                                                                                                                             |
| V2BOARD_DB_SSH_TYPE    | ssh认证方式。<br>可选值为：passwd / pkey<br>值为passwd时，使用密码进行认证，V2BOARD_DB_SSH_KEY 与 V2BOARD_DB_SSH_KEYPASS将不生效。<br>值为pkey时，使用私钥进行认证，V2BOARD_DB_SSH_PASS将不生效。 |
| V2BOARD_DB_SSH_IP      | 数据库所在主机的IP。<br>bot与v2board数据库部署于同一主机时，请阅读[2.6 特别说明](#26-特别说明)                                                                                                                |
| V2BOARD_DB_SSH_PORT    | 可与数据库主机进行ssh连接的端口                                                                                                                                                                   |
| V2BOARD_DB_SSH_USER    | 用于建立ssh连接的用户名                                                                                                                                                                           |
| V2BOARD_DB_SSH_PASS    | 用于建立ssh连接的用户密码                                                                                                                                                                         |
| V2BOARD_DB_SSH_KEY     | 用户建立ssh连接的私钥内容。在进行该项配置时请注意：<br>1. 不能删除开头的"\|\-"；<br>2. 注意缩进                                                                                                   |
| V2BOARD_DB_SSH_KEYPASS | 用于ssh连接的私钥密码，没有密码时该项留空                                                                                                                                                         |

#### 2.5 Image tag说明
| tag        | 说明                                                  | image size                                                                                                       |
| ---------- | ----------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| latest     | alpine 3.17 + python 3.8                              | ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/moefaq/v2board_python_bot-docker/latest)     |
| 3.8        | 同latest                                              | ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/moefaq/v2board_python_bot-docker/py3.8)      |
| 3.9        | alpine 3.17 + python 3.9                              | ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/moefaq/v2board_python_bot-docker/py3.9)      |
| 3.10       | alpine 3.17 + python 3.10                             | ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/moefaq/v2board_python_bot-docker/py3.10)     |
| 3.11       | alpine 3.17 + python 3.11                             | ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/moefaq/v2board_python_bot-docker/py3.11)     |
| distroless | 使用google distroless镜像构建<br>debian11 +python 3.9 | ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/moefaq/v2board_python_bot-docker/distroless) |

#### 2.6 特别说明
当bot与v2board数据库部署在同一主机时，由于docker容器默认的network driver为bridge，bot将无法直接通过Loopback address（127.0.0.1/localhost/::1等）访问数据库。以下给出几种解决办法供选择：  
1. 使用ssh方式连接数据库
   详见[常规使用](#常规使用)。  
   其中，应将ssh ip地址设置为：host.docker.internal  
   将database ip设置为：127.0.0.1
2. 修改compose文件，去除两处有关networks的对象/数组。  
   然后将services:bot:下添加network_mode: host对象，将容器网络模式设置为host  
**隔离性：方案1＞方案2，通用性：方案1＜方案2**，建议使用方案1。  
另外，出于安全角度考虑，不建议数据库监听至0.0.0.0。
