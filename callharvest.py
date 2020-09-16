import requests
from datetime import datetime, timedelta
import json

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36"
}

s = requests.Session()

s.headers = headers


def toBJtime(t):
    d = datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
    d1 = timedelta(hours=8) + d
    return int(datetime.timestamp(d1))


def getHarvestTime():
    usdt = "https://api.blockchair.com/ethereum/transactions?q=input_hex(%5E4641257d),recipient(0x1a6eC8EB73bf404112475895d6C8814ad5A7bd96)"
    dai = "https://api.blockchair.com/ethereum/transactions?q=input_hex(%5E4641257d),recipient(0xbDD4a57c5EE8558370bb661d29a979657D81258e)"

    usdtData = s.get(usdt).json()
    daiData = s.get(dai).json()
    ret = {}
    for i in usdtData["data"]:
        if not i["failed"]:
            ret["usdt"] = toBJtime(i["time"])
            break
    for i in daiData["data"]:
        if not i["failed"]:
            ret["dai"] = toBJtime(i["time"])
            break
    with open("callharvest.json", "w") as f:
        f.write(json.dumps(ret))
    print(ret)


if __name__ == "__main__":
    getHarvestTime()
