# -*- coding: UTF-8 -*-
import getpass
import urllib
from google.appengine.api import xmpp
from google.appengine.ext import db
from google.appengine.api import users
import base64

import fanfou
import settings

from django.utils import simplejson as json
from google.appengine.api import memcache

EXPIRE_TIME = 604800 #七天，最多一个月

MAX_MESSAGE_COUNT = 'MAX_MESSAGE_COUNT'

ID_TO_NUMBER_PREFIX = 'ID_TO_NUMBER_'
NUMBER_TO_ID_PREFIX = 'NUMBER_TO_ID_'
SCREEN_NAME_PREFIX = 'SCREEN_NAME_'
CONTENT_PREFIX = 'CONTENT_'
STATUS_EXISTS_PREFIX = 'STATUS_EXISTS_' #判断消息 id 是否已存在

INPUT_ERROR_MESSAGE = '您的输入有误，请重新输入。'
TOO_MANY_BINDING_MESSAGE = '由于 GAE 目前的限制，小机器人不能同时伺候两个人…'
TODO_ERROR_MESSAGE = '该功能还没写好=..='

NETWORK_ERROR = '网络错误，请重试。'

class users(db.Model):
    gid = db.StringProperty(required=True)
    name = db.StringProperty(required=True)
    pwd = db.StringProperty(required=True)

    last_home_tl = db.StringProperty()
    last_mentions = db.StringProperty()
    last_reply = db.StringProperty()
    last_dm = db.StringProperty()

    auto_home_tl = db.IntegerProperty()
    auto_mentions = db.IntegerProperty()
    auto_replies = db.IntegerProperty()
    auto_dm = db.IntegerProperty()
    feedback = db.IntegerProperty() #todo

##memcache
def memcache_get(key):
    return memcache.get(key)

def memcache_add(key, value):
    result = memcache.get(key)
    if result is not None:
        memcache.add(key, value, EXPIRE_TIME)
    else:
        memcache.set(key, value, EXPIRE_TIME)

def get_max_message_count():
    result = memcache.get(MAX_MESSAGE_COUNT)
    if result is not None:
        return result
    else:
        memcache.add(MAX_MESSAGE_COUNT, 1, EXPIRE_TIME)
        return 1

def get_status_real_id(gid, id):
    result = memcache_get(NUMBER_TO_ID_PREFIX + id)
    return result

def init_max_message_count(gid):
    memcache.flush_all()

def inc_max_message_count():
    memcache.incr(MAX_MESSAGE_COUNT)

def status_exists(key): #判断消息是不是已经在 memcache 中
    result = memcache.get(STATUS_EXISTS_PREFIX + key)
    if result is None:
        memcache.add(STATUS_EXISTS_PREFIX + key, 1, EXPIRE_TIME)
        return 0
    else:
        return 1
#######

#######

def init_message_count(gid):
    init_max_message_count(gid)
    xmpp.send_message(gid, '@ 的 id 号初始化完毕。')

def give_instructions(gid):
    xmpp.send_message(gid, manual_message)

def get_user_oauth_info(gid): #从 SQL 中获取 oAuth 信息
    result = db.GqlQuery("SELECT * FROM users WHERE gid='%s'"%(gid))[0]
    name = result.name
    pwd = result.pwd
    return [name,pwd]

##home timeline
def refresh_home_timeline(gid): #done 格式调整
    oauth_token, oauth_secret = get_user_oauth_info(gid)
    a = fanfou.fanfou(settings.consumer_key, settings.consumer_secret, oauth_token, oauth_secret)
    response, content = a.statuses_home_timeline()
    content = json.loads(content)
    updated_status_id = content[0]['id']
    update_last_home_tl(gid, updated_status_id)
    for item in reversed(content):
        message_count = get_max_message_count()
        message_id = item['id']
        if not status_exists(message_id): #判重
            memcache_add('%s%s'%(NUMBER_TO_ID_PREFIX, `message_count`), message_id)
            conversation = '%s: %s'%(item['user']['screen_name'], item['text'])
            memcache_add('%s%s'%(SCREEN_NAME_PREFIX, `message_count`), item['user']['screen_name'])
            memcache_add('%s%s'%(CONTENT_PREFIX, `message_count`), conversation)
            inc_max_message_count()
            xmpp.send_message(gid, '%s #%s'%(conversation, message_count))

def update_last_home_tl(gid, updated_status_id): #更新上一条最新的 home timeline 
    result = db.GqlQuery("SELECT * FROM users WHERE gid='%s'"%(gid))[0]
    result.last_home_tl = updated_status_id
    result.put()

