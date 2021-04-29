from brownie import a


# General/shared
ADDR_0 = "0x0000000000000000000000000000000000000000"
NULL_BYTES = "0x"
E_18 = int(1e18)
INIT_ETH_BAL = 100 * E_18


# Oracle
NORM_FACTOR = 115792089237316195423570985008687907853269984665640564039457
# Error factor since solidity and python give different answers for the same
# division calculation with very large numbers. Since the random number is used
# to choose from a relatively small list of stakers, this difference is negligible
# and won't impact the result of the executor
ERROR_FACTOR = 1.000000000000001
INIT_ASC_PER_USD = E_18
# ETH = $2000
INIT_ETH_PER_USD = 5 * 10**14
# 2 gwei
INIT_GAS_PRICE_FAST = 2 * 10**9

REV_MSG_NZ_UINT = "Shared: uint input is empty"
REV_MSG_NZ_ADDR = "Shared: address input is empty"
REV_MSG_NZ_BYTES = "Shared: bytes input is empty"
REV_MSG_NZ_BYTES32 = "Shared: bytes32 input is empty"
REV_MSG_NZ_UINT_ARR = "Shared: uint arr input is empty"


# Forwarder
REV_MSG_NOT_REG = "Forw: caller not the Registry"


# Miner
INIT_REQUESTER_REWARD = 10**20
INIT_EXECUTOR_REWARD = 10**21
INIT_REFERAL_REWARD = 10**20
MAX_UPDATE_BAL = 1000 * E_18
MIN_REWARD = E_18
MIN_FUND = 10000 * E_18

REV_MSG_NO_PEND_REW = "Miner: no pending rewards"
REV_MSG_CLAIM_TOO_LARGE = "Miner: claim too large"
REV_MSG_BAL_TOO_HIGH = "Miner: ASC bal too high"
REV_MSG_RATES_TOO_LOW = "Miner: new rates too low"
REV_MSG_FUND_TOO_LOW = "Miner: funding too low, peasant"


# Owner
REV_MSG_OWNER = "Ownable: caller is not the owner"


# StakeMan
BLOCKS_IN_EPOCH = 100
STAN_STAKE = 10000 * E_18
INIT_NUM_STAKES = 100
MAX_TEST_STAKE = INIT_NUM_STAKES * STAN_STAKE
NULL_EXEC = (ADDR_0, 0)

REV_MSG_NOT_ENOUGH_STAKE = "SM: not enough stake, peasant"
REV_MSG_NOFISH = "SM: something fishy here"
REV_MSG_NOT_STAKER = "SM: idx is not you"


# Registry
# EXEC_GAS_OVERHEAD_NO_REF = 40000
# EXEC_GAS_OVERHEAD_REF = 60000
GAS_OVERHEAD_ASCOIN = 70500
GAS_OVERHEAD_ETH = 47000
INIT_BASE_BOUNTY_USD = 5
INIT_ETH_BOUNTY_MULTIPLIER = 3
NULL_REQ = (ADDR_0, ADDR_0, NULL_BYTES, False, False, 0, 0, ADDR_0)
# NULL_REQ_BYTES = b'\x80\x03O%\xfc\xea\xbf-\x0e\xdfP5\xb2"\xe6\x93$\x9f\x1b\xd3\x0bq\xe2\xc8\xfb\x07\x8a\xad9\x83\xd4j'
# NULL_REQ_HEX = '0x' + NULL_REQ_BYTES.hex()
NULL_HASH = '0x0000000000000000000000000000000000000000000000000000000000000000'
INIT_ASC_REW_POOL = 10**25
INIT_GAS_PRICE_FAST = 10**9
CID_PREFIX_STR = '1220'
CID_PREFIX_BYTES = bytes.fromhex(CID_PREFIX_STR)

REV_MSG_TARGET = "Reg: nice try ;)"
REV_MSG_ALREADY_EXECUTED = "Reg: already executed"
REV_MSG_NOT_SAME = "Reg: request not the same"
REV_MSG_CANNOT_VERIFY = "Reg: cannot verify. Nice try ;)"
REV_MSG_NOT_EXEC = "Reg: not executor or expired"
REV_MSG_ETHFORCALL_NOT_MSGVALUE = "Reg: ethForCall not msg.value"
REV_MSG_ETHFORCALL_HIGH = "Reg: ethForCall too high"
REV_MSG_NOT_REQUESTER = "Reg: not the requester"
REV_MSG_CALLDATA_NOT_VER = "Reg: calldata not verified"
REV_MSG_FISHY = "Reg: something fishy here"
REV_MSG_REENTRANCY = "ReentrancyGuard: reentrant call"


# ASCoin
ASCOIN_ADDR = "0x31E31e3703D367014BA5802B7C5E41d96E331723"

REV_MSG_EXCEED_BAL = "ERC20: transfer amount exceeds balance"
REV_MSG_EXCEED_ALLOWANCE = "ERC20: transfer amount exceeds allowance"