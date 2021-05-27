from consts import *
from utils import *
from brownie import reverts, chain, web3
from brownie.test import strategy


settings = {"stateful_step_count": 20, "max_examples": 25}

def test_stakeManager(BaseStateMachine, state_machine, a, cleanAUTO, evmMaths):

    INIT_TOKEN_AMNT = 10**25
    
    class StateMachine(BaseStateMachine):

        # Set up the initial test conditions once
        def __init__(cls, a, cleanAUTO):
            super().__init__(cls, a, cleanAUTO)
            cls.allAddrs = a[:] + [cls.sm]
            for addr in a[1:]:
                print(addr)
                print(cls.AUTO.balanceOf(a[0]))
                cls.AUTO.transfer(addr, INIT_TOKEN_AMNT, {'from': a[0]})


        # Reset the local versions of state to compare the contract to after every run
        def setup(self):
            self.ethBals = {addr: INIT_ETH_BAL if addr in a else 0 for addr in self.allAddrs}
            self.autoBals = {addr: INIT_TOKEN_AMNT if addr in a else 0 for addr in self.allAddrs}
            self.totalStaked = 0
            self.stakerToStakedAmount = {addr: 0 for addr in self.allAddrs}
            self.stakes = []
            self.exec = (ADDR_0, 0)
            self.numTxsTested = 0


        # Variables that will be a random value with each fcn/rule called
        # st_recips = strategy("address[]", length=MAX_NUM_SENDERS, unique=True)

        def rule_test(self):
            pass


        # Check all the balances of every address are as they should be after every tx
        def invariant_bals(self):
            self.numTxsTested += 1
            for addr in self.allAddrs:
                assert addr.balance() == self.ethBals[addr]
                assert self.AUTO.balanceOf(addr) == self.autoBals[addr]
        

        # Check variable(s) after every tx that shouldn't change since there's
        # no intentional way to
        def invariant_nonchangeable(self):
            assert self.sm.getOracle() == self.o
            assert self.sm.getAUTO() == self.AUTO
            assert self.sm.STAN_STAKE() == STAN_STAKE
            assert self.sm.BLOCKS_IN_EPOCH() == BLOCKS_IN_EPOCH
        

        # Check all the state variables that can be changed after every tx
        def invariant_state_vars(self):
            assert self.sm.getTotalStaked() == self.totalStaked
            assert self.sm.getStakes() == self.stakes
            assert self.sm.getStakesLength() == len(self.stakes)
            assert self.sm.getStakesSlice(0, len(self.stakes)) == self.stakes
            curEpoch = getEpoch(web3.eth.block_number)
            assert self.sm.getCurEpoch() == curEpoch
            assert self.sm.getExecutor() == self.exec
            assert self.sm.getUpdatedExecRes() == getUpdatedExecResult(evmMaths, web3.eth.block_number, self.stakes)

            for addr in self.allAddrs:
                assert self.sm.getStake(addr) == self.stakerToStakedAmount[addr]
                assert self.sm.isCurExec(addr) == isCurExec(self.exec, addr, curEpoch, len(self.stakes))

        

        # Print how many rules were executed at the end of each run
        def teardown(self):
            print(f'Total rules executed = {self.numTxsTested-1}')

    
    state_machine(StateMachine, a, cleanAUTO, settings=settings)