def auto_refresh_home_timeline(gid, last_id): #待合并
    oauth_token, oauth_secret = get_user_oauth_info(gid)
    a = fanfou.fanfou(settings.consumer_key, settings.consumer_secret, oauth_token, oauth_secret)
    response, content = a.statuses_home_timeline(since_id=last_id)
    content = json.loads(content)
    updated_status_id = content[0]['id']
    update_last_home_tl(gid, updated_status_id)
    for item in reversed(content):
        message_count = get_max_message_count()
        message_id = item['id']
        if not status_exists(message_id): #判重
            memcache_add('%s%s'%(NUMBER_TO_ID_PREFIX, `message_count`), message_id)
            conversation = '%s: %s'%(item['user']['screen_name'], item['text'])
            memcache_add('%s%s'%(SCREEN_NAME_PREFIX, `message_count`), item['user']['screen_name'])
            memcache_add('%s%s'%(CONTENT_PREFIX, `message_count`), conversation)
            inc_max_message_count()
            xmpp.send_message(gid, '%s #%s'%(conversation, message_count))
#######home timeline
##replies
def show_new_replies(gid):
    oauth_token, oauth_secret = get_user_oauth_info(gid)
    a = fanfou.fanfou(settings.consumer_key, settings.consumer_secret, oauth_token, oauth_secret)
    response, content = a.statuses_replies()
    content = json.loads(content)
    for item in reversed(content):
        message_count = get_max_message_count()
        message_id = item['id']
        if not status_exists(message_id):
            memcache_add('%s%s'%(NUMBER_TO_ID_PREFIX, `message_count`), message_id)
            conversation = '%s: %s'%(item['user']['screen_name'], item['text'])
            memcache_add('%s%s'%(SCREEN_NAME_PREFIX, `message_count`), item['user']['screen_name'])
            inc_max_message_count()
            xmpp.send_message(gid, '%s #%s'%(conversation, message_count))

def update_last_reply(gid, updated_status_id):
    result = db.GqlQuery("SELECT * FROM users WHERE gid='%s'"%(gid))[0]
    result.last_reply = updated_status_id
    result.put()

def auto_refresh_reply(gid, last_id):
    oauth_token, oauth_secret = get_user_oauth_info(gid)
    a = fanfou.fanfou(settings.consumer_key, settings.consumer_secret, oauth_token, oauth_secret)
    if last_id != '':
        response, content = a.statuses_replies(since_id=last_id)
    else:
        response, content = a.statuses_replies()
    content = json.loads(content)
    for item in reversed(content):
        message_count = get_max_message_count()
        message_id = item['id']
        if not status_exists(message_id):
            memcache_add('%s%s'%(NUMBER_TO_ID_PREFIX, `message_count`), message_id)
            conversation = '%s: %s'%(item['user']['screen_name'], item['text'])
            memcache_add('%s%s'%(CONTENT_PREFIX, `message_count`), conversation)
            memcache_add('%s%s'%(SCREEN_NAME_PREFIX, `message_count`), item['user']['screen_name'])
            inc_max_message_count()
            update_last_reply(gid, item['id']) #更新最新的 id
            xmpp.send_message(gid, '%s #%s'%(conversation, message_count))

def reply_statuses(gid, mes):
    params = mes.split(" ")
    reply_id = get_status_real_id(gid, params[1])
    reply_content = ' '.join(mes.split(" ")[2:])
    result = db.GqlQuery("SELECT * FROM users WHERE gid='%s'"%(gid))[0]
    oauth_token, oauth_secret = get_user_oauth_info(gid)
    a = fanfou.fanfou(settings.consumer_key, settings.consumer_secret, oauth_token, oauth_secret)
    response, content = a.statuses_update(
        status = "@%s %s"%(memcache_get(SCREEN_NAME_PREFIX + params[1]), reply_content),
        in_reply_to_status_id = reply_id,
    )

#######replies
##mentions
def update_last_mention(gid, updated_status_id):
    result = db.GqlQuery("SELECT * FROM users WHERE gid='%s'"%(gid))[0]
    result.last_mentions = updated_status_id
    result.put()

