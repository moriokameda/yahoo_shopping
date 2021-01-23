import re
import bs4
import requests
import yaml
import json
from urllib import request, parse


class YahooShopNotifer(object):

    def __init__(self):
        self.soup_result = None
        # 検索や通知に必要なプロパティー
        with open('./config.yml', 'rt') as fp:
            text = fp.read()
        property_dict = yaml.safe_load(text)['yahoo_shop_notifier']
        self.YAHOO_SHOP_SEARCH_API = property_dict['yahoo_shop_search_api']
        self.YAHOO_APPID = property_dict['yahoo_appid']
        self.QUERY = property_dict['query']
        self.PRICE_FROM = property_dict['price_from']
        self.LINE_NOTIFY_API = property_dict['line_notify_api']
        self.LINE_NOTIFY_TOKEN = property_dict['line_notify_token']
        print(f"property_dict:  {property_dict}")
        print(f"YAHOO_SHOP_SEARCH_API: {self.YAHOO_SHOP_SEARCH_API}")
        print(f"YAHOO_APPID: {self.YAHOO_APPID}")
        print(f"QUERY: {self.QUERY}")
        print(f"PRICE_FROM: {self.PRICE_FROM}")
        print(f"LINE_NOTIFY_API: {self.LINE_NOTIFY_API}")
        print(f"LINE_NOTIFY_TOKEN: {self.LINE_NOTIFY_TOKEN}")

    def get_search_result(self):
        # 検索条件の設定
        # 参考 : https://developer.yahoo.co.jp/webapi/shopping/shopping/v1/itemsearch.html
        params = parse.urlencode({
            'appid': self.YAHOO_APPID,
            'query': self.QUERY,
            'price_from': self.PRICE_FROM
        })
        req = request.Request(self.YAHOO_SHOP_SEARCH_API + params)
        page = request.urlopen(req)
        html = page.read().decode('utf-8')
        json_html = json.loads(html)
        # print(json_html['hits'])
        save_path = 'sample.json'
        with open(save_path, 'w') as out_file:
            json.dump(json_html, out_file, indent=2)
        # print(json_html)
        # self.soup_result = bs4.BeautifulSoup(html, "lxml")
        # print(self.soup_result.find('hits'))
        self.soup_result = json_html

    def need_notice(self):
        # if self.soup_result.find('hits').get('json') is not None:
        #     if int(self.soup_result.find('hits').get('json')) > 0:
        #         # 検索結果の数が0より大きければ通知する
        #         return True
        # else:
        #     return False
        if self.soup_result['hits'] is not None:
            if len(self.soup_result['hits']) > 0:
                return True
        else:
            return False

    def _build_notification_message(self):
        # 対象商品のURLを通知メッセージに追加する
        product_urls = ''
        for link in self.soup_result['hits']:
            product_urls += link['url'] + '\n'
        return product_urls + '以上'

    def notice_to_line(self):
        message_base = '希望の商品あり！'
        product_urls = self._build_notification_message()
        message = '\n' + message_base + '\n' + product_urls
        payload = {'message': message}
        headers = {'Authorization': f'Bearer ' +  self.LINE_NOTIFY_TOKEN}
        print(headers)
        response = request.Request(self.LINE_NOTIFY_API, data=parse.urlencode(payload).encode('utf-8'),
                                   headers=headers, method='POST')
        with request.urlopen(response) as res:
            res.read()


def main():
    # send_line_notify('テスト')
    notifer = YahooShopNotifer()
    notifer.get_search_result()
    if notifer.need_notice():
        notifer.notice_to_line()

def send_line_notify(notify_message):
    line_notify_token = "3Y2Jd9AFVhW1k43QmywV51hcg0ci9gteupDuHlafDMo"
    line_notify_api = 'https://notify-api.line.me/api/notify'
    headers = {'Authorization': f'Bearer {line_notify_token}'}
    data = {'message': f'message: {notify_message}'}
    requests.post(line_notify_api,headers=headers, data= data)


if __name__ == '__main__':
    main()
    # send_line_notify('test')

