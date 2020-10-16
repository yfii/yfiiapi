from web3 import Web3, HTTPProvider
import json
import time

w3url = "https://eth-mainnet.alchemyapi.io/v2/4bdDVB5QAaorY2UE-GBUbM2yQB3QJqzv"

w3 = Web3(HTTPProvider(w3url))

WETH = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
YFII = "0xa1d0E215a23d7030842FC67cE582a6aFa3CCaB83"
DAI = "0x6B175474E89094C44Da98b954EedeAC495271d0F"
MEFI = "0x1a969239E12F07281f8876D11AfceE081D872adf"
iUSDT = "0x72Cf258c852Dc485a853370171d46B9D29fD3184"
UNI = "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984"

yfii2dai = [YFII, WETH, DAI]
mefi2dai = [MEFI, WETH, DAI]
uni2dai = [UNI, WETH, DAI]

with open("abi/erc20.json") as f:
    erc20ABI = json.loads(f.read())

with open("abi/uniswapRouterv2.json") as f:
    uniswapABI = json.loads(f.read())

with open("abi/pool4.json") as f:
    poolABI = json.loads(f.read())

with open("abi/vault.json") as f:
    vaultABI = json.loads(f.read())

with open("abi/uniswap_token.json") as f:
    uniswapTokenABI = json.loads(f.read())

with open("abi/bal_token.json") as f:
    balTokenABI = json.loads(f.read())

uniswap_instance = w3.eth.contract(
    abi=uniswapABI,
    address=w3.toChecksumAddress("0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"),
)


def getiTokenPrice(vault_address):
    vault_instance = w3.eth.contract(
        abi=vaultABI, address=w3.toChecksumAddress(vault_address)
    )
    price = vault_instance.functions.getPricePerFullShare().call() / 1e18
    return price


def getBalLPPrice(BalTokenAddress):
    baltoken_instance = w3.eth.contract(
        abi=balTokenABI, address=w3.toChecksumAddress(BalTokenAddress)
    )
    tokens = baltoken_instance.functions.getFinalTokens().call()

    token_tvl = 0
    for token in tokens:
        token_balance = baltoken_instance.functions.getBalance(token).call()
        token_decimals = (
            w3.eth.contract(abi=erc20ABI, address=w3.toChecksumAddress(token))
            .functions.decimals()
            .call()
        )
        if token.lower() == WETH.lower():
            tokentoDai = [WETH, DAI]
        else:
            tokentoDai = [token, WETH, DAI]
        _tokenPrice = getprice(tokentoDai, token_decimals)
        _tokentvl = token_balance / 10 ** token_decimals * _tokenPrice
        token_tvl += _tokentvl
    totalSupply = baltoken_instance.functions.totalSupply().call() / 1e18
    return token_tvl / totalSupply


def getUniswapLPPrice(uniTokenAddress):
    unitoken_instance = w3.eth.contract(
        abi=uniswapTokenABI, address=w3.toChecksumAddress(uniTokenAddress)
    )
    token0 = unitoken_instance.functions.token0().call()
    token0_instance = w3.eth.contract(
        abi=erc20ABI, address=w3.toChecksumAddress(token0)
    )
    token0_decimals = token0_instance.functions.decimals().call()

    token1 = unitoken_instance.functions.token1().call()
    token1_instance = w3.eth.contract(
        abi=erc20ABI, address=w3.toChecksumAddress(token1)
    )
    token1_decimals = token1_instance.functions.decimals().call()

    if token0.lower() == WETH.lower():
        token0toDai = [WETH, DAI]
    else:
        token0toDai = [token0, WETH, DAI]
    if token1.lower() == WETH.lower():
        token1toDai = [WETH, DAI]
    else:
        token1toDai = [token1, WETH, DAI]

    _reserve0, _reserve1, _ = unitoken_instance.functions.getReserves().call()
    _reserve0Price = getprice(token0toDai, token0_decimals)
    _reserve1Price = getprice(token1toDai, token1_decimals)

    _token0tvl = _reserve0 / 10 ** token0_decimals * _reserve0Price
    _token1tvl = _reserve1 / 10 ** token1_decimals * _reserve1Price

    totalSupply = unitoken_instance.functions.totalSupply().call() / 1e18

    return (_token0tvl + _token1tvl) / totalSupply


def getprice(token2dai, token_decimals):
    price = uniswap_instance.functions.getAmountsOut(
        10 ** token_decimals, token2dai
    ).call()[-1]
    return float(w3.fromWei(price, "ether"))


