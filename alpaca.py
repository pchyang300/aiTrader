import alpaca_trade_api
import alpaca_trade_api as tradeapi
import time
from datetime import timedelta
from datetime import date
import datetime
from scipy.stats import linregress
import asyncio
from alpaca_trade_api.rest import TimeFrame, TimeFrameUnit
import warnings

warnings.filterwarnings('ignore', 'Discarding nonzero nanoseconds in conversion', )

path_api_key = "C:/Users/pchya/Desktop/keys/apikey.txt"
path_api_secret = "C:/Users/pchya/Desktop/keys/apisecret.txt"
path_paper_api_key = "C:/Users/pchya/Desktop/keys/paperapikey.txt"
path_paper_api_secret = "C:/Users/pchya/Desktop/keys/paperapisecret.txt"

f = open(path_api_key, 'r')
API_KEY = f.read()
f = open(path_api_secret, 'r')
API_SECRET = f.read()
f = open(path_paper_api_key, 'r')
PAPER_API_KEY = f.read()
f = open(path_paper_api_secret, 'r')
PAPER_API_SECRET = f.read()
f.close()

paper_base_url = 'https://paper-api.alpaca.markets'
live_url = "https://api.alpaca.markets"

# Switch between live or paper trading here:
#api = tradeapi.REST(API_KEY, API_SECRET, live_url, api_version='v2')
api = tradeapi.REST(PAPER_API_KEY, PAPER_API_SECRET, paper_base_url, api_version='v2')


async def buy_all(symbol, amount):
    cnt = 0
    while cnt < 5:
        try:
            print("Purchasing shares...")
            purchase_amount = amount
            # print("Buying power: " + str(buying_power) + "\n")
            while purchase_amount > 1.0000:
                three_fourths = .75 * purchase_amount
                quote = get_quote(symbol)
                fractional_shares = three_fourths / quote
                api.submit_order(
                    symbol=symbol,
                    qty=fractional_shares,
                    side='buy',
                    type='market',
                    time_in_force='day')
                print("Purchased " + str(fractional_shares) + " of " + symbol)
                time.sleep(5)
                purchase_amount = float(api.get_account().buying_power)
                cnt = 0
            break
        except ZeroDivisionError:
            print("Unable to obtain quote. Markets must be closed.")
            break
        except Exception as e:
            print(e)
            print("An error occurred. Trying again in 5 seconds...")
            await asyncio.sleep(5)
            cnt += 1
    if cnt == 5:
        print("A problem occurred at buy_all(). Please check program or manually purchase shares")


async def sell_all(symbol):
    print(f"Selling all shares of {symbol}")
    cnt = 0
    while cnt < 5:
        try:
            shares = api.get_position(symbol).qty
            api.submit_order(
                symbol=symbol,
                qty=shares,
                side='sell',
                type='market',
                time_in_force='day')
            # Remove symbol from holdings
            with open('holdings.txt', "r") as f:
                lines = f.readlines()
            # Looping through all, if symbol does not equal symbol, then write to file
            with open('holdings.txt', "w") as f:
                for line in lines:
                    values = line.split(",")
                    line.strip("\n")
                    if values[0] != symbol:
                        f.write(line)
            break
        except alpaca_trade_api.rest.APIError:
            await asyncio.sleep(1)
            print("Hmmm... looks like there are no shares to sell.")
            await asyncio.sleep(1)
            print("Continuing with program...")
            break
        except Exception as e:
            print(e)
            print("Something went wrong...")
            await asyncio.sleep(1)
            print("trying again in 10 seconds...")
            cnt += 1
            await asyncio.sleep(10)
    if cnt == 5:
        print("Unable to sell all. Please check program or manually sell your shares")


def check_market_open():
    while True:
        try:
            clock = api.get_clock()
            return clock
        except Exception as e:
            print(e)
            print("An exception occurred at check_market_open()")
            print("Trying again in 30 seconds...")
            time.sleep(30)


