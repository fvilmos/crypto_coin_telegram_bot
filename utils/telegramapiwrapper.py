import requests
import urllib
import json
import datetime

# https://core.telegram.org/bots/api#available-methods
# https://core.telegram.org/bots#6-botfather
# https://djangostars.com/blog/how-to-create-and-deploy-a-telegram-bot/


class TelegramAPIWrapper():

    def __init__(self, TOKEN='',MSGAGE=5):

        self.MSGAGE = MSGAGE 
        self.TOKEN = TOKEN
        self.URL = "https://api.telegram.org/bot{}/".format(self.TOKEN)

    def set_token(self,token):
        """Sets the TOKEN, received from Telegram

        Args:
            token (str): Unique TOKEN
        """
        self.TOKEN = token
        self.URL = "https://api.telegram.org/bot{}/".format(self.TOKEN)


    def get_response_from_url(self,url):
        """
        retun the response from URL

        Args:
            url ([type]): URL

        Returns:
            [type]: str
        """
        resp = requests.get(url)
        resp_txt = resp.content.decode('utf8')

        return resp_txt

    def send_msg(self, msg='',chat_id=''):
        """
        uses telegrame sendMessage API
        see: https://core.telegram.org/bots/api

        Args:
            msg (str, optional): String message to sent. Defaults to ''.
            chat_id (str, optional): telegram chat id. Defaults to ''.
        """
        # format, constract the string to be posted
        msg = urllib.parse.quote_plus(msg)
        url = self.URL + 'sendMessage?text={}&chat_id={}'.format(msg,chat_id)

        return self.get_response_from_url(url)

    def get_msgs(self, OFFSET=None):
        """
        uses telegrame getUpdates API, format it to json
        see: https://core.telegram.org/bots/api
        """
        url = self.URL+ "getUpdates"

        if OFFSET is not None:
            url +='?offset={}'.format(OFFSET)

         
        return json.loads(self.get_response_from_url(url))

    def get_last_msg(self):
        """
        Return the last valid msg, not older than the MSGAGE defined
        uses telegrame getUpdates API, offset parameter
        see: https://core.telegram.org/bots/api
        """
        msgs = self.get_msgs()
        if msgs['ok'] is not False:

            if len(msgs['result'])> 0:
                msg = sorted(self.get_msgs()['result'], key = lambda x: x['update_id'])[-1]

                msg_date = int(msg['message']['date'])
                curret_date = int(datetime.datetime.timestamp(datetime.datetime.now()))

                ret = None
                if self.MSGAGE >= abs(curret_date -  msg_date):
                    last_update_id = int(msg['update_id'])
                    ret = self.get_msgs(last_update_id)['result'][0]

                return ret

        else:
            return None


    def get_last_msg_text(self):
        """
        Return last message text, hadle the error
        Returns:
            [type]: empty str is empty list, othervise the last message
        """

        try:
            msg = self.get_last_msg()['message']['text']
        except:
            msg = ""

        return msg