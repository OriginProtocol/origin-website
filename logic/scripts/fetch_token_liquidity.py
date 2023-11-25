from oneinch_py import OneInchSwap
import requests
import time
import json
from config import constants
import sys
from io import StringIO

# capture standard out to a string that we can pass to the webhook
s = StringIO()
sys.stdout = s

e18 = 1000000000000000000
e6 = 1000000

def emoji(slippage):
    if slippage < 1:
        return "✅"
    elif slippage < 3:
        return "😞"
    else:
        return "🚫"

# use lowercase addresses
coins = {
    '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48':{'name':'USDC'},
    '0x8207c1ffc5b6804f6024322ccf34f29c3541ae26':{'name':'OGN'},
    '0x9c354503c38481a7a7a51629142963f98ecc12d0':{'name':'OGV'},
    '0x2a8e1e676ec238d8a992307b495b45b3feaa5e86':{'name':'OUSD'},
    '0x856c4efb76c1d1ae02e20ceb03a2a6a08b0b8dc3':{'name':'OETH'}
}
coin_list = ','.join(coins.keys())

# fetch prices for each coin from CoinGecko
r = requests.get('https://api.coingecko.com/api/v3/simple/token_price/ethereum?contract_addresses='+coin_list+'&vs_currencies=usd')
response = r.json()
for address in response:
    coins[address]['price'] = response[address]['usd']

# free RPC endpoint
rpc_url = "https://rpc.coinsdo.net/eth"
# spoof Vitalik's wallet since the reeciving address doesn't matter
exchange = OneInchSwap(constants.ONEINCH_KEY, "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045") 

for address in coins:

    name = coins[address]['name']

    if name == "OETH" or name == "USDC":
        # 2 decimals
        price = '${:0,.2f}'.format(coins[address]['price'])
    else:
        # 5 decimals
        price = '${:0,.5f}'.format(coins[address]['price'])
    print("**"+name+"**" + " ("+price+")")

    if (name == "USDC"):
        print("\n")
        continue

    amounts = [10000,25000,50000,100000]
    for usd_amount in amounts:

        pretty_amount = '${:0,.0f}'.format(usd_amount)

        # buy token with USDC
        r = exchange.get_quote(from_token_symbol='USDC', to_token_symbol=address, amount=usd_amount)
        quote = int(r['toAmount'])/e18 
        expected = usd_amount/coins[address]['price']
        slippage = ((expected-quote)/expected)*100
        print(emoji(slippage) + " Buy " + pretty_amount + " with " + str(round(slippage,2)) +"% slippage")

        time.sleep(1) # 1inch rate limit
       
        # sell token for USDC (USDC uses 6 decimal places not 18)
        r = exchange.get_quote(from_token_symbol=address, to_token_symbol='USDC', amount=expected, decimals=6)
        quote = int(r['toAmount'])/e6
        slippage = ((usd_amount-quote)/usd_amount)*100
        print(emoji(slippage) + " Sell " + pretty_amount + " with " + str(round(slippage,2)) + "% slippage")
        
        time.sleep(1) # 1inch rate limit
    print("\n")

# fire webhook
hook = {'content':s.getvalue()}
requests.post(constants.DISCORD_LIQUIDITY_WEBHOOK, data=json.dumps(hook), headers={'Content-type':'application/json'})
