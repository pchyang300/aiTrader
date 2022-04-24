This was a personal project of mine that I created to automate trading stocks. It
utilizes the Alpaca Stock Trading API to buy and sell stocks as well as obtaining
historical data. This program runs by itself with no user input using the run window
or using a cmd prompt. This program should initially be run at the beginning of the 
weekend so that stock picks can be generated. The process starts by obtaining all the 
active stocks that you can trade on Alpaca. There's a little over 10,000 of them. Aftwards 
They are filtered based on volume, fraction trading, and exchange listing. Then program 
pulls historical price data for each stock with a max of 2 years in 30 minute increments 
using the API. This data is fitted into a numpy array and fed into the LSTM neural network. 
Once training is completed the next 30 minute price is recursively predicted for the next
5 days. A list of stocks is generated and written into stocks.txt. The top two stocks with 
The highest predicted gain percentage are the stock picks and are written into stock_picks.txt. 
Once the stock market opens, an asyncio task list will be created where each stock pick 
will be "trailed" for a good entry position using the strategy of trailing buy. The stock 
will be purchased and monitored daily for price movement. Once purchased it will be written
into the holdings.txt file. If the stock gains reach within 75% of 
the predicted amount, then a trailing sell will be executed. If the stock loses more than
5% then the stock will be sold. Once a stock is sold, the next stock in line from stocks.txt
will be placed into the asyncio task list. This program will loop forever generating stock 
picks during the weekends and execute stock trading for each individual stock the following 
weekdays. 

This program requires API keys that can be obtained from opening a free account with 
Alpaca.  

This was created with Python 3.8.
To use, install the dependencies from requirement.txt. 
Either enter API keys into the alpaca.py file or put them into a text file and provide
the path in alpaca.py. 
Finally run main.py.

Disclamer of Liability:
The material and information contained on this website is for general information purposes only. You should not rely upon the material or information on this website as a basis for making any business, investment, or any other decisions. 