def show_new_mentions(gid, since_id):
    oauth_token, oauth_secret = get_user_oauth_info(gid)
    a = fanfou.fanfou(settings.consumer_key, settings.consumer_secret, oauth_token, oauth_secret)
    if since_id == '': #手动查看新 mentions
        response, content = a.statuses_mentions()
        content = json.loads(content)
        for item in reversed(content):
            message_count = get_max_message_count()
            message_id = item['id']
            if not status_exists(message_id):
                memcache_add('%s%s'%(NUMBER_TO_ID_PREFIX, `message_count`), message_id)
                conversation = '%s: %s'%(item['user']['screen_name'], item['text'])
                memcache_add('%s%s'%(CONTENT_PREFIX, `message_count`), conversation)
                memcache_add('%s%s'%(SCREEN_NAME_PREFIX, `message_count`), item['user']['screen_name'])
                inc_max_message_count()
                update_last_mention(gid, item['id'])
                xmpp.send_message(gid, '%s #%s'%(conversation, message_count))
    else: #自动获取新 mentions
        since_id = db.GqlQuery("SELECT * FROM users WHERE gid='%s'"%(gid))[0].last_mentions
        response, content = a.statuses_mentions(since_id=since_id)
        content = json.loads(content)
        for item in reversed(content):
            message_count = get_max_message_count()
            message_id = item['id']
            if not status_exists(message_id):
                memcache_add('%s%s'%(NUMBER_TO_ID_PREFIX, `message_count`), message_id)
                conversation = '%s: %s'%(item['user']['screen_name'], item['text'])
                memcache_add('%s%s'%(CONTENT_PREFIX, `message_count`), conversation)
                memcache_add('%s%s'%(SCREEN_NAME_PREFIX, `message_count`), item['user']['screen_name'])
                inc_max_message_count()
                update_last_mention(gid, item['id'])
                xmpp.send_message(gid, '%s #%s'%(conversation, message_count))
#######mentions
##dm
def new_dm_notification(gid):
    oauth_token, oauth_secret = get_user_oauth_info(gid)
    a = fanfou.fanfou(settings.consumer_key, settings.consumer_secret, oauth_token, oauth_secret)
    response, content = a.account_notification()
    content = json.loads(content)
    new_dm_num = content['direct_messages']
    if new_dm_num:
        xmpp.send_message(gid, '你有 %s 封新私信'%(new_dm_num))
#######dm

def auth_oauth_info(gid):
    xmpp.send_message(gid, TODO_ERROR_MESSAGE)

def easter_color_eggs(gid, mes): #hint
    if mes.find("饿了".decode("utf-8")) != -1:
        xmpp.send_message(gid, "肯德基 24 小时外卖热线 4008-823-823；麦当劳 24 小时外卖热线 4008-517-517.")
    pass

def update_statuses(gid, mes):
    oauth_token, oauth_secret = get_user_oauth_info(gid)
    a = fanfou.fanfou(settings.consumer_key, settings.consumer_secret, oauth_token, oauth_secret)
    response, content = a.statuses_update(status=mes)
    t = json.loads(content)
    easter_color_eggs(gid, mes)

def retweet_statuses(gid, mes):
    params = mes.split(" ")
    retweet_id = get_status_real_id(gid, params[1])
    if len(params) == 2: #没有附加内容
        result = db.GqlQuery("SELECT * FROM users WHERE gid='%s'"%(gid))[0]
        oauth_token, oauth_secret = get_user_oauth_info(gid)
        a = fanfou.fanfou(settings.consumer_key, settings.consumer_secret, oauth_token, oauth_secret)
        response, content = a.statuses_update(
            status = "RT@%s"%(memcache_get(CONTENT_PREFIX + params[1])),
            repost_status_id = retweet_id,
        )
    else: #有附加内容
        result = db.GqlQuery("SELECT * FROM users WHERE gid='%s'"%(gid))[0]
        oauth_token, oauth_secret = get_user_oauth_info(gid)
        retweet_content = ' '.join(mes.split(" ")[2:])
        a = fanfou.fanfou(settings.consumer_key, settings.consumer_secret, oauth_token, oauth_secret)
        response, content = a.statuses_update(
            status = "%s RT@%s"%(retweet_content, memcache_get(CONTENT_PREFIX + params[1])),
            repost_status_id = retweet_id,
        )

def bind_user(gid, mes):
    result = db.GqlQuery("SELECT * FROM users")
    if result.count() > 0:
        xmpp.send_message(gid, TOO_MANY_BINDING_MESSAGE)
    elif len(mes.split(" ")) != 3:
        xmpp.send_message(gid, INPUT_ERROR_MESSAGE)
    else:
        e = users(
            gid = gid,                              
            name = mes.split(' ')[1],
            pwd = mes.split(' ')[2],
            last_home_tl = '',                      #最新一条获取的 home tl
            last_mentions = '',                     #最新一条获取的 mention
            last_reply = '',
            last_dm = '',                           
            auto_home_tl = 1,                       #自动刷新 home tl，默认打开
            auto_mentions = 0,                      #自动刷新 mentions，默认关闭
            auto_replies = 1,                       #自动刷新 replies，默认打开
            auto_dm = 1,                            #自动提醒 dm，默认打开
            feedback = 0,                           #发送成功反馈，默认关闭
        )
        e.put()
        xmpp.send_message(gid, '绑定成功')

