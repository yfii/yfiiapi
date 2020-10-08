from web3 import Web3, HTTPProvider
from web3.contract import BadFunctionCallOutput
from collections import defaultdict
import collections

# w3url = "https://mainnet.infura.io/v3/998f64f3627548bbaf2630599c1eefca"
w3url = "https://eth-mainnet.alchemyapi.io/v2/4bdDVB5QAaorY2UE-GBUbM2yQB3QJqzv"

w3 = Web3(HTTPProvider(w3url))
import json

with open("abi/vault.json") as f:
    vaultABI = json.loads(f.read())

with open("prices.json") as f:
    data = json.loads(f.read())

config = {
    "iDAI": "0x1e0DC67aEa5aA74718822590294230162B5f2064",
    "iUSDT": "0x72Cf258c852Dc485a853370171d46B9D29fD3184",
    "iYCRV": "0x3E3db9cc5b540d2794DB3861BE5A4887cF77E48B",
    "iTUSD": "0x4243f5C8683089b65a9F588B1AE578d5D84bFBC9",
    "iUSDC": "0x23B4dB3a435517fd5f2661a9c5a16f78311201c1",
    "iETH": "0xa8EA49a9e242fFfBdECc4583551c3BcB111456E6",
    "iBUSD": "0xc46d2fC00554f1f874F37e6e3E828A0AdFEFfbcB",
    "iHBTC": "0x26AEdD2205FF8a87AEF2eC9691d77Ce3f40CE6E9",
}


def updateData():
    block_number = w3.eth.blockNumber
    n = block_number
    for name, address in config.items():
        contract_instance = w3.eth.contract(
            abi=vaultABI, address=w3.toChecksumAddress(address)
        )

        lastrun = int(max(data[name].keys()))  # 上次运行最大的block_number
        print(f"name:{name}")
        print(f"lastrun:{lastrun}")
        while 1:
            a = contract_instance.functions.getPricePerFullShare().call(
                block_identifier=block_number
            )
            # print(block_number, a)
            block_number -= 50
            data[name][block_number] = a
            if block_number < lastrun:
                block_number = n
                break

    with open("prices.json", "w") as f:
        f.write(json.dumps(data))

    with open("prices.json") as f:
        data1 = json.loads(f.read())

    pricePerFullShare = {}
    for k, v in data1.items():
        # print(k,v)
        od = collections.OrderedDict(sorted(v.items(), reverse=False))
        pricePerFullShare[k] = [v for k, v in od.items()]

    with open("pricePerFullShare.json", "w") as f:
        f.write(json.dumps(pricePerFullShare))


if __name__ == "__main__":
    updateData()