def getDATA():
    # apy 计算公式是
    # 每周产出代币数量*价格 / 池子里面的代币数量*价格 *52
    weekly_reward = (
        pool4_instance.functions.rewardRate().call() / 1e6 * 7 * 24 * 60 * 60
    )

    token_instance = w3.eth.contract(abi=erc20ABI, address=w3.toChecksumAddress(YFII))
    totalStakedAmount = token_instance.functions.balanceOf(POOL4).call() / 1e18

    YFIIPrice = getyfiiprice()
    TVL = totalStakedAmount * YFIIPrice
    # YFIWeeklyROI = (weekly_reward / TVL) * 100 / 1.01
    YFIWeeklyROI = (weekly_reward * 1.01 / TVL) * 100
    apy = YFIWeeklyROI * 52
    return {"apy": apy, "totalStakedAmount": totalStakedAmount, "TVL": TVL}


def get_data(pool, rewardTokenAddress, reward_price, lp_price, lp_token=False):
    pool_instance = w3.eth.contract(abi=poolABI, address=w3.toChecksumAddress(pool))
    if not lp_token:
        lp = pool_instance.functions.lp().call()  # 存的代币
    else:
        lp = lp_token
    lp_instance = w3.eth.contract(abi=erc20ABI, address=w3.toChecksumAddress(lp))
    lp_decimals = lp_instance.functions.decimals().call()

    reward_instance = w3.eth.contract(
        abi=erc20ABI, address=w3.toChecksumAddress(rewardTokenAddress)
    )
    reward_decimals = reward_instance.functions.decimals().call()

    stake_lp = lp_instance.functions.balanceOf(pool).call() / 10 ** lp_decimals
    tvl = stake_lp * lp_price

    weekly_reward = (
        pool_instance.functions.rewardRate().call()
        / 10 ** reward_decimals
        * 7
        * 24
        * 60
        * 60
    )
    print(weekly_reward, reward_price)
    if tvl != 0:
        WeeklyROI = (weekly_reward * reward_price / tvl) * 100
    else:
        WeeklyROI = 0
    periodFinish = pool_instance.functions.periodFinish().call()
    if periodFinish < int(time.time()):
        apy = "0.00%"
    else:
        apy = WeeklyROI * 52
        apy = f"{round(apy, 2)}%"
    return {"apy": apy, "staked": stake_lp, "tvl": tvl}


config = [
    {
        "name": "pool4",
        "pool": "0x3d367C9529f260B0661e1C1E91167C9319ee96cA",
        "rewardTokenAddress": "0x72Cf258c852Dc485a853370171d46B9D29fD3184",
        "reward_price": "getiTokenPrice('0x72Cf258c852Dc485a853370171d46B9D29fD3184')",
        "lp_price": "getprice(yfii2dai, 18)",
    },
    {
        "name": "pool5",
        "pool": "0xB6C7Bf515828c1eBf0D5F34930Cda0741eD9263F",
        "rewardTokenAddress": "0xa1d0e215a23d7030842fc67ce582a6afa3ccab83",
        "reward_price": "getprice(yfii2dai, 18)",
        "lp_price": "getprice(yfii2dai, 18)",
    },
    {
        "name": "yfii-mefi",
        "pool": "0x6A77c0c917Da188fBfa9C380f2E60dd223c0c35a",
        "rewardTokenAddress": "0x1a969239e12f07281f8876d11afcee081d872adf",
        "reward_price": "getprice(mefi2dai, 8)",
        "lp_price": "getprice(yfii2dai, 18)",
    },
    {
        "name": "mefiethlp-mefi",
        "pool": "0x6CA21695CB12A251bB19aE73Bda6964f1BBc48De",
        "rewardTokenAddress": "0x1a969239e12f07281f8876d11afcee081d872adf",
        "reward_price": "getprice(mefi2dai, 8)",
        "lp_price": "getUniswapLPPrice('0xc4b478e749dbcfddf96c6f84f4133e2f03c345a9')",
    },
    {
        "name": "bal-yfii",
        "pool": "0xAFfcD3D45cEF58B1DfA773463824c6F6bB0Dc13a",
        "rewardTokenAddress": "0xa1d0E215a23d7030842FC67cE582a6aFa3CCaB83",
        "reward_price": "getprice(yfii2dai, 18)",
        "lp_price": "getBalLPPrice('0x16cAC1403377978644e78769Daa49d8f6B6CF565')",
        "lp_token": "0x16cAC1403377978644e78769Daa49d8f6B6CF565",
    },
    {
        "name": "eth-usdt",
        "pool": "0x6C3e4cb2E96B01F4b866965A91ed4437839A121a",
        "rewardTokenAddress": "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984",
        "reward_price": "getprice(uni2dai, 18)",
        "lp_price": "getUniswapLPPrice('0x0d4a11d5EEaaC28EC3F61d100daF4d40471f1852')",
        "lp_token": "0x0d4a11d5EEaaC28EC3F61d100daF4d40471f1852",
    },
    {
        "name": "eth-usdc",
        "pool": "0x7FBa4B8Dc5E7616e59622806932DBea72537A56b",
        "rewardTokenAddress": "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984",
        "reward_price": "getprice(uni2dai, 18)",
        "lp_price": "getUniswapLPPrice('0xB4e16d0168e52d35CaCD2c6185b44281Ec28C9Dc')",
        "lp_token": "0xB4e16d0168e52d35CaCD2c6185b44281Ec28C9Dc",
    },
    {
        "name": "eth-dai",
        "pool": "0xa1484C3aa22a66C62b77E0AE78E15258bd0cB711",
        "rewardTokenAddress": "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984",
        "reward_price": "getprice(uni2dai, 18)",
        "lp_price": "getUniswapLPPrice('0xA478c2975Ab1Ea89e8196811F51A7B7Ade33eB11')",
        "lp_token": "0xA478c2975Ab1Ea89e8196811F51A7B7Ade33eB11",
    },
    {
        "name": "eth-wbtc",
        "pool": "0xCA35e32e7926b96A9988f61d510E038108d8068e",
        "rewardTokenAddress": "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984",
        "reward_price": "getprice(uni2dai, 18)",
        "lp_price": "getUniswapLPPrice('0xBb2b8038a1640196FbE3e38816F3e67Cba72D940')",
        "lp_token": "0xBb2b8038a1640196FbE3e38816F3e67Cba72D940",
    },
]