def time_to_market_close():
    while True:
        try:
            clock = api.get_clock()
            a = clock.next_close
            b = clock.timestamp
            return (a.to_pydatetime() - b.to_pydatetime()).total_seconds()
        except Exception as e:
            print(e)
            print("An error occurred at wait_for_market_close()")
            print("Trying again in 30 seconds...")
            time.sleep(30)


def wait_for_market_open():
    while True:
        try:
            clock = api.get_clock()
            if not clock.is_open:
                a = clock.next_open
                b = clock.timestamp
                time_to_open = (a.to_pydatetime() - b.to_pydatetime()).total_seconds()
                print("\nCurrent date and time: " + str(datetime.datetime.now()))
                print("Time until market open: " + str(time_to_open) + " seconds")
                print("Waiting...")
                time.sleep(round(time_to_open))
            break
        except Exception as e:
            print(e)
            print("An exception occurred at wait_for_market_open()")
            print("Trying again in 30 seconds...")
            time.sleep(30)


def time_before_market_close():
    while True:
        try:
            clock = api.get_clock()
            if is_market_open():
                a = clock.next_close
                b = clock.timestamp
                time_to_close = (a.to_pydatetime() - b.to_pydatetime()).total_seconds()
                return time_to_close
            else:
                break
        except Exception as e:
            print(e)
            print('An exception occurred at time_before_market_close()')
            print('Trying again in 30 seconds')
            time.sleep(30)


def wait_until_num_hours_before_market_open(hours_prior):
    while True:
        try:
            clock = api.get_clock()
            a = (clock.next_open - timedelta(hours=hours_prior))
            b = clock.timestamp
            time_before_open = (a.to_pydatetime() - b.to_pydatetime()).total_seconds()
            return round(time_before_open)
        except Exception as e:
            print(e)
            print("An exception occurred at wait_until_num_hours_before_market_open()")
            print("Trying again in 30 seconds...")
            time.sleep(30)


def wait_15_min_before_market_close():
    while True:
        try:
            clock = api.get_clock()
            if clock.is_open:
                a = clock.next_close - timedelta(minutes=15)
                b = clock.timestamp
                time_to_15_close = (a.to_pydatetime() - b.to_pydatetime()).total_seconds()
                print("\nCurrent date and time: " + str(datetime.datetime.now()))
                print("Waiting until 15 prior to close. Starts in: " + str(time_to_15_close) + " seconds")
                print("...")
                time.sleep(round(time_to_15_close))
            break
        except Exception as e:
            print(e)
            print("An exception occurred at wait_15_min_before_market_close()")
            print("Trying again in 30 seconds...")
            time.sleep(30)


def get_quote(symbol):
    while True:
        try:
            quote = api.get_latest_trade(symbol).p
            if quote > 0:
                return quote
            else:
                while quote <= 0:
                    time.sleep(1)
                    try:
                        quote = api.get_latest_trade(symbol).p
                    except Exception as e:
                        print(e)
                        quote = 0
                return quote

        except Exception as e:
            print(e)
            print("An exception occurred at get_quote()")
            print("Trying again in 1 seconds...")
            time.sleep(1)


def get_position(symbol):
    while True:
        try:
            quantity = api.get_position(symbol).qty
            return quantity
        except Exception as e:
            print(e)
            print("An exception occurred at get_position()")
            print("Trying again in 30 seconds...")
            time.sleep(30)


def get_buying_power():
    while True:
        try:
            return api.get_account().buying_power
        except Exception as e:
            print(e)
            print("An exception occurred at get_buying_power()")
            print("Trying again in 30 seconds...")
            time.sleep(30)


def is_market_open():
    while True:
        try:
            return api.get_clock().is_open
        except Exception as e:
            print(e)
            print("An exception occurred at is_market_open()")
            print("Trying again in 30 seconds...")
            time.sleep(30)