def auto_refresh(gid):
    result = db.GqlQuery("SELECT * FROM users WHERE gid='%s'"%(gid))[0]
    if result.auto_home_tl:
        last_home_tl = result.last_home_tl
        if last_home_tl != '':
            auto_refresh_home_timeline(gid, last_home_tl)
        else:
            refresh_home_timeline(gid)

    if result.auto_replies:
        last_reply = result.last_reply
        if last_reply != '': #新 @
            auto_refresh_reply(gid, last_reply)
        else: #重新刷新 @
            auto_refresh_reply(gid, '')

    if result.auto_dm: #todo
        pass
        #new_dm_notification(gid)

    if result.auto_mentions:
        last_mentions = result.last_mentions
        show_new_mentions(gid, since_id=last_mentions)

def params_handler(mes, gid):
    if mes == '-@':
        show_new_replies(gid)
    elif mes == '-rt':
        show_new_mentions(gid, since_id='')
    elif mes == '-d':
        new_dm_notification(gid)

    elif mes == '-on':
        result = db.GqlQuery("SELECT * FROM users WHERE gid='%s'"%(gid))[0]
        result.auto_home_tl = 1
        result.put()
        xmpp.send_message(gid, 'home timeline 刷新已打开。')
    elif mes == '-off':
        result = db.GqlQuery("SELECT * FROM users WHERE gid='%s'"%(gid))[0]
        result.auto_home_tl = 0
        result.put()
        xmpp.send_message(gid, 'home timeline 刷新已关闭。')
    elif mes == '-rton':
        result = db.GqlQuery("SELECT * FROM users WHERE gid='%s'"%(gid))[0]
        result.auto_mentions = 1
        result.put()
        xmpp.send_message(gid, 'mentions 提醒已打开，你会接收到别人 RT/@ 提到你的消息。')
    elif mes == '-rtoff':
        result = db.GqlQuery("SELECT * FROM users WHERE gid='%s'"%(gid))[0]
        result.auto_mentions = 0
        result.put()
        xmpp.send_message(gid, 'mentions 提醒已关闭。')
    elif mes == '-sn':
        result = db.GqlQuery("SELECT * FROM users WHERE gid='%s'"%(gid))[0]
        result.auto_replies = 1
        result.put()
        xmpp.send_message(gid, 'replies 提醒已打开，你会接收到别人 @ 你的消息（不包括 RT 到你的）。')
    elif mes == '-sf':
        result = db.GqlQuery("SELECT * FROM users WHERE gid='%s'"%(gid))[0]
        result.auto_replies = 0
        result.put()
        xmpp.send_message(gid, 'replies 提醒已关闭。')

    elif mes == '-init':
        init_message_count(gid)
    elif mes == '-auth':
        auth_oauth_info(gid)
    elif mes == '-r':
        refresh_home_timeline(gid)
    elif mes == '-h':
        give_instructions(gid)

    elif mes[:2] == '-b':
        if len(mes.split(" ")) < 3:
            xmpp.send_message(gid, INPUT_ERROR_MESSAGE)
        else:
            bind_user(gid, mes)
    elif mes[:2] == '-@':
        if len(mes.split(" ")) < 3:
            xmpp.send_message(gid, INPUT_ERROR_MESSAGE)
        else:
            reply_statuses(gid, mes)
    elif mes[:3] == '-rt':
        if len(mes.split(" ")) < 2:
            xmpp.send_message(gid, INPUT_ERROR_MESSAGE)
        else:
            retweet_statuses(gid, mes)
    elif mes[:4] == '-fav':
        xmpp.send_message(gid, TODO_ERROR_MESSAGE)
    elif mes == '-x':
        xmpp.send_message(gid, base64.b64decode(x))
    else:
        update_statuses(gid, mes)

manual_message = u"""
    -h                      查看帮助
    -b key1 key2            绑定帐号

    -on                     开启 home timeline 自动刷新
    -off                    关闭 home timeline 自动刷新
    -sn                     开启 @ 提醒
    -sf                     关闭 @ 提醒
    -rton                   开启 mentions 提醒
    -rtoff                  关闭 mentions 提醒
    -d                      查看有没有新私信

    -r                      立即刷新 tl
    -rt                     查看最新 20 条提到你的消息（包括 RT/@ 提到的）
    -@                      查看最新 20 条 @ 你的消息

    -init                   将消息的 id 号清零（用于你觉得 id 号过长不容易输入的时候）
    -@ num xxx              回复 id 号为 num 的消息，回复内容为 xxx
    -rt num xxx             转发 id 为 num 的消息，xxx 为转发附加的内容（可没有附加内容）
"""

x = "SSdtIHRoZSBvbmUgd2hvIHdhbnRzIHRvIGJlIHdpdGggeW91LApkZWVwIGluc2lkZSBJIGhvcGUgeW91IGZlZWwgaXQgdG9vLAp3YWl0ZWQgb24gYSBsaW5lIG9mIGdyZWVucyBhbmQgYmx1ZXMsCmp1c3QgdG8gYmUgdGhlIG5leHQgdG8gYmUgd2l0aCB5b3Uu"