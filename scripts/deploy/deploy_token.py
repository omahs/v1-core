from ape_safe import ApeSafe
from brownie import accounts, OverlayV1Token, Contract, history, web3
import json
from scripts.overlay_management import OM
from scripts import utils


MINTER_ROLE = web3.solidityKeccak(['string'], ["MINTER"])


def get_verification_info():
    # Save verification info (for etherscan verification)
    verif_info = OverlayV1Token.get_verification_info()
    with open('scripts/deploy/OverlayV1Token_verif_info.json', 'w') as j:
        json.dump(verif_info, j, indent=4)


def deploy_w_eoa(eoa):
    ovl = eoa.deploy(OverlayV1Token)
    ovl.grantRole(MINTER_ROLE, eoa, {"from": eoa})
    return ovl


def deploy_w_safe(chain_id, safe):
    # Get contract bytecode
    data = OverlayV1Token.bytecode

    # Load create call contract
    create_call = utils.load_const_contract(chain_id, OM.CREATE_CALL)

    # Deploy feed factory and get address
    tx = create_call.performCreate(0, data, {'from': safe.address})
    ovl_address = tx.events['ContractCreation']['newContract']

    # Grant minter role to safe
    ovl = Contract.from_abi("OverlayV1Token", ovl_address, OverlayV1Token.abi)
    ovl.grantRole(MINTER_ROLE, safe.address, {"from": safe.address})

    # Get last two transactions; deploy and grant role
    hist = history.from_sender(safe.address)
    safe_tx = safe.multisend_from_receipts(hist[-2:])

    # Sign and post
    safe.sign_transaction(safe_tx)
    safe.post_transaction(safe_tx)

    return ovl_address


def main(chain_id):
    OM.connect_to_chain(chain_id)
    print('Getting all parameters')
    if chain_id == OM.ARB_TEST:
        eoa_name = input('Enter EOA name: ')
        eoa = accounts.load(eoa_name)
        ovl = deploy_w_eoa(eoa)
        ovl_addr = ovl.address
    else:
        safe = ApeSafe(OM.const_addresses[chain_id][OM.PROTOCOL_SAFE])
        ovl_addr = deploy_w_safe(chain_id, safe)
    print(f'Overlay token deployed at {ovl_addr}')
    get_verification_info()
