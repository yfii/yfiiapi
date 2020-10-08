import requests

# from web3 import Web3, HTTPProvider
import json

# w3url = "https://mainnet.infura.io/v3/998f64f3627548bbaf2630599c1eefca"

# w3 = Web3(HTTPProvider(w3url))

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36"
}


def getdforce():
    url1 = "https://api.dforce.network/api/getRoi/"

    z1 = requests.get(url1, headers=headers)

    url2 = "https://markets.dforce.network/api/v1/getApy/?net=main"
    z2 = requests.get(url2, headers=headers)

    apy = {}
    apy["usdt"] = z1.json()["dUSDT"] + float(z2.json()["dUSDT"]["now_apy"]) / 100
    apy["dai"] = z1.json()["dDAI"] + float(z2.json()["dDAI"]["now_apy"]) / 100
    return apy


def getcurve():
    url = "https://api.coinmarketcap.com/data-api/v1/farming/yield/latest"
    headers = {
        "referer": "https://coinmarketcap.com/yield-farming/",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36",
    }
    z1 = requests.get(url, headers=headers)
    data = z1.json()["data"]["farmingProjects"]
    for i in data:
        if i["name"] == "Curve":
            for p in i["poolList"]:
                if p["name"] == "Y":
                    stakeApy = p["yearlyROI"] / 100
    return stakeApy


def getfortube():
    url = "https://farm.for.tube/api/v2/bank_tokens"
    headers = {
        "referer": "https://for.tube/bank/home",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36",
    }
    z1 = requests.get(url, headers=headers)

    url1 = "https://api.for.tube/api/v1/bank/markets?mode=extended"
    z2 = requests.get(
        url1,
        headers={
            "referer": "https://for.tube/bank/home",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36",
            "Authorization": "SFMyNTY.g2gDbQAAACoweDAwMDAwMDAwNGZhOWU2MzVkYmU5MWM4M2FlZTM1N2QwMTQ5NDkzNmRuBgCfP3F7dAFiAAFRgA.8_HNNWK2A0pVVvH71_Ckv9q9NxRdIVxafnG5aLzvd-c",
        },
    )
    data = z1.json()
    data1 = z2.json()
    ret = {}
    getdata = ["usdc", "eth", "busd", "wbtc", "hbtc", "usdt"]
    for k, v in data.items():
        _apy = float(v["estimated_ar"])
        symbol = v["symbol"].lower()
        if symbol in getdata:
            ret[symbol] = _apy
    for v in data1["data"]:
        deposit_interest_rate = float(v["deposit_interest_rate"])
        symbol = v["token_symbol"].lower()
        if symbol in getdata:
            ret[symbol] += deposit_interest_rate
    for k, v in ret.items():
        ret[k] = f"{round(v*100, 2)}%"
    return ret


def getapy():
    apy = getdforce()
    ycrv = getcurve()
    apy["ycrv"] = ycrv
    apy["tusd"] = ycrv * 0.98
    for k, v in apy.items():
        apy[k] = f"{round(v*100, 2)}%"

    fortube_apy = getfortube()
    apy.update(fortube_apy)
    apy["weth"] = apy["eth"]
    print(apy)
    with open("apy.json", "w") as f:
        f.write(json.dumps(apy))


if __name__ == "__main__":
    getapy()
