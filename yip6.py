from web3 import Web3, HTTPProvider
import json

# w3url = "https://mainnet.infura.io/v3/998f64f3627548bbaf2630599c1eefca"
w3url = "https://eth-mainnet.alchemyapi.io/v2/4bdDVB5QAaorY2UE-GBUbM2yQB3QJqzv"

w3 = Web3(HTTPProvider(w3url))


with open("abi/erc20.json") as f:
    erc20ABI = json.loads(f.read())

YFII = w3.eth.contract(
    abi=erc20ABI,
    address=w3.toChecksumAddress("0xa1d0E215a23d7030842FC67cE582a6aFa3CCaB83"),
)

circularMiningPool = "0xB6af2DabCEBC7d30E440714A33E5BD45CEEd103a"

startBlock = 11067700  # https://etherscan.io/block/countdown/11067700

beforeBlock = int(startBlock - 24 * 60 * 60 / 13 * 7)  # 一周之前的区块高度，为了查一周之前 循环挖矿的余额

beforeAmount = YFII.functions.balanceOf(circularMiningPool).call(
    block_identifier=beforeBlock
)  # 之前累计的余额

# 本次要发送的金额 = (beforeAmount/4)+ 本周的 = (beforeAmount/4)+（当前余额-beforeAmount）
print(
    YFII.functions.balanceOf(circularMiningPool).call()
    - beforeAmount
    + beforeAmount / 4
)
