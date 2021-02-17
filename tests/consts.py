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

REV_MSG_NZ_UINT = "Shared: uint input is empty"
REV_MSG_NZ_ADDR = "Shared: address input is empty"
REV_MSG_NZ_BYTES = "Shared: bytes input is empty"
REV_MSG_NZ_UINT_ARR = "Shared: uint arr input is empty"


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
GAS_OVERHEAD_ETH = 10000
GAS_OVERHEAD_ASCOIN = 20000
INIT_BASE_BOUNTY = 10**15
INIT_REQUESTER_REWARD = 10**19
INIT_EXECUTOR_REWARD = 10**20
INIT_ETH_TO_ASCOIN_RATE = 18000 * E_18
NULL_REQ = (ADDR_0, ADDR_0, NULL_BYTES, False, 0, 0, ADDR_0)
INIT_ASC_REW_POOL = 10**25

REV_MSG_TARGET_REG = "Registry: nice try ;)"


# ASCoin
ASCOIN_ADDR = "0x31E31e3703D367014BA5802B7C5E41d96E331723"
REV_MSG_EXCEED_BAL = "ERC20: transfer amount exceeds balance"