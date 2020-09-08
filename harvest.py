import json

from web3 import Web3, HTTPProvider

w3url = "https://mainnet.infura.io/v3/998f64f3627548bbaf2630599c1eefca"

w3 = Web3(HTTPProvider(w3url))

DF = "0x431ad2ff6a9C365805eBaD47Ee021148d6f7DBe0"
WETH = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
CRV = "0xD533a949740bb3306d119CC777fa900bA034cd52"
YFII = "0xa1d0E215a23d7030842FC67cE582a6aFa3CCaB83"
DAI = "0x6B175474E89094C44Da98b954EedeAC495271d0F"
config = [
    {
        "token": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
        "Strategy": "0xe2df4c46acabb1cdb446351d6b24727944a5bfcc",
        "vault": "0x72Cf258c852Dc485a853370171d46B9D29fD3184",
        "name": "usdt",
        "StrategyName": "dforce",
        "pool": "0x324EebDAa45829c6A8eE903aFBc7B61AF48538df",
    },
    {
        "token": "0xdF5e0e81Dff6FAF3A7e52BA697820c5e32D806A8",
        "Strategy": "0x898828957133d4c50030a5A2D55Ca370915E6A77",
        "vault": "0x3E3db9cc5b540d2794DB3861BE5A4887cF77E48B",
        "name": "ycrv",
        "StrategyName": "crv",
        "pool": "0xFA712EE4788C042e2B7BB55E6cb8ec569C4530c1",
    },
    {
        "token": "0x6B175474E89094C44Da98b954EedeAC495271d0F",
        "Strategy": "0xbDD4a57c5EE8558370bb661d29a979657D81258e",
        "vault": "0x1e0DC67aEa5aA74718822590294230162B5f2064",
        "name": "dai",
        "StrategyName": "dforce",
        "pool": "0xD2fA07cD6Cd4A5A96aa86BacfA6E50bB3aaDBA8B",
    },
    {
        "token": "0x0000000000085d4780B73119b644AE5ecd22b376",
        "Strategy": "0x30aE128ebCdec11F62cB3fa9C6a0E8269a9AF686",
        "vault": "0x4243f5C8683089b65a9F588B1AE578d5D84bFBC9",
        "name": "tusd",
        "StrategyName": "crv",
    },
]

with open("abi/crvdeposit.json") as f:
    crvABI = json.loads(f.read())

with open("abi/uniswapRouterv2.json") as f:
    uniswapABI = json.loads(f.read())

with open("abi/df.json") as f:
    dfABI = json.loads(f.read())

uniswap_instance = w3.eth.contract(
    abi=uniswapABI,
    address=w3.toChecksumAddress("0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"),
)

df2yfii = [DF, WETH, YFII]
crv2yfii = [CRV, WETH, YFII]
yfii2dai = [YFII, WETH, DAI]


def getyfiiprice():
    price = uniswap_instance.functions.getAmountsOut(
        w3.toWei(1, "ether"), yfii2dai
    ).call()[-1]
    return float(w3.fromWei(price, "ether"))


yfiiprice = getyfiiprice()


def getcrv(pool, strategy):
    contract_instance = w3.eth.contract(abi=crvABI, address=w3.toChecksumAddress(pool))
    crv = contract_instance.functions.claimable_tokens(strategy).call()
    outyfii = uniswap_instance.functions.getAmountsOut(crv, crv2yfii).call()[-1]
    outyfii = float(w3.fromWei(outyfii, "ether"))
    usdprice = outyfii * yfiiprice
    # print(f"ycrv策略可以收割yfii:{outyfii/1e18},合约地址:{strategy}")
    return {
        "outyfii": outyfii,
        "name": "crv",
        "strategy": strategy,
        "usdprice": usdprice,
    }


def getdf(pool, strategy):
    contract_instance = w3.eth.contract(abi=dfABI, address=w3.toChecksumAddress(pool))
    df = contract_instance.functions.earned(strategy).call()
    outyfii = uniswap_instance.functions.getAmountsOut(df, df2yfii).call()[-1]
    outyfii = float(w3.fromWei(outyfii, "ether"))
    usdprice = outyfii * yfiiprice
    # print(f"df 策略可以收割yfii:{outyfii/1e18},合约地址:{strategy}")
    return {
        "outyfii": outyfii,
        "name": "df",
        "strategy": strategy,
        "usdprice": usdprice,
    }


def getharvest():
    ret = []
    for i in config:
        pool = i.get("pool", "")
        if pool:
            pool = w3.toChecksumAddress(i["pool"])
        strategy = w3.toChecksumAddress(i["Strategy"])
        if i["StrategyName"] == "dforce":
            ret.append(getdf(pool, strategy))
        elif i["StrategyName"] == "crv" and i["name"] == "ycrv":
            ret.append(getcrv(pool, strategy))
    print(ret)


if __name__ == "__main__":
    getharvest()
