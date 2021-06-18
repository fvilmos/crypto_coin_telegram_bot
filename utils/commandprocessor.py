import json 

class CommandProcessor():
    """Process temegram commands
    """
    def __init__(self,coinInfoObj=None,alert_file='./data/alert.json'):

        self.ci = coinInfoObj
        self.alert_file = alert_file

        self.command = {"/help": {"info": "List all availalle commands", "handler": self.help_handler},
                "/set-alert": {"info": "Set and alert for a specific crypto_coin, ex: /set-alert XRP price <= 1.6; supports <,>,=, and combinations, tag = [price/change24Hr]", "handler": self.set_alert_handler},
                "/clear-alert": {"info": "Clear alert for a specific crypto_coin, ex: /clear-alert 1, where 1 is the order from /list-alerts; or /clear-alert XRP, will clear all active alerts only for XRP", "handler": self.clear_alert_handler},
                "/list-coins": {"info": "List all available coins - Powered by CoinDesk , default: ETH,XRP,XLM,ADA,EOS,FIL,LRC,NMR,OMG,OXT,XTZ,ZRX,ADA", "handler": self.list_coins_handler},
                "/list-alerts": {"info": "List all available alerts [price, change24Hr], default: all", "handler": self.list_coin_alerts},
                }

        self.alert_list = []

        # update alert list
        self.load_alert_file()

    def set_alert_file(self,f='./data/alert.json'):
        """set alert.jason file location

        Args:
            f (str, optional): alert.json file location. Defaults to './data/alert.json'.
        """
        self.alert_file = f

        # reload content
        self.load_alert_file()

    def cmd_processor(self, cmd_dict={}):
        """Pharses the telegramm commands

        Args:
            cmd_dict (dict, optional): Dict received from telegram bot. Defaults to {}.

        Returns:
            str: command arguments
        """

        ret = None
        if cmd_dict is not None:
            try:
                msg_parts = cmd_dict['message']['text'].lower().split(' ')

                args = None

                if len(msg_parts)>1:
                    args = msg_parts[1::1]
                else:
                    args = None

                if msg_parts[0] in self.command:
                    handler = self.command.get(msg_parts[0]).get('handler')
                    ret = handler(args)
            except:
                pass
        return ret

    def load_alert_file(self):
        """

        Args:
            f (str, optional): [description]. Defaults to "alert.json".
        """
        # load alerts
        try:
            jfile = open(self.alert_file, "r")
            jcontent = jfile.read()
            self.alert_list = json.loads(jcontent)
        except:
            print ("json load issue!")

        
    def write_alert_file(self):
        """Write alerts.json file
        """
        # TODO: use append, don't write the full json
        
        # reset notification to occure again on restart
        for alert in self.alert_list:
            alert['alerted'] = str(0)

        jstr = json.dumps(self.alert_list)
        jsonFile = open(self.alert_file, "w")
        jsonFile.write(jstr)
        jsonFile.close()

    def help_handler(self, args):
        """List all available comands

        Args:
            args (str): comand argument list

        Returns:
            str: string of available commands
        """

        ret = ''
        for cmd in self.command:
            msg = cmd + " : " + str(self.command.get(cmd).get('info'))
            ret += msg + "\n"
        
        return ret

    def set_alert_handler(self, args):
        """Sets the alert 

        Args:
            args (str): set command arguments

        Returns:
            str: string to be sent by the bot
        """

        ret = ''

        if len(args) != 4:
            ret = "Please check the provided values, {} arguments received instead of 4!".format(len(args))
        else:
            #add alert
            self.alert_list.append({'coin': args[0].upper(), 'value': args[1], 'operation': args[2], 'target': args[3], 'alerted': 0})
            ret = 'Alert added for {}'.format(args[0].upper())

            # save content to file
            self.write_alert_file()

            #trigger list reload, since new value was added
            self.load_alert_file()

        return ret


    def clear_alert_handler(self, args):
        """Remove all or a specific element from the alert list

        Args:
            args (list of stringd): if argument is a coin i.e. XRP, will remove all the alerts for XRP, otherwhise just the specific order from the list

        Returns:
            str: string to be sent by the bot
        """
        ret = ''

        if len(args) == 1:
            
            # test if arg[0] is int
            coin_name = args[0].upper()
            
            try:
                if coin_name.isalpha():
                    for i,element in enumerate(self.alert_list):
                        if element['coin'] == coin_name:
                            # ennumerate starts with 1
                            self.alert_list.pop(i-1)
                else:
                    # elemet order received (int)
                    self.alert_list.pop(int(coin_name))
                
                self.write_alert_file()
                ret = 'All alerts for {} removed'.format(coin_name)
            except :
                 ret = 'Element not removed, check the command syntax!'

        return ret

    def list_coins_handler(self, args):
        """List all available coins

        Args:
            args (str): list command arguments

        Returns:
            str: string to be sent by the bot
        """
        ret = ''
        val = self.ci.get_coin_info()

        # construct telegram list
        for i,c in enumerate(val):
            name = c['name']
            currncy = c['currency']
            price = "{0:.3f}".format(c['price'])
            change24Hr_percent ="{:.3f}%".format(c['change24Hr_percent'])

            ret += str(i) + '. ' + name + ", price: " + price + " " + currncy + ", change24Hr: " + change24Hr_percent +"\n"

        return ret

    def list_coin_alerts(self,args):
        """List all tracked coin info

        Args:
            args (str): list command arguments

        Returns:
            str: string to be sent by the bot
        """
        ret =''
        for i,ch in enumerate(self.alert_list):
            # {'coin': args[0], 'value': args[1], 'operation': args[2], 'target': args[3]}
            ret += str(i) + ". " + ch['coin'] + " " + ch['value'] + " " + ch['operation'] + " " + ch['target'] + '\n'
        
        return ret
    
    def alert_processor (self):
        """Process all alerts saved in the alert json
        Returns:
            str: string to be sent by the bot
        """
        ret = []
        val = self.ci.get_coin_info()

        for coin in val:

            # get all alerts for a specific coin
            coin_name = coin['name']

            alerts = list(filter(lambda x: x['coin'] == str(coin_name).upper(), self.alert_list))

            # process alerts
            for alert in alerts:

                # test condition, alert if fulfilled, set alerted state, to do not occure in the future
                # handle tags=[price / change24Hr]

                alert_value = alert['value']
                alert_operation = alert['operation']
                alert_target = alert['target']
                coin_price = coin['price']
                alert_state = alert['alerted']
                coin_change24h_value = coin['change24Hr_value']

                # skipp is processed allready
                if alert_state == str(1): continue

                if alert_value == 'price':
                    alert_result = self.process_operation('price',alert_operation,coin_price, alert_target)

                elif alert_value == 'change24Hr':
                    alert_result = self.process_operation('change24Hr',alert_operation,coin_change24h_value, alert_target)

                else:
                    alert_value = 'Invalid alert value {}!'.format(alert_value)
                
                #TODO: write persitently the alerted state in json file
                if alert_result is not None:
                    alert['alerted'] = str(1)
                    ret.append(alert_result)

        return ret

    def process_operation(self,tag, op, value, target):
        """Process alert operation

        Args:
            tag (string): tag string [price,hange24Hr]
            op (string): operation, [<,<=>,>=,==]
            value (string float): coin value i.e. 1.6
            target (string float): alert target i.e. 1.2

        Returns:
            string: String to be posted telegram
        """

        ret = None
        if op == '<':
            ret = 'Alert: {} is {:.3f} less than your alert {:.3f} USD'.format(tag,float(value),float(target)) if float (value) < float(target) else None

        elif op == '<=':
            ret = 'Alert: {} is {:.3f} less or equal than your alert {:.3f} USD'.format(tag,float(value),float(target)) if float (value) <= float(target) else None

        elif op == '>':
            ret = 'Alert: {} is {:.3f} bigger than your alert {:.3f} USD'.format(tag,float(value),float(target)) if float (value) > float(target) else None

        elif op == '>=':
            ret = 'Alert: {} is {:.3f} bigger or equal than your alert {:.3f} USD'.format(tag,float(value),float(target)) if float (value) >= float(target) else None

        elif op == '==':
            ret = 'Alert: {} is {:.3f} equal with your alert {:.3f} USD'.format(tag,float(value),float(target)) if float (value) == float(target) else None

        else:
            ret = 'Invalid operation {}'.format(op)

        return ret