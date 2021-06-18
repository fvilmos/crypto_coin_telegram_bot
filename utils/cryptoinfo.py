import requests


class CoinInfo():
    """
    Collect coin information using CoinDesk API (Powered by CoinDesk, https://www.coindesk.com/)
    Author: fvilmos
    """
    def __init__(self, url='https://production.api.coindesk.com/v1/currency/ticker?currencies=',coin_list=None):
        """
        Using an input list of coins retrives information from the CoinDesk server
        Args:
            url (str, optional): CoinDesc API. Defaults to 'https://production.api.coindesk.com/v1/currency/ticker?currencies='.
            coin_list ([type], optional): Use a simple comma separated list like "XRP,XLM". Defaults to None.
        """
        self.url = url
        self.coin_list = coin_list

        # coin source information
        print ("Powered by CoinDesk, https://www.coindesk.com/")

    def set_coin_list(self,coin_list):
        """Set a new value to the coinlist

        Args:
            coin_list (str): Default 
        """
        
    def get_coin_info(self,PRINT=False):
        """
        pharses the received information and returns a disct with the parsed data
        Args:
            PRINT (bool, optional): Used to list the received information in console. Defaults to False.

        Returns:
            dict: holds coin information parsed values, like price
        """
        
        ret = None
        ret = requests.get(self.url+self.coin_list).json()

        coin_info = []
        try:

            for c in ret['data']['currency']:
                c_name = c

                # get individual coin data

                c_info=ret['data']['currency'][c_name]
                c_currency = 'USD'
                c_price = c_info['quotes'][c_currency]['price']
                c_change24Hr_percent = c_info['quotes'][c_currency]['change24Hr']['percent']
                c_change24Hr_value = c_info['quotes'][c_currency]['change24Hr']['value']
                c_change24Hr_low = c_info['quotes'][c_currency]['low']
                c_change24Hr_high = c_info['quotes'][c_currency]['high']

                # print if required
                if PRINT is True:
                    print ("--------------")
                    print ("values:",c_name,c_currency,c_price,c_change24Hr_percent,c_change24Hr_value, c_change24Hr_low,c_change24Hr_high)
                    print ("--------------")

                # create dict with pharsed data
                coin_info.append({'name':c_name,'currency':c_currency,'price':c_price,'change24Hr_percent':c_change24Hr_percent,'change24Hr_value':c_change24Hr_value,'change24Hr_low':c_change24Hr_low,'change24Hr_high':c_change24Hr_high})

            return coin_info

        except:
                return None