def is_fractionable(symbol):
    while True:
        try:
            return api.get_asset(symbol).fractionable
        except Exception as e:
            print("An exception occurred at is_fractionable()")
            print(e)
            print("Trying again in 90 seconds...")
            time.sleep(90)


def is_tradable(symbol):
    while True:
        try:
            return api.get_asset(symbol).tradable
        except Exception as e:
            print(e)
            print("An exception occurred at is_tradable()")
            print("Trying again in 90 seconds...")
            time.sleep(90)


def liquidate_all_positions():
    cnt = 0
    while cnt < 5:
        try:
            api.close_all_positions()
            break
        except Exception as e:
            print(e)
            print("Something went wrong...")
            time.sleep(1)
            print("trying again in 10 seconds...")
            cnt += 1
            time.sleep(10)

    if cnt == 5:
        print("Unable to sell all. Please check program or manually sell your shares")


async def monitor_stock_gain(symbol, change):
    try:
        if is_market_open():
            print(f"Monitoring price of {symbol}...")
            initial_price = get_entry_price(symbol)
            while initial_price is None:
                initial_price = get_entry_price(symbol)
            while is_market_open():
                lst = []
                for i in range(5):
                    lst.append(get_quote(symbol))
                    await asyncio.sleep(1)
                price = sum(lst) / len(lst)
                gain = ((price - initial_price) / initial_price) * 100
                print(f'Monitoring {symbol} ${price:.2f}        percent gain: {gain:.2f}%')
                if gain > 0.75 * float(change):
                    await trailing_sell(symbol)
                    break
                if gain < -5:
                    await sell_all(symbol)
                    break

                # Sell all positions by end of week.
                if not is_market_open_tomorrow() and time_before_market_close() < 300:
                    sell_all(symbol)
                    await asyncio.sleep(600)

    except Exception as e:
        print(e)


def get_entry_price(symbol):
    cnt = 0
    while cnt < 5:
        try:
            if is_market_open():
                return float(api.get_position(symbol).avg_entry_price)
            else:
                break
        except Exception as e:
            print("Something went wrong...")
            print(e)
            time.sleep(1)
            print("trying again in 10 seconds...")
            cnt += 1
            time.sleep(10)
    if cnt == 5:
        print("Problem occurred at get_entry_price")


async def trailing_sell(symbol):
    cnt = 0
    while cnt < 5:
        try:
            max_price = get_quote(symbol)
            percent_change = 0
            pullback_percentage = -1.6  # Experiment with this number
            sold = False
            initial_price = get_entry_price(symbol)
            while initial_price is None:
                initial_price = get_entry_price(symbol)

            while percent_change > pullback_percentage and is_market_open():
                lst = []

                for i in range(5):
                    lst.append(get_quote(symbol))
                    await asyncio.sleep(1)
                average_price = sum(lst) / len(lst)
                next_price = average_price
                if next_price > max_price:
                    max_price = next_price
                    print(f"---->NEW {symbol} MAX PRICE: ${max_price:.2f}")
                percent_change = ((next_price - max_price) / max_price) * 100
                gain = ((next_price - initial_price) / initial_price) * 100
                print(
                    f'{symbol} current price: ${next_price:.2f}   gain: {gain:.2f}%       pullback: {percent_change:.2f}%')

            if is_market_open():
                await sell_all(symbol)

                # Remove symbol from holdings
                with open('holdings.txt', "r") as f:
                    lines = f.readlines()
                # If symbol does not equal symbol, then write to file
                with open('holdings.txt', "w") as f:
                    for line in lines:
                        values = line.split(",")
                        line.strip("\n")
                        if values[0] != symbol:
                            f.write(line)
                break
        except Exception as e:
            print(e)
            cnt += 1
    if cnt == 5:
        print('Error occurred at trailing_sell. Unable to execute selling')


