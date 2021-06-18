"""
Crypto coin telegram Bot
Author: fvilmos
"""
from utils import cryptoinfo
from utils import telegramapiwrapper as taw
from utils import commandprocessor as cmdproc
from utils import safethread as st
import threading
import time
import argparse
import os


def worker5():
    """
    Periodic function, handle telegram send / receive functionality
    """
    val = ''

    # get last message, process it and alerts if is the case
    lmsg = bot.get_last_msg()
    val = cmdProcObj.cmd_processor(lmsg)
    
    if val is not None:  
        # echo 
        print (val)
        bot.send_msg(val,ID)

    # scheduler base time ~ 5s
    timer_ev5.wait(5)

def worker30():
    """
    Periodic function, handle telegram alerts
    Slower, since the CoinDesk refresh rate is about 30s
    """
    alerts = ''

    # process alerts
    alerts = cmdProcObj.alert_processor()

    if alerts is not None:
        for alert in alerts:
            # echo
            print (alert)
            bot.send_msg(alert,ID)

    # scheduler base time ~ 30s
    timer_ev30.wait(30)

# get script path
path, _ = os.path.split(os.path.realpath(__file__))

# telegram token, put yours
TOKEN = "<TOKEN>"

# telegram ID, put yours
ID = "<ID>"

# default coin list, extend if needed
coin_list='ETH,XRP,XLM,ADA,EOS,FIL,LRC,NMR,OMG,OXT,XTZ,ZRX,ADA'

# telegram bot
bot = taw.TelegramAPIWrapper(TOKEN=TOKEN)

# get coin info
ci_obj = cryptoinfo.CoinInfo(coin_list=coin_list)

# command processor
cmdProcObj = cmdproc.CommandProcessor(ci_obj)

# threads for periodic functions
timer_ev5 = threading.Event()
timer_th5 = st.SafeThread(target=worker5)

timer_ev30 = threading.Event()
timer_th30 = st.SafeThread(target=worker30)


# entry point
if __name__=="__main__":

    # input arguments
    parser = argparse.ArgumentParser(description='Telegram bot for crypto coin information. Checks and triggers notifications based on the setteled alerts.\n')
    parser.add_argument('-f', type=str, help='alert.json file location', default='/data/alert.json')
    parser.add_argument('-cl', type=str, help='coin list, simple string file with the crypto acronim, i.e. XRP', default='ETH,XRP,XLM,ADA,EOS,FIL,LRC,NMR,OMG,OXT,XTZ,ZRX,ADA')
    parser.add_argument('-t', type=str, help='TOKEN received from the Telegram bot creation process', default='<YOUR TOKEN>')
    parser.add_argument('-id', type=str, help='ID, received from the Telegram IDBot', default='<YOUR ID>')


    args = parser.parse_args()

    # set coin list
    ci_obj.set_coin_list(str(args.cl))

    # set alarm.json file location
    cmdProcObj.set_alert_file (path + str(args.f))

    # set token
    bot.set_token(str(args.t))

    # set ID
    ID = str(args.id)

    # start the perodic threads
    timer_th30.start()
    timer_th5.start()

    # keep running
    while True:
        time.sleep(1)
