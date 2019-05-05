#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os.path
from pymongo import MongoClient

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

from tornado.options import define, options
define("port", default=8001, help="run on the given port", type=int)

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')
    
class BaseHandler(tornado.web.RequestHandler):
    def get(self):
        self.write_error(404)

    def write_error(self, status_code, **kwargs):
        if status_code == 404:
            # self.render('404.html')
            self.write("%s Not Found" % status_code)
        else:
            self.write("Gosh darnit, user! You caused a %d error." % status_code)

class ResultHandler(tornado.web.RequestHandler):
    typeMap = {'product': '产品', 'miniapp': '小程序'}

    def fetch_data(self, post_type, post_date):
        client = MongoClient()
        database = client['BgSpider']
        collection = database[post_type+'_items']
        postList = collection.find(
            {'post_date':post_date}, 
            {'_id': 0, 'post_abstract': 1, 'post_title': 1, 'post_url': 1}
        )
        client.close()
        return postList

    def post(self):
        headline = self.get_argument('headline')
        post_type = self.get_arguments('post_type')
        post_date = self.get_argument('post_date')
        postList = []
        post_type_zh = []

        for i in range(len(post_type)):
            postList.append(self.fetch_data(post_type[i], post_date))
            post_type_zh.append(self.typeMap[post_type[i]])

        self.render('result.html', headline=headline, post_date=post_date, 
            post_type=post_type_zh, postList=postList)

if __name__ == '__main__':
    tornado.options.parse_command_line()
    app = tornado.web.Application(
        handlers=[
            (r'/', IndexHandler), 
            (r'/result', ResultHandler),
            (r".*", BaseHandler)
        ],
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        debug=True
    )
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