async def trailing_buy(symbol, amount, change):
    cnt = 0
    while cnt < 5:
        try:
            min_price = get_quote(symbol)
            percent_change = 0
            pullback_percentage = 1.6  # Experiment with this number
            bought = False

            while percent_change < pullback_percentage and is_market_open():
                lst = []
                for i in range(5):
                    lst.append(get_quote(symbol))
                    await asyncio.sleep(1)
                average_price = sum(lst) / len(lst)
                next_price = average_price
                if next_price < min_price:
                    min_price = next_price
                    print(f"---->NEW {symbol} MINIMUM PRICE: ${min_price:.2f}")
                percent_change = ((next_price - min_price) / min_price) * 100
                print(f'Trailing {symbol}... current price: ${next_price:.2f}       pullback: {percent_change:.2f}%')

            if is_market_open():
                cnt = 0
                while cnt < 5:
                    try:
                        if 0.8 * amount < float(get_buying_power()) < 1.2 * amount:
                            await buy_all(symbol, amount)

                            with open('stock_picks.txt', "r") as f:
                                lines = f.readlines()
                            # Removes symbol from stock_picks.txt list
                            # If symbol does not equal symbol, then write to file
                            with open('stock_picks.txt', "w") as f:
                                for line in lines:
                                    values = line.split(",")
                                    line.strip("\n")
                                    if values[0] != symbol:
                                        f.write(line)

                            break
                        else:
                            fractional_shares = amount / get_quote(symbol)
                            api.submit_order(
                                symbol=symbol,
                                qty=fractional_shares,
                                side='buy',
                                type='market',
                                time_in_force='day')
                            print("Purchased " + str(fractional_shares) + " of " + symbol)

                            # Remove symbol from stock picks
                            with open("stock_picks.txt", "r") as f:
                                lines = f.readlines()
                            # If file symbol does not equal symbol, then write line to file
                            with open("stock_picks.txt", "w") as f:
                                for line in lines:
                                    values = line.split(",")
                                    line.strip("\n")
                                    if values[0] != symbol:
                                        f.write(line)

                            time.sleep(5)
                            break
                    except Exception as e:
                        print(e)
                    cnt += 1
                f = open('holdings.txt', 'a')
                f.write(symbol.strip('\n') + ',' + str(change.strip('\n')) + ',' + str(date.today()) + "\n")
                f.close()
                bought = True
            return bought
        except Exception as e:
            print(e)
            cnt += 1
    if cnt == 5:
        print("Error occurred at trailing_buy. Unable to execute buying")


def get_slope(symbol, seconds):
    cnt = 0
    while cnt < 5:
        try:
            cnt = 0
            interval = []
            price_data = []

            while cnt < seconds:
                interval.append(cnt)
                price_data.append(get_quote(symbol))
                cnt += 1
                time.sleep(1)
            return linregress(interval, price_data).slope
        except Exception as e:
            print(e)
            cnt += 1

    if cnt == 5:
        print("Error occurred at get_slope(). Unable to get_slope()")
        return 0


def get_symbols_list(min_volume=None, max_volume=None):
    symbols_list = []
    asset_list = api.list_assets(status='active')
    cnt = 0
    for asset in asset_list:
        symbol = asset.symbol
        tradable = asset.tradable
        fractionable = asset.fractionable
        exchange = asset.exchange
        days = 1
        if tradable and fractionable and (exchange == 'NASDAQ' or exchange == "NYSE"):
            while True:
                try:
                    delta = datetime.timedelta(days=days)
                    start_date = date.today() - delta
                    while len(api.get_bars(symbol, timeframe=TimeFrame.Day, start=start_date.strftime('%Y-%m-%d'), limit=1)) == 0:
                        days += 1
                        delta = datetime.timedelta(days=days)
                        start_date = date.today() - delta
                    volume = api.get_bars(symbol, timeframe=TimeFrame.Day, start=start_date.strftime('%Y-%m-%d'), limit=1)[0].v
                    break
                except Exception as e:
                    print(e)

            if min_volume is None and max_volume is not None:
                if volume < max_volume:
                    symbols_list.append(symbol)
            if min_volume is not None and max_volume is None:
                if min_volume < volume:
                    symbols_list.append(symbol)
            if min_volume is not None and max_volume is not None:
                if min_volume < volume < max_volume:
                    symbols_list.append(symbol)
            if min_volume is None and max_volume is None:
                symbols_list.append(symbol)

        cnt += 1
        print(cnt)

    return symbols_list


