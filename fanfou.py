#!/usr/bin/env python
# -*- coding: utf-8 -*-

import oauth2 as oauth
import urllib

class fanfou():
    def __init__(self, consumer_key, consumer_secret, oauth_token, oauth_token_secret):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.oauth_token = oauth_token
        self.oauth_token_secret = oauth_token_secret
        self.token = oauth.Token(
            key = self.oauth_token,
            secret = self.oauth_token_secret
        )
        self.consumer = oauth.Consumer(
            key = self.consumer_key,
            secret = self.consumer_secret
        )
        self.client = oauth.Client(self.consumer, self.token) ###

    #search

    ##搜索全站消息(未设置隐私用户的消息)
    def search_public_timeline(self, **params):
        url = 'http://api.fanfou.com/search/public_timeline.json?'
        url += urllib.urlencode(params)
        req = oauth.Request(
            method = "GET",
            url = url,
        )
        signature_method = oauth.SignatureMethod_HMAC_SHA1()
        req.sign_request(signature_method, self.consumer, self.token)
        response, content = self.client.request(url, "GET", req.to_postdata())
        return response, content

    ##搜索全站用户(只返回其中未被ban掉的用户)
    def search_users(self, **params):
        url = 'http://api.fanfou.com/search/users.json?'
        url += urllib.urlencode(params)
        req = oauth.Request(
            method = "GET",
            url = url,
        )
        signature_method = oauth.SignatureMethod_HMAC_SHA1()
        req.sign_request(signature_method, self.consumer, self.token)
        response, content = self.client.request(url, "GET", req.to_postdata())
        return response, content

    #blocks

    #users

    #account

    def account_verify_credentials(self, **params):
        url = 'http://api.fanfou.com/account/verify_credentials.json?'
        url += urllib.urlencode(params)
        req = oauth.Request(
            method = "GET",
            url = url,
        )
        signature_method = oauth.SignatureMethod_HMAC_SHA1()
        req.sign_request(signature_method, self.consumer, self.token)
        response, content = self.client.request(url, "GET", req.to_postdata())
        return response, content

    ##返回未读的mentions, direct message 以及关注请求数量
    def account_notification(self, **params):
        url = 'http://api.fanfou.com/account/notification.json?'
        url += urllib.urlencode(params)
        req = oauth.Request(
            method = "GET",
            url = url,
        )
        signature_method = oauth.SignatureMethod_HMAC_SHA1()
        req.sign_request(signature_method, self.consumer, self.token)
        response, content = self.client.request(url, "GET", req.to_postdata())
        return response, content

    def account_update_notify_num(self, **params):
        url = 'http://api.fanfou.com/account/update_notify_num.json'
        req = oauth.Request(
            method = "POST",
            url = url,
            parameters = params,
        )
        signature_method = oauth.SignatureMethod_HMAC_SHA1()
        req.sign_request(signature_method, self.consumer, self.token)
        response, content = self.client.request(url, "POST", req.to_postdata())
        return response, content
    #saved-searches

    #photos

    #trends

    #followers

    #返回用户关注者的id列表
    def followers_ids(self, **params):
        url = 'http://api.fanfou.com/followers/ids.json?'
        url += urllib.urlencode(params)
        req = oauth.Request(
            method = "GET",
            url = url,
        )
        signature_method = oauth.SignatureMethod_HMAC_SHA1()
        req.sign_request(signature_method, self.consumer, self.token)
        response, content = self.client.request(url, "GET", req.to_postdata())
        return response, content

    #favorites

    #friendships

    #friends

    ##返回用户好友的id列表
    def friends_ids(self, **params):
        url = 'http://api.fanfou.com/friends/ids.json?'
        url += urllib.urlencode(params)
        req = oauth.Request(
            method = "GET",
            url = url,
        )
        signature_method = oauth.SignatureMethod_HMAC_SHA1()
        req.sign_request(signature_method, self.consumer, self.token)
        response, content = self.client.request(url, "GET", req.to_postdata())
        return response, content

    #statuses

    #返回用户的前100个关注者
    def statuses_home_timeline(self, **params):
        url = 'http://api.fanfou.com/statuses/home_timeline.json?'
        url += urllib.urlencode(params)
        req = oauth.Request(
            method = "GET",
            url = url,
        )
        signature_method = oauth.SignatureMethod_HMAC_SHA1()
        req.sign_request(signature_method, self.consumer, self.token)
        response, content = self.client.request(url, "GET", req.to_postdata())
        return response, content

    def statuses_followers(self, **params):
        url = 'http://api.fanfou.com/statuses/followers.json?'
        url += urllib.urlencode(params)
        req = oauth.Request(
            method = "GET",
            url = url,
        )
        signature_method = oauth.SignatureMethod_HMAC_SHA1()
        req.sign_request(signature_method, self.consumer, self.token)
        response, content = self.client.request(url, "GET", req.to_postdata())
        return response, content

    ##发送消息
    def statuses_update(self, **params):
        url = 'http://api.fanfou.com/statuses/update.json'
        req = oauth.Request(
            method = "POST",
            url = url,
            parameters = params,
        )
        signature_method = oauth.SignatureMethod_HMAC_SHA1()
        req.sign_request(signature_method, self.consumer, self.token)
        response, content = self.client.request(url, "POST", req.to_postdata())
        return response, content

    #显示回复当前用户的20条消息(未设置隐私用户和登录用户好友的消息)
    def statuses_replies(self, **params):
        url = 'http://api.fanfou.com/statuses/replies.json?'
        url += urllib.urlencode(params)
        req = oauth.Request(
            method = "GET",
            url = url,
        )
        signature_method = oauth.SignatureMethod_HMAC_SHA1()
        req.sign_request(signature_method, self.consumer, self.token)
        response, content = self.client.request(url, "GET", req.to_postdata())
        return response, content

    #返回用户好友
    def statuses_friends(self, **params):
        url = 'http://api.fanfou.com/statuses/friends.json?'
        url += urllib.urlencode(params)
        req = oauth.Request(
            method = "GET",
            url = url,
        )
        signature_method = oauth.SignatureMethod_HMAC_SHA1()
        req.sign_request(signature_method, self.consumer, self.token)
        response, content = self.client.request(url, "GET", req.to_postdata())
        return response, content

    def statuses_mentions(self, **params):
        url = 'http://api.fanfou.com/statuses/mentions.json?'
        url += urllib.urlencode(params)
        req = oauth.Request(
            method = "GET",
            url = url,
        )
        signature_method = oauth.SignatureMethod_HMAC_SHA1()
        req.sign_request(signature_method, self.consumer, self.token)
        response, content = self.client.request(url, "GET", req.to_postdata())
        return response, content
    #direct-messages