def getlpTVL():
    lp = [
        {
            "token": "0x0d4a11d5EEaaC28EC3F61d100daF4d40471f1852",
            "Strategy": "0x9466AAC3e97F1E716d97c8331ba346Bb243c13bD",
            "vault": "0x7E43210a4c6831D421f57026617Fdfc8ED3A0baf",
            "name": "eth/usdt",
            "StrategyName": "uni",
            "pool": "0x6C3e4cb2E96B01F4b866965A91ed4437839A121a",
        },
        {
            "token": "0xa478c2975ab1ea89e8196811f51a7b7ade33eb11",
            "Strategy": "0x41cCed5B81634EcFbd9eCA039aF5dfD05e713B2c",
            "vault": "0x19d994471D61d36FE367928Cc58102a376089D1f",
            "name": "eth/dai",
            "StrategyName": "uni",
            "pool": "0xa1484C3aa22a66C62b77E0AE78E15258bd0cB711",
        },
        {
            "token": "0xB4e16d0168e52d35CaCD2c6185b44281Ec28C9Dc",
            "Strategy": "0x1DE7D7AE631Dc4FFac3af9Cb4a9633820ba85Cd8",
            "vault": "0x68A23248000d5d4C943EE685989998c1B19bD74E",
            "name": "eth/usdc",
            "StrategyName": "uni",
            "pool": "0x7FBa4B8Dc5E7616e59622806932DBea72537A56b",
        },
        {
            "token": "0xBb2b8038a1640196FbE3e38816F3e67Cba72D940",
            "Strategy": "0xd24e08bdfefd68138F975035874F38554389A2E6",
            "vault": "0xb918368082655fA223c162266ecd88Aa7Ae40bc9",
            "name": "eth/wbtc",
            "StrategyName": "uni",
            "pool": "0xCA35e32e7926b96A9988f61d510E038108d8068e",
        },
    ]

    for i in lp:
        data = {}
        vault_address = i["vault"]
        vault_instance = w3.eth.contract(
            abi=vaultABI, address=w3.toChecksumAddress(vault_address)
        )
        pricePerFullShare = (
            vault_instance.functions.getPricePerFullShare().call() / 1e18
        )
        balance = vault_instance.functions.balance().call()

        # lp token price
        token = vault_instance.functions.token().call()
        lpprice = getUniswapLPPrice(token)

        tvl = balance * pricePerFullShare / 1e18 * lpprice
        data = {
            "name": i["name"],
            "tvl": tvl,
            "staked": balance * pricePerFullShare / 1e18,
        }
        print(data)


if __name__ == "__main__":
    # getlpTVL()
    for i in config:
        reward_price = eval(i["reward_price"])
        lp_price = eval(i["lp_price"])
        lp_token = i.get("lp_token", False)
        data = get_data(
            i["pool"], i["rewardTokenAddress"], reward_price, lp_price, lp_token
        )
        data["name"] = i["name"]
        print(data)