def did_stock_breakout(symbol):
    today = datetime.date.today()
    last_monday = today - datetime.timedelta(days=today.weekday())
    bars = api.get_bars(symbol, start=last_monday.strftime('%Y-%m-%d'), end=today.strftime('%Y-%m-%d'),
                        timeframe=TimeFrame(30, TimeFrameUnit.Minute))
    n = len(bars) - 1
    change = ((bars[n].o - bars[0].o) / bars[0].o) * 100
    if change <= 5:
        return False
    else:
        return True


def get_new_stock_pick():
    with open('stocks.txt', "r") as f:
        lines = f.readlines()

    for line in lines:
        values = line.split(',')
        symbol = values[0]
        change = values[1].strip('\n')
        if not did_stock_breakout(symbol) and float(change) > 5:
            # If symbol does not equal symbol, then write to file
            with open('stock_picks.txt', 'a') as f:
                f.write(line)
            f = open('stocks.txt', "r")
            x_lines = f.readlines()
            f.close()
            f = open('stocks.txt', 'w')
            for x_line in x_lines:
                x_values = x_line.split(",")
                x_line.strip("\n")
                if x_values[0] != symbol:
                    f.write(x_line)
            f.close()
            return symbol, float(change)
        else:
            # Otherwise remove from stocks.txt file.
            f = open('stocks.txt', "r")
            x_lines = f.readlines()
            f.close()
            f = open('stocks.txt', 'w')
            for x_line in x_lines:
                x_values = x_line.split(",")
                x_line.strip("\n")
                if x_values[0] != symbol:
                    f.write(x_line)
            f.close()
    print("No stock picks generated. All stocks have already gained more than 5%")


async def buy_and_monitor(symbol, purchase_amount, change):
    await trailing_buy(symbol, purchase_amount, change)
    await monitor_stock_gain(symbol, change)
    if is_market_open():
        new_symbol, new_change = get_new_stock_pick()
        new_purchase_amount = float(get_buying_power())
        await buy_and_monitor(new_symbol, new_purchase_amount, new_change)


async def monitor(symbol, change):
    await monitor_stock_gain(symbol, change)
    if is_market_open():
        new_symbol, new_change = get_new_stock_pick()
        new_purchase_amount = float(get_buying_power())
        await buy_and_monitor(new_symbol, new_purchase_amount, new_change)


async def asyncio_tasks(stock_picks, amount, expected_change):
    task_list = []
    for stock, change in zip(stock_picks, expected_change):
        task_list.append(asyncio.create_task(buy_and_monitor(stock, amount, change)))
    await asyncio.gather(*task_list)


async def continue_buy_and_monitor(old_stock_purchases, current_stock_picks):
    task_list = []

    # Dictionaries are passed into this function
    if len(old_stock_purchases) > 0:
        for stock in old_stock_purchases:
            change = old_stock_purchases[stock]
            task_list.append(asyncio.create_task(monitor(stock, change)))
    if len(current_stock_picks) > 0:
        purchase_amount = float(get_buying_power()) / len(current_stock_picks)
        for stock in current_stock_picks:
            change = current_stock_picks[stock]
            task_list.append(asyncio.create_task(buy_and_monitor(stock, purchase_amount, change)))
    await asyncio.gather(*task_list)


def is_market_open_tomorrow():
    try:
        delta = datetime.timedelta(days=1)
        if str(date.today() + delta) == \
                str(api.get_calendar(date.today() + delta, date.today() + delta)[0].date).split(' ')[0]:
            return True
        else:
            return False
    except Exception as e:
        print(e)
        print('Problem occurred at is_market_open_tomorrow')
