#libraries
import json
import websocket
import pprint
import numpy
import talib
import tkinter as tk
from threading import *
from pandas import DataFrame
import matplotlib.pyplot as plt
import tkinter.font as font
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation
from matplotlib.figure import Figure


PERIOD = 14 #number of closing prices calculated in RSI
SYMBOL = 'ETHUSD'
QUANTITY: float = 1 #amount to buy per transaction
buy_counter = 0
sell_counter = 0
in_position: bool = False #entered ideal RSI range
on = False 
prices = [] # 1 minute closing prices
global rsi
unclosed_prices = []
num_prices = 0
window = tk.Tk()
myFont = font.Font(family="Stencil", size=11, weight="bold")
x = tk.StringVar()
global startButton
closeWS = False
tradelist = [] # all trades that have taken place
tradecounter = 0
tradelistIsOpen = False
tkRSI = tk.StringVar()
StartWallet = 0
profit = 0
wallet = 0 #amount of funds users has allot to bot 
tkProfit = tk.StringVar()
in_range = False


def start(): #when user hits start button to enter main screen
    global on
    on = True
    # destroying home page so main screen elements can be added
    startButton.destroy()
    L1.destroy()
    L2.destroy()
    E2.destroy()
    E1.destroy()
    E3.destroy()
    L3.destroy()
    popupmenu.destroy()
    # set up RSI conditions
    oversold = tkOverSold.get()
    overbought = tkOverBought.get()
    coinChoice = tkcoin.get()
    global wallet, StartWallet
    StartWallet = tkWallet.get()
    wallet = StartWallet
    if coinChoice == 'Ethereum':
        SOCKET = "wss://stream.binance.com:9443/ws/ethusdt@kline_1m"
    if coinChoice == 'Bitcoin':
        SOCKET = "wss://stream.binance.com:9443/ws/btcusdt@kline_1m"

    def tradehistory():
        global tradelistIsOpen
        if not tradelistIsOpen:
            tradelistIsOpen = True
            global Label1
            Label1 = tk.Label(window, text="Trade History", bg="black", fg="white", height=2, width=30, font=myFont)
            Label1.pack(fill=tk.BOTH, expand=1)
            global Labels
            Labels = []
            global i
            i = 0
            for trade in tradelist:
                history = tk.StringVar()
                history.set(trade)
                Labels.append(tk.Label(window, textvariable=history, bg="black", fg="white", height=2, width=30, font=myFont))
                Labels[i].pack(fill=tk.BOTH, expand=1)
                i+=1

    def cleartradehsitory():
        global tradelistIsOpen
        if tradelistIsOpen:
            Label1.destroy()
            tradelistIsOpen = False
            for label3 in Labels:
                label3.destroy()

    def stop():
        global closeWS
        closeWS = True

    def show_price():
        plt.plot(prices)
        plt.show()

    def show_rsi():
        plt.plot(rsi)
        plt.show()

    def connection(): #thread that runns continuous loop gathering prices from websocket
        ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message) #connect to websocket
        ws.run_forever()

    def on_open(ws):
        print('opened connection')

    def on_close(ws):
        print('closed connection')
        ws.close()

    def on_message(ws, message): #every time a new price is recieved
        if closeWS:
            on_close()
        print('got message')
        json_message = json.loads(message)
        # pprint.pprint(json_message)
        candle = json_message['k']
        candle_closed = candle['x']
        close = candle['c']
        global x
        x.set('Current Price: ${}'.format(close))
        global prices, wallet, sell_counter, buy_counter, in_position, QUANTITY, rsi, tradecounter, profit, StartWallet, in_range
        if not in_position: 
            profit = wallet - StartWallet
            print("profit calc")
            print(profit)
            print(StartWallet)
            print(wallet)
        if in_position:
            print("before")
            cost2: float = float(close)
            profit = wallet - StartWallet + cost2
            print("after")
        tkProfit.set('Profit: ${}'.format(profit))
        if candle_closed:
            print("candle closed at {}".format(close))
            prices.append(float(close))
            print("prices")
            print(prices)
            cost: float = float(close)
            print("current funds {}".format(wallet))
            print("Sell counter {}".format(sell_counter))
            print("buy counter {}".format(buy_counter))

            if len(prices) > PERIOD: #make sure there's enough data to calculate RSI
                np_closes = numpy.array(prices)
                rsi = talib.RSI(np_closes, PERIOD)
                print("all rsis calculated so far")
                print(rsi)
                last_rsi = rsi[-1]
                tkRSI.set('Current RSI: {}'.format(last_rsi))
                print("current rsi is {}".format(last_rsi))

                if last_rsi < oversold:
                    in_range = True
                    print('in range')
                if last_rsi > overbought:
                    if in_position: #meets sell conditions
                        print("SELLLL!!!")
                        wallet += cost * QUANTITY
                        tradelist.append('Sold for ${}'.format(cost))
                        tradecounter += 1
                        sell_counter += 1
                        in_position = False
                        print("current funds {}".format(wallet))

                    else:
                        print("don't own any")

                if in_range and last_rsi > (oversold - 1):
                    if in_position:
                        print("already own")
                    else: #meets buy conditions
                        print("BUYYYYYY!!!!")
                        print("test1")
                        print(close)
                        wallet -= cost * QUANTITY
                        tradelist.append('Bought for ${}'.format(cost))
                        tradecounter += 1
                        print("test2")
                        buy_counter += 1
                        in_position = True
                        in_range = False
                        print("current funds {}".format(wallet))

     #converting normal variables into TK variables that can be displayed and setting up buttons for main screen                   
    priceButton = tk.Button(window, text="Price Graph", command=show_price, bg="black", fg="white", height=2, width=30, font=myFont)
    priceButton.pack(fill=tk.BOTH, expand=1)
    rsiButton = tk.Button(window, text="RSI graph", command=show_rsi, bg="black", fg="white", height=2, width=30, font=myFont)
    rsiButton.pack(fill=tk.BOTH, expand=1)
    tradehistorybutton = tk.Button(window, text="trade history", command=tradehistory, bg="black", fg="white", height=2, width=30, font=myFont)
    tradehistorybutton.pack(fill=tk.BOTH, expand=1)
    cleartradehistorybutton = tk.Button(window, text="clear trade history", command=cleartradehsitory, bg="black", fg="white", height=2, width=30, font=myFont)
    cleartradehistorybutton.pack(fill=tk.BOTH, expand=1)
    stopButton = tk.Button(window, text="Stop", command=stop, bg="black", fg="white", height=2, width=30, font=myFont)
    stopButton.pack(fill=tk.BOTH, expand=1)
    label = tk.Label(textvariable=x, bg="black", fg="white", height=2, width=30, font=myFont)
    label.pack(fill=tk.BOTH, expand=1)
    rsiL = tk.Label(window, textvariable=tkRSI, bg="black", fg="white", height=2, width=30, font=myFont)
    rsiL.pack(fill=tk.BOTH, expand=1)
    ptofitL = tk.Label(window, textvariable=tkProfit, bg="black", fg="white", height=2, width=30, font=myFont)
    ptofitL.pack(fill=tk.BOTH, expand=1)
    t = Thread(target=connection)
    t.start()
    window.mainloop() #thread for continuous loop that operates GUI

