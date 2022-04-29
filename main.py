from alpaca import *
from swingTrade import *
from datetime import date
import datetime
import random
import pandas as pd
import asyncio


def get_length_of_holdings():
    f = open('holdings.txt', 'r')
    lines = f.read().splitlines()
    old_stock_purchases = {}
    for line in lines:
        values = line.split(',')
        old_stock_purchases[values[0]] = values[1]
    f.close()
    return len(old_stock_purchases)


def get_length_of_stock_picks():
    f = open('stock_picks.txt', 'r')
    lines = f.read().splitlines()
    current_stock_picks = {}
    for line in lines:
        values = line.split(',')
        current_stock_picks[values[0]] = values[1]
    f.close()
    return len(current_stock_picks)


while True:
    egg_basket = 2      # Determines how many different stocks to own at a time
    one_day = datetime.timedelta(days=1)
    if (not is_market_open_tomorrow() and time_to_market_close() > 86400) or \
            (not is_market_open_tomorrow() and get_length_of_holdings() == 0 and get_length_of_stock_picks() == 0):
        print("Tomorrow is the start of the weekend.")
        seconds = wait_until_num_hours_before_market_open(56)
        print("Stock pick will start 56 hours prior to next market open.")
        print(f"Waiting... {seconds} seconds")

        if seconds > 0:  # If seconds is negative, then skip waiting until 56 hour prior to open.
            try:
                time.sleep(seconds)
            except Exception as e:
                print(e)



        start_time = datetime.datetime.now()
        symbols = get_symbols_list(min_volume=10000000)     # Filter stocks based on minimum volume
        random.shuffle(symbols)
        if len(symbols) > 800:
            final_symbols_list = symbols[0:800]
        else:
            final_symbols_list = symbols

        print(final_symbols_list)
        list_size = len(final_symbols_list)
        print("Number of stocks queued: ", list_size)

        df = pd.DataFrame(columns=['Symbol', 'Change', 'Open', 'Close'])
        predictions_path_name = 'predictions/' + 'predictions_' + str(date.today()) + ".csv"
        df.to_csv(predictions_path_name, index=False, header=True)

        progress_cnt = 1

        for symbol in final_symbols_list:
            try:
                print(f'Training {progress_cnt} / {list_size}')
                predict_open, predict_close = predict_swing_gain(symbol)
                percent_change = ((predict_close - predict_open) / predict_open) * 100

                if str(percent_change) == 'nan':
                    continue
                data = {
                    'Symbol': [symbol],
                    'Change': [percent_change],
                    'Open': [predict_open],
                    'Close': [predict_close]
                }
                df = pd.DataFrame(data)
                df.to_csv(predictions_path_name, mode='a', index=False, header=False)
                progress_cnt += 1
            except Exception as e:
                print(e)
                print("Unable to get prediction")
                final_symbols_list.remove(symbol)
        f.close()
        print("Started at ", start_time)
        print("Finished predictions at ", datetime.datetime.now())

        df = pd.read_csv(predictions_path_name)
        df.sort_values(by=['Change'], inplace=True, ascending=False)
        stocks = []
        expected_change = []

        for i in range(len(df)):
            stocks.append(df['Symbol'].iloc[i])
            expected_change.append(df['Change'].iloc[i])

        open("stocks.txt", "w").close()
        open("stock_picks.txt", "w").close()
        f = open('stocks.txt', 'w')
        for stock, change in zip(stocks, expected_change):
            f.write(stock + ',' + str(change) + '\n')
        f.close()

        stock_picks = []
        # Move top two over to stock_picks.txt
        with open('stocks.txt', 'r') as fin:
            data = fin.read().splitlines(True)
            f = open('stock_picks.txt', 'a')
            for value in data[0:egg_basket]:
                values = value.split(',')
                stock_picks.append(values[0])
                f.write(values[0] + ',' + values[1])
            f.close()
        with open('stocks.txt', 'w') as fout:
            fout.writelines(data[egg_basket:])

        print('Stock picks for today ', stock_picks)

    f = open('holdings.txt', 'r')
    lines = f.read().splitlines()
    old_stock_purchases = {}
    for line in lines:
        values = line.split(',')
        if len(values[0]) != 0:
            old_stock_purchases[values[0]] = values[1]
    f.close()

    f = open('stock_picks.txt', 'r')
    lines = f.read().splitlines()
    current_stock_picks = {}
    for line in lines:
        values = line.split(',')
        if len(values[0]) != 0:
            current_stock_picks[values[0]] = values[1]
    f.close()

    wait_for_market_open()
    # Wait_for_market_open() could be off by a few seconds, so we are going to check every second if market is open.
    while not is_market_open():
        start = time.time()
        while time.time() - start < 1:
            pass

    # Holdings and stock picks must add up to egg_basket size. Otherwise liquidate all holdings. This to reset to begin
    # new week of trading.
    print('Length of stock holdings list: ', len(old_stock_purchases))
    print('Length of stock picks list: ', len(current_stock_picks))
    if len(old_stock_purchases) + len(current_stock_picks) > egg_basket:
        liquidate_all_positions()
        open('holdings.txt', 'w').close()
        open('dia.txt', 'w').close()
        old_stock_purchases = {}
        print("Waiting for account to update...")

        while time.time() - start < 600:    # Wait 10 minutes before trailing stocks to avoid volatility
            pass
        # Wait for positions to update to zero and buying power to update
        while len(api.list_positions()) != 0 or float(api.get_account().buying_power) < 5:
            start = time.time()
            while time.time() - start < 1:
                pass


    if len(current_stock_picks) == 0 and len(old_stock_purchases) == 0:
        new_stock_picks = {}
        for i in range(egg_basket):
            new_symbol, new_change = get_new_stock_pick()
            new_stock_picks[new_symbol] = new_change
            f.close()

        if is_market_open():
            asyncio.run(continue_buy_and_monitor(old_stock_purchases, new_stock_picks))
    else:
        if is_market_open():
            asyncio.run(continue_buy_and_monitor(old_stock_purchases, current_stock_picks))
