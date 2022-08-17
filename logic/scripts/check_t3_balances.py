import requests
import os

etherscan_api_key = os.environ["ETHERSCAN_API_KEY"]
webhook_url = os.environ["WEBHOOK_URL"]
threshold = 500000 * 1e18

for (address, wallet) in [
    ("0xFE730B3cf80cA7B31905f70241F7C786BAF443E3", "Investor"),
    ("0x2EaE0CaE2323167ABF78462e0C0686865c67a655", "Team"),
]:
    result = requests.get(
        "https://api.etherscan.io/api?module=account&action=tokenbalance"
        "&contractaddress=0x8207c1ffc5b6804f6024322ccf34f29c3541ae26"
        "&address={}&tag=latest&apikey={}".format(address, etherscan_api_key)
    ).json()
    if int(result["result"]) < threshold:
        requests.post(
            webhook_url,
            data={
                "username": "T3 Wallet Balance",
                "content": "{} has a low balance of {} OGN".format(
                    wallet, int(int(result["result"]) / 1e18)
                ),
            },
        )
    else:
        print("{} T3 wallet balance is above threshold".format(wallet))
