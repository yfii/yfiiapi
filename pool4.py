from web3 import Web3, HTTPProvider
import json

w3url = "https://mainnet.infura.io/v3/998f64f3627548bbaf2630599c1eefca"

w3 = Web3(HTTPProvider(w3url))

WETH = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
YFII = "0xa1d0E215a23d7030842FC67cE582a6aFa3CCaB83"
DAI = "0x6B175474E89094C44Da98b954EedeAC495271d0F"
iUSDT = "0x72Cf258c852Dc485a853370171d46B9D29fD3184"
POOL4 = "0x3d367C9529f260B0661e1C1E91167C9319ee96cA"

yfii2dai = [YFII, WETH, DAI]

with open("abi/erc20.json") as f:
    erc20ABI = json.loads(f.read())

with open("abi/uniswapRouterv2.json") as f:
    uniswapABI = json.loads(f.read())

with open("abi/pool4.json") as f:
    pool4ABI = json.loads(f.read())

uniswap_instance = w3.eth.contract(
    abi=uniswapABI,
    address=w3.toChecksumAddress("0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"),
)
pool4_instance = w3.eth.contract(abi=pool4ABI, address=POOL4)


def getyfiiprice():
    price = uniswap_instance.functions.getAmountsOut(
        w3.toWei(1, "ether"), yfii2dai
    ).call()[-1]
    return float(w3.fromWei(price, "ether"))


def _weekly_reward():
    return pool4_instance.functions.rewardRate().call() / 1e18 * 60480


def _totalStakedAmount():
    token_instance = w3.eth.contract(abi=erc20ABI, address=w3.toChecksumAddress(YFII))
    return token_instance.functions.balanceOf(POOL4).call() / 1e18


def getDATA():
    weekly_reward = (
        pool4_instance.functions.rewardRate().call() / 1e6 * 7 * 24 * 60 * 60
    )

    token_instance = w3.eth.contract(abi=erc20ABI, address=w3.toChecksumAddress(YFII))
    totalStakedAmount = token_instance.functions.balanceOf(POOL4).call() / 1e18

    YFIIPrice = getyfiiprice()
    TVL = totalStakedAmount * YFIIPrice
    YFIWeeklyROI = (weekly_reward / TVL) * 100 / 1.01
    apy = YFIWeeklyROI * 52
    return {"apy": apy, "totalStakedAmount": totalStakedAmount, "TVL": TVL}


if __name__ == "__main__":
    print(getDATA())