#converting normal variables into TK variables that can be displayed and setting up buttons for start screen
if not on:
    print('not on')
    L1 = tk.Label(window, text="Oversold Value", bg="black", fg="white", height=2, width=30, font=myFont)
    L1.pack(fill=tk.BOTH, expand=1)
    tkOverSold = tk.IntVar()
    E1 = tk.Entry(window, textvariable=tkOverSold, bg="purple", fg="white", font=myFont, justify='center')
    E1.pack(fill=tk.BOTH, expand=1, ipady=6)
    L2 = tk.Label(window, text="Overbought Value", bg="black", fg="white", height=2, width=30, font=myFont)
    L2.pack(fill=tk.BOTH, expand=1)
    tkOverBought = tk.IntVar()
    E2 = tk.Entry(window, textvariable=tkOverBought, bg="purple", fg="white", font=myFont, justify='center')
    E2.pack(fill=tk.BOTH, expand=1, ipady=6)
    L3 = tk.Label(window, text="Wallet Amount", bg="black", fg="white", height=2, width=30, font=myFont)
    L3.pack(fill=tk.BOTH, expand=1)
    tkWallet = tk.IntVar()
    E3 = tk.Entry(window, textvariable=tkWallet, bg="purple", fg="white", font=myFont, justify='center')
    E3.pack(fill=tk.BOTH, expand=1, ipady=6)
    startButton = tk.Button(window, text="Start", command=start, bg="cyan", fg="purple4", height=2, width=30, font=myFont)
    tkcoin = tk.StringVar()
    choices = {'Ethereum', 'Bitcoin'}
    tkcoin.set("Ethereum")
    popupmenu = tk.OptionMenu(window, tkcoin, *choices)
    popupmenu.pack(ipady=6, fill=tk.BOTH, expand=1)
    startButton.pack(fill=tk.BOTH, expand=1)
    window.mainloop() #thread for continuous loop that operates GUI
