import time
import requests
import json
import random
from web3 import Web3

w3 = Web3(Web3.HTTPProvider("https://zksync-era.blockpi.network/v1/rpc/public"))

abi = json.load(open('abi.json'))  # ABI
pepe_claim_address = w3.to_checksum_address(
    '0x95702a335e3349d197036Acb04BECA1b4997A91a')
claim_cotract = w3.eth.contract(address=pepe_claim_address, abi=abi)

headers = {
    'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
    'Accept': 'application/json, text/plain, */*',
    'Referer': 'https://www.zksyncpepe.com/airdrop',
    'sec-ch-ua-mobile': '?0',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'X-KL-saas-Ajax-Request': 'Ajax_Request',
    'sec-ch-ua-platform': '"Windows"',
}

with open("wallets_with_drop.txt", "r") as f:
    keys_list = [row.strip() for row in f if row.strip()]
    numbered_keys = list(enumerate(keys_list, start=1))
    random.shuffle(numbered_keys)

for wallet_number, private in numbered_keys:

    account = w3.eth.account.from_key(private)
    address = account.address

    amount_check = requests.get(
        f'https://www.zksyncpepe.com/resources/amounts/{address.lower()}.json',
        headers=headers,
    )

    try:
        if isinstance(json.loads(amount_check.text), list):
            pass

    except:
        print(f'{address}: You are not eligible')
        with open('not_eligible_wallets.txt', 'a') as output:
            print(f'{address}', file=output)
        continue


    proof_check = requests.get(
        f'https://www.zksyncpepe.com/resources/proofs/{address.lower()}.json',
        headers=headers,
    )

    amount = w3.to_wei(amount_check.json()[0], 'ether')
    proof = proof_check.json()

    tx = {
        "chainId": w3.eth.chain_id,
        "from": address,
        'maxFeePerGas': w3.eth.gas_price,
        'maxPriorityFeePerGas': w3.eth.gas_price,
        "nonce": w3.eth.get_transaction_count(address)
    }

    try:
        tx_claim = claim_cotract.functions.claim(proof, amount).build_transaction(tx)
        claim_txn = w3.eth.account.sign_transaction(tx_claim, private)
        claim_txn_hash = w3.eth.send_raw_transaction(claim_txn.rawTransaction)
        print(f"Claim TX: https://explorer.zksync.io/tx/{claim_txn_hash.hex()}")

        with open('ok_wallets.txt', 'a') as output:
            print(f'{address}', file=output)

        time.sleep(random.randint(100, 200))


    except Exception as err:

        with open('ne_ok_wallets.txt', 'a') as output:
            print(f'{address}', file=output)

        print(err)

    time.sleep(2)
