from consts import *
from utils import *
from brownie import reverts, chain, web3
from brownie.test import strategy


settings = {"stateful_step_count": 250, "max_examples": 300}

def test_stakeManager(BaseStateMachine, state_machine, a, cleanAUTO, evmMaths):

    INIT_TOKEN_AMNT = 10**25
    # Web3 times out past 50
    MAX_NUM_TO_STAKE = 50
    # Run into block gas limit and read timeouts past 500
    MAX_STAKE_LEN = 500
    NUM_SENDERS = 5
    
    class StateMachine(BaseStateMachine):

        # Set up the initial test conditions once
        def __init__(cls, a, cleanAUTO):
            super().__init__(cls, a, cleanAUTO)
            
            cls.allAddrs = a[:NUM_SENDERS] + [cls.sm]

            # Distribute tokens evenly to NUM_SENDERS and call approve from each of them
            for addr in a[:NUM_SENDERS]:
                cls.AUTO.transfer(addr, INIT_TOKEN_AMNT, {'from': a[0]})
                cls.AUTO.approve(cls.sm, BIG_NUM, {'from': addr})
            
            deployerBal = cls.AUTO.balanceOf(a[0])
            if deployerBal > INIT_TOKEN_AMNT:
                cls.AUTO.transfer('0x0000000000000000000000000000000000000001', deployerBal - INIT_TOKEN_AMNT, {'from': a[0]})
            
            # chain.sleep(BLOCKS_IN_EPOCH)


        # Reset the local versions of state to compare the contract to after every run
        def setup(self):
            self.ethBals = {addr: INIT_ETH_BAL if addr in a else 0 for addr in self.allAddrs}
            self.ethBals[a[0]] -= ERC1820_ETH_AMOUNT
            self.autoBals = {addr: INIT_TOKEN_AMNT if addr in a else 0 for addr in self.allAddrs}
            self.totalStaked = 0
            self.stakerToStakedAmount = {addr: 0 for addr in self.allAddrs}
            self.stakes = []
            self.exec = NULL_EXEC
            self.numTxsTested = 0


        st_numStakes = strategy("uint", max_value=MAX_NUM_TO_STAKE)
        st_sender = strategy("address", length=NUM_SENDERS)
        st_sender2 = strategy("address", length=NUM_SENDERS)
        st_idxs = strategy("uint[]", max_length=MAX_NUM_TO_STAKE)
        st_numIdxs = strategy("uint", max_value=MAX_NUM_TO_STAKE)
        st_mine_num = strategy("uint", min_value=1, max_value=BLOCKS_IN_EPOCH)


        # Using this to make 3 rules of stake to balance out the 3 rules of unstake
        # so that most of it isn't unstaking
        def _stake(self, st_numStakes, st_sender):
            amount = st_numStakes * STAN_STAKE
            if len(self.stakes) + st_numStakes > MAX_STAKE_LEN:
                print('        PAST MAX_STAKE_LEN rule_stake', bn()+1, len(self.stakes), st_numStakes, st_sender)
            elif st_numStakes == 0:
                print('        REV_MSG_NZ_UINT rule_stake', bn()+1, len(self.stakes), st_numStakes, st_sender)
                with reverts(REV_MSG_NZ_UINT):
                    self.sm.stake(st_numStakes, {'from': st_sender})
            elif self.autoBals[st_sender] < amount:
                print('        REV_MSG_EXCEED_BAL rule_stake', bn()+1, len(self.stakes), st_numStakes, st_sender)
                with reverts(REV_MSG_EXCEED_BAL):
                    self.sm.stake(st_numStakes, {'from': st_sender})
            else:
                print('                    rule_stake', bn()+1, len(self.stakes), st_numStakes, st_sender)
                self.sm.stake(st_numStakes, {'from': st_sender})

                self.autoBals[self.sm] += amount
                self.autoBals[st_sender] -= amount
                self.totalStaked += amount
                self.stakerToStakedAmount[st_sender] += amount
                if self.exec[1] != getEpoch(bn()):
                    # Use self.stakes that hasn't been updated yet because the exec
                    # is updated before modifications to stakes
                    self.exec = getExecutor(evmMaths, bn(), self.stakes, self.exec)
                self.stakes.extend([st_sender] * st_numStakes)


        def rule_stake1(self, st_numStakes, st_sender):
            self._stake(st_numStakes, st_sender)


        def rule_stake2(self, st_numStakes, st_sender):
            self._stake(st_numStakes, st_sender)


        def rule_stake3(self, st_numStakes, st_sender):
            self._stake(st_numStakes, st_sender)


        def rule_unstake_random_idxs(self, st_idxs, st_sender):
            amount = len(st_idxs) * STAN_STAKE
            isOutBounds, isNotStaker, newStakes = unstakeErrors(self.stakes, st_idxs, st_sender)

            if amount == 0:
                print('        REV_MSG_NZ_UINT_ARR rule_unstake_random_idxs', bn()+1, len(self.stakes),  st_idxs, st_sender)
                with reverts(REV_MSG_NZ_UINT_ARR):
                    self.sm.unstake(st_idxs, {'from': st_sender})
            elif self.stakerToStakedAmount[st_sender] < amount:
                print('        REV_MSG_NOT_ENOUGH_STAKE rule_unstake_random_idxs', bn()+1, len(self.stakes),  st_idxs, st_sender)
                with reverts(REV_MSG_NOT_ENOUGH_STAKE):
                    self.sm.unstake(st_idxs, {'from': st_sender})
            elif isOutBounds:
                print('        REV_MSG_OUT_OF_RANGE rule_unstake_random_idxs', bn()+1, len(self.stakes),  st_idxs, st_sender)
                with reverts(REV_MSG_OUT_OF_RANGE):
                    self.sm.unstake(st_idxs, {'from': st_sender})
            elif isNotStaker:
                print('        REV_MSG_NOT_STAKER rule_unstake_random_idxs', bn()+1, len(self.stakes),  st_idxs, st_sender)
                with reverts(REV_MSG_NOT_STAKER):
                    self.sm.unstake(st_idxs, {'from': st_sender})
            else:
                print('                    rule_unstake_random_idxs', bn()+1, len(self.stakes), st_idxs, st_sender)
                self.sm.unstake(st_idxs, {'from': st_sender})

                self.autoBals[st_sender] += amount
                self.autoBals[self.sm] -= amount
                self.totalStaked -= amount
                self.stakerToStakedAmount[st_sender] -= amount
                if self.exec[1] != getEpoch(bn()):
                    # Use self.stakes that hasn't been updated yet because the exec
                    # is updated before modifications to stakes
                    self.exec = getExecutor(evmMaths, bn(), self.stakes, self.exec)
                self.stakes = newStakes


        def rule_unstake_working_idxs(self, st_numIdxs, st_sender):
            amount = st_numIdxs * STAN_STAKE
            if self.stakes.count(st_sender) >= st_numIdxs:
                idxs, newStakes = getFirstIndexes(self.stakes, st_sender, st_numIdxs)

                if amount == 0:
                    print('        REV_MSG_NZ_UINT_ARR rule_unstake_working_idxs', bn()+1, len(self.stakes),  st_numIdxs, st_sender)
                    with reverts(REV_MSG_NZ_UINT_ARR):
                        self.sm.unstake(idxs, {'from': st_sender})
                elif self.stakerToStakedAmount[st_sender] < amount:
                    print('        REV_MSG_NOT_ENOUGH_STAKE rule_unstake_working_idxs', bn()+1, len(self.stakes),  st_numIdxs, st_sender)
                    with reverts(REV_MSG_NOT_ENOUGH_STAKE):
                        self.sm.unstake(idxs, {'from': st_sender})
                else:
                    print('                    rule_unstake_working_idxs', bn()+1, len(self.stakes), st_numIdxs, st_sender)
                    self.sm.unstake(idxs, {'from': st_sender})

                    self.autoBals[st_sender] += amount
                    self.autoBals[self.sm] -= amount
                    self.totalStaked -= amount
                    self.stakerToStakedAmount[st_sender] -= amount
                    if self.exec[1] != getEpoch(bn()):
                        # Use self.stakes that hasn't been updated yet because the exec
                        # is updated before modifications to stakes
                        self.exec = getExecutor(evmMaths, bn(), self.stakes, self.exec)
                    self.stakes = newStakes
            else:
                print('        NOT_ENOUGH_COUNTS rule_unstake_working_idxs', bn()+1, len(self.stakes),  st_numIdxs, st_sender)



        # Specifically make a staker unstake all their stake to make this more common in
        # the tests since it seems like an edge case could emerge
        def rule_unstake_all_for_staker(self, st_sender):
            n = self.stakes.count(st_sender)
            if n == 0:
                print('        REV_MSG_NOT_ENOUGH_STAKE rule_unstake_all_for_staker', bn()+1, len(self.stakes), st_sender)
                with reverts(REV_MSG_NOT_ENOUGH_STAKE):
                    self.sm.unstake([0], {'from': st_sender})
            else:
                idxs, newStakes = getFirstIndexes(self.stakes, st_sender, n)
                amount = len(idxs) * STAN_STAKE

                print('                    rule_unstake_all_for_staker', bn()+1, len(self.stakes), st_sender)
                self.sm.unstake(idxs, {'from': st_sender})

                self.autoBals[st_sender] += amount
                self.autoBals[self.sm] -= amount
                self.totalStaked -= amount
                self.stakerToStakedAmount[st_sender] -= amount
                if self.exec[1] != getEpoch(bn()):
                    # Use self.stakes that hasn't been updated yet because the exec
                    # is updated before modifications to stakes
                    self.exec = getExecutor(evmMaths, bn(), self.stakes, self.exec)
                self.stakes = newStakes


        def rule_updateExecutor(self, st_sender):
            print('                    rule_updateExecutor', bn()+1, len(self.stakes), st_sender)
            self.sm.updateExecutor({'from': st_sender})

            if self.exec[1] != getEpoch(bn()):
                # Use self.stakes that hasn't been updated yet because the exec
                # is updated before modifications to stakes
                self.exec = getExecutor(evmMaths, bn(), self.stakes, self.exec)


        def rule_isUpdatedExec(self, st_sender, st_sender2):
            print('                    rule_isUpdatedExec', bn()+1, len(self.stakes), st_sender, st_sender2)
            tx = self.sm.isUpdatedExec(st_sender, {'from': st_sender2})

            if self.exec[1] == getEpoch(bn()):
                assert tx.return_value == (self.exec[0] == st_sender)
            else:
                # Use self.stakes that hasn't been updated yet because the exec
                # is updated before modifications to stakes
                self.exec = getExecutor(evmMaths, bn(), self.stakes, self.exec)
                if self.exec[0] == st_sender or len(self.stakes) == 0:
                    assert tx.return_value == True
                else:
                    assert tx.return_value == False
                

        def rule_mine(self, st_mine_num):
            print('                    rule_mine', bn()+1, len(self.stakes), st_mine_num)
            chain.mine(st_mine_num)


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
            assert self.sm.getAUTOAddr() == self.AUTO
            assert self.sm.STAN_STAKE() == STAN_STAKE
            assert self.sm.BLOCKS_IN_EPOCH() == BLOCKS_IN_EPOCH
        

        # Check all the state variables that can be changed after every tx
        def invariant_state_vars(self):
            assert self.sm.getTotalStaked() == self.totalStaked
            assert self.sm.getStakes() == self.stakes
            assert self.sm.getStakesLength() == len(self.stakes)
            assert self.sm.getStakesSlice(0, len(self.stakes)) == self.stakes
            curEpoch = getEpoch(bn())
            assert self.sm.getCurEpoch() == curEpoch
            assert self.sm.getExecutor() == self.exec
            if self.exec[1] != curEpoch:
                assert self.sm.getUpdatedExecRes() == getUpdatedExecResult(evmMaths, bn(), self.stakes, self.exec[1])
            else:
                assert self.sm.getUpdatedExecRes() == (curEpoch, 0, 0, ADDR_0)

            for addr in self.allAddrs:
                assert self.sm.getStake(addr) == self.stakerToStakedAmount[addr]
                assert self.sm.isCurExec(addr) == isCurExec(self.exec, addr, curEpoch, len(self.stakes))

        

        # Print how many rules were executed at the end of each run
        def teardown(self):
            print(f'Total rules executed = {self.numTxsTested-1}')

    
    state_machine(StateMachine, a, cleanAUTO, settings=settings)