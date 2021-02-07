from brownie import a


# General/shared
ZERO_ADDR = "0x0000000000000000000000000000000000000000"


# Oracle
NORM_FACTOR = 115792089237316195423570985008687907853269984665640564039457
# Error factor since solidity and python give different answers for the same
# division calculation with very large numbers. Since the random number is used
# to choose from a relatively small list of stakers, this difference is negligible
# and won't impact the result of the executor
ERROR_FACTOR = 1.000000000000001

REV_MSG_NZ_UINT = "Shared: uint input is empty"
REV_MSG_NZ_ADDR = "Shared: address input is empty"
REV_MSG_NZ_BYTES32 = "Shared: bytes32 input is empty"


# StakeMan
BLOCKS_IN_EPOCH = 100
E_18 = int(1e18)
STAN_STAKE = 10000 * E_18
INIT_NUM_STAKES = 100
MAX_TEST_STAKE = INIT_NUM_STAKES * STAN_STAKE
NULL_EXEC = (ZERO_ADDR, 0)

REV_MSG_ = "StakeMan: too much, peasant"
REV_MSG_NOFISH = "StakeMan: something fishy here"


# ASCoin
REV_MSG_EXCEED_BAL = "ERC20: transfer amount exceeds balance"