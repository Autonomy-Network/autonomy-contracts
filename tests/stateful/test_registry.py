# from consts import *
# from utils import *
# from brownie import reverts, chain, web3
# from brownie.test import strategy, contract_strategy


# settings = {"stateful_step_count": 50, "max_examples": 25}

# def test_registry(BaseStateMachine, state_machine, a, cleanAUTO, evmMaths, MockTarget):

#     INIT_TOKEN_AMNT = 10**25
#     NUM_SENDERS = 5
#     MAX_ETH_AMOUNT = (INIT_ETH_BAL / 10)
    
#     class StateMachine(BaseStateMachine):

#         # Set up the initial test conditions once
#         def __init__(cls, a, cleanAUTO):
#             super().__init__(cls, a, cleanAUTO)

#             cls.target = a[0].deploy(MockTarget, cls.uf, ADDR_0)
#             cls.senders = a[:NUM_SENDERS]
#             cls.allAddrs = cls.senders + [cls.r]

#             # Distribute tokens evenly to NUM_SENDERS and call approve from each of them
#             for addr in a[:NUM_SENDERS]:
#                 cls.AUTO.transfer(addr, INIT_TOKEN_AMNT, {'from': a[0]})
#                 cls.AUTO.approve(cls.sm, BIG_NUM, {'from': addr})
            
#             deployerBal = cls.AUTO.balanceOf(a[0])
#             if deployerBal > INIT_TOKEN_AMNT:
#                 cls.AUTO.transfer('0x0000000000000000000000000000000000000001', deployerBal - INIT_TOKEN_AMNT)
            
            

#         # Reset the local versions of state to compare the contract to after every run
#         def setup(self):
#             self.ethBals = {addr: INIT_ETH_BAL if addr in a else 0 for addr in self.allAddrs}
#             self.autoBals = {addr: INIT_TOKEN_AMNT if addr in a else 0 for addr in self.allAddrs}
#             self.rawReqs = []
#             self.hashedReqs = []
#             self.hashedReqsUnveri = []
#             self.rawReqCounts = {addr: 0 for addr in self.allAddrs}
#             self.hashedReqCounts = {addr: 0 for addr in self.allAddrs}
#             self.hashedReqUnveriCounts = {addr: 0 for addr in self.allAddrs}
#             self.numTxsTested = 0

#             self.tarX = 0
#             self.tarUserAddr = ADDR_0
#             self.tarMsgSender = ADDR_0


#         st_sender = strategy("address", length=NUM_SENDERS)
#         st_referer = strategy("address", length=NUM_SENDERS)
#         st_msgValue = strategy("uint", max_value=MAX_ETH_AMOUNT)
#         st_ethForCall = strategy("uint", max_value=MAX_ETH_AMOUNT)
#         st_verifySender = strategy("bool")
#         st_payWithAUTO = strategy("bool")
#         st_x = strategy("uint")
#         st_newUserAddr = strategy("address", length=NUM_SENDERS)
#         st_id_src = strategy("uint")


#         def rule_newReq_setX(self, st_x, st_referer, st_msgValue, st_ethForCall, st_verifySender, st_payWithAUTO, st_sender):
#             inputs = st_x, self.target, st_referer, st_msgValue, st_ethForCall, st_verifySender, st_payWithAUTO, st_sender
#             callData = self.target.setX.encode_input(st_x)

#             if st_payWithAUTO and st_ethForCall != st_msgValue:
#                 print('        REV_MSG_ETHFORCALL_NOT_MSGVALUE rule_newReq_setX', inputs)
#                 with reverts(REV_MSG_ETHFORCALL_NOT_MSGVALUE):
#                     self.r.newReqPaySpecific(self.target, st_referer, callData, st_ethForCall, st_verifySender, st_payWithAUTO, {'value': st_msgValue, 'from': st_sender})

#             elif (not st_payWithAUTO) and st_ethForCall > st_msgValue:
#                 print('        REV_MSG_ETHFORCALL_HIGH rule_newReq_setX', inputs)
#                 with reverts(REV_MSG_ETHFORCALL_HIGH):
#                     self.r.newReqPaySpecific(self.target, st_referer, callData, st_ethForCall, st_verifySender, st_payWithAUTO, {'value': st_msgValue, 'from': st_sender})
            
#             elif st_verifySender:
#                 print('        CANNOT_DECODE_TO_ADDRESS rule_newReq_setX', inputs)
#                 with reverts(''):
#                     self.r.newReqPaySpecific(self.target, st_referer, callData, st_ethForCall, st_verifySender, st_payWithAUTO, {'value': st_msgValue, 'from': st_sender})

#             else:
#                 print('                    rule_newReq_setX', inputs)
#                 self.r.newReqPaySpecific(self.target, st_referer, callData, st_ethForCall, st_verifySender, st_payWithAUTO, {'value': st_msgValue, 'from': st_sender})

#                 req = (st_sender, self.target, st_referer, callData, st_msgValue, st_ethForCall, st_verifySender, st_payWithAUTO)
#                 self.rawReqs.append(req)
#                 self.ethBals[self.r] += st_msgValue
#                 self.ethBals[st_sender] -= st_msgValue


#         # Parameters where it won't fail most of the time
#         def rule_newReq_setX_working(self, st_x, st_referer, st_msgValue, st_payWithAUTO, st_sender):
#             if st_payWithAUTO: st_msgValue = 0
#             inputs = st_x, self.target, st_referer, st_msgValue, st_payWithAUTO, st_sender
#             callData = self.target.setX.encode_input(st_x)
            
#             print('                    rule_newReq_setX_working', inputs)
#             self.r.newReqPaySpecific(self.target, st_referer, callData, 0, False, st_payWithAUTO, {'value': st_msgValue, 'from': st_sender})

#             req = (st_sender, self.target, st_referer, callData, st_msgValue, 0, False, st_payWithAUTO)
#             self.rawReqs.append(req)
#             self.ethBals[self.r] += st_msgValue
#             self.ethBals[st_sender] -= st_msgValue


#         def rule_newReq_setXPay(self, st_x, st_referer, st_msgValue, st_ethForCall, st_verifySender, st_payWithAUTO, st_sender):
#             inputs = st_x, self.target, st_referer, st_msgValue, st_ethForCall, st_verifySender, st_payWithAUTO, st_sender
#             callData = self.target.setXPay.encode_input(st_x)

#             if st_payWithAUTO and st_ethForCall != st_msgValue:
#                 print('        REV_MSG_ETHFORCALL_NOT_MSGVALUE rule_newReq_setXPay', inputs)
#                 with reverts(REV_MSG_ETHFORCALL_NOT_MSGVALUE):
#                     self.r.newReqPaySpecific(self.target, st_referer, callData, st_ethForCall, st_verifySender, st_payWithAUTO, {'value': st_msgValue, 'from': st_sender})

#             elif (not st_payWithAUTO) and st_ethForCall > st_msgValue:
#                 print('        REV_MSG_ETHFORCALL_HIGH rule_newReq_setXPay', inputs)
#                 with reverts(REV_MSG_ETHFORCALL_HIGH):
#                     self.r.newReqPaySpecific(self.target, st_referer, callData, st_ethForCall, st_verifySender, st_payWithAUTO, {'value': st_msgValue, 'from': st_sender})
            
#             elif st_verifySender:
#                 print('        CANNOT_DECODE_TO_ADDRESS rule_newReq_setXPay', inputs)
#                 with reverts(''):
#                     self.r.newReqPaySpecific(self.target, st_referer, callData, st_ethForCall, st_verifySender, st_payWithAUTO, {'value': st_msgValue, 'from': st_sender})

#             else:
#                 print('                    rule_newReq_setXPay', inputs)
#                 self.r.newReqPaySpecific(self.target, st_referer, callData, st_ethForCall, st_verifySender, st_payWithAUTO, {'value': st_msgValue, 'from': st_sender})

#                 req = (st_sender, self.target, st_referer, callData, st_msgValue, st_ethForCall, st_verifySender, st_payWithAUTO)
#                 self.rawReqs.append(req)
#                 self.ethBals[self.r] += st_msgValue
#                 self.ethBals[st_sender] -= st_msgValue


#         # Parameters where it won't fail most of the time
#         def rule_newReq_setXPay_working(self, st_x, st_referer, st_ethForCall, st_msgValue, st_payWithAUTO, st_sender):
#             inputs = st_x, self.target, st_referer, st_msgValue, st_payWithAUTO, st_sender
#             callData = self.target.setXPay.encode_input(st_x)
            
#             print('                    rule_newReq_setXPay_working', inputs)
#             self.r.newReqPaySpecific(self.target, st_referer, callData, 0, False, st_payWithAUTO, {'value': st_msgValue, 'from': st_sender})

#             req = (st_sender, self.target, st_referer, callData, st_msgValue, 0, False, st_payWithAUTO)
#             self.rawReqs.append(req)
#             self.ethBals[self.r] += st_msgValue
#             self.ethBals[st_sender] -= st_msgValue


#         def rule_newReq_setAddrPayVerified(self, st_newUserAddr, st_referer, st_msgValue, st_ethForCall, st_verifySender, st_payWithAUTO, st_sender):
#             inputs = st_newUserAddr, self.target, st_referer, st_msgValue, st_ethForCall, st_verifySender, st_payWithAUTO, st_sender
#             callData = self.target.setAddrPayUserVerified.encode_input(st_newUserAddr)

#             if st_payWithAUTO and st_ethForCall != st_msgValue:
#                 print('        REV_MSG_ETHFORCALL_NOT_MSGVALUE rule_newReq_setAddrPayVerified', inputs)
#                 with reverts(REV_MSG_ETHFORCALL_NOT_MSGVALUE):
#                     self.r.newReqPaySpecific(self.target, st_referer, callData, st_ethForCall, st_verifySender, st_payWithAUTO, {'value': st_msgValue, 'from': st_sender})

#             elif (not st_payWithAUTO) and st_ethForCall > st_msgValue:
#                 print('        REV_MSG_ETHFORCALL_HIGH rule_newReq_setAddrPayVerified', inputs)
#                 with reverts(REV_MSG_ETHFORCALL_HIGH):
#                     self.r.newReqPaySpecific(self.target, st_referer, callData, st_ethForCall, st_verifySender, st_payWithAUTO, {'value': st_msgValue, 'from': st_sender})
            
#             elif st_verifySender and st_newUserAddr != st_sender:
#                 print('        REV_MSG_CALLDATA_NOT_VER rule_newReq_setAddrPayVerified', inputs)
#                 with reverts(REV_MSG_CALLDATA_NOT_VER):
#                     self.r.newReqPaySpecific(self.target, st_referer, callData, st_ethForCall, st_verifySender, st_payWithAUTO, {'value': st_msgValue, 'from': st_sender})

#             else:
#                 print('                    rule_newReq_setAddrPayVerified', inputs)
#                 self.r.newReqPaySpecific(self.target, st_referer, callData, st_ethForCall, st_verifySender, st_payWithAUTO, {'value': st_msgValue, 'from': st_sender})

#                 req = (st_sender, self.target, st_referer, callData, st_msgValue, st_ethForCall, st_verifySender, st_payWithAUTO)
#                 self.rawReqs.append(req)
#                 self.ethBals[self.r] += st_msgValue
#                 self.ethBals[st_sender] -= st_msgValue


#         def rule_executeRawReq(self, st_id_src, st_sender):
#             if len(self.rawReqs) > 0:
#                 # st_id_src isn't able to know about the length of self.stakes, and we want it to fail occasionally
#                 # so that 'out of bounds' is tested while still mainly providing useful results
#                 id = st_id_src % int(len(self.rawReqs)*1.01)

#                 if id >= len(self.rawReqs):
#                     print('        REV_MSG_CALLDATA_NOT_VER rule_newReq_setAddrPayVerified', inputs)
#                     with reverts(REV_MSG_CALLDATA_NOT_VER):
#                         self.r.executeRawReq(id)


#         # Check all the balances of every address are as they should be after every tx
#         def invariant_bals(self):
#             self.numTxsTested += 1
#             for addr in self.allAddrs:
#                 assert addr.balance() == self.ethBals[addr]
#                 assert self.AUTO.balanceOf(addr) == self.autoBals[addr]


#         # Check variable(s) after every tx that shouldn't change since there's
#         # no intentional way to
#         def invariant_nonchangeable(self):
#             assert self.r.GAS_OVERHEAD_AUTO() == GAS_OVERHEAD_AUTO
#             assert self.r.GAS_OVERHEAD_ETH() == GAS_OVERHEAD_ETH
#             assert self.r.BASE_BPS() == BASE_BPS
#             assert self.r.PAY_AUTO_BPS() == PAY_AUTO_BPS
#             assert self.r.PAY_ETH_BPS() == PAY_ETH_BPS
#             assert self.r.getAUTOAddr() == self.AUTO
#             assert self.r.getStakeManager() == self.sm
#             assert self.r.getOracle() == self.o
#             assert self.r.getUserForwarder() == self.uf
#             assert self.target.veriForwarderAddr() == self.uf


#         # Check all the state variables that can be changed after every tx
#         def invariant_state_vars(self):
#             # Raw reqs
#             assert self.r.getRawReqs() == self.rawReqs
#             assert self.r.getRawReqsSlice(0, len(self.rawReqs)) == self.rawReqs
#             assert self.r.getRawReqLen() == len(self.rawReqs)
#             # Can probably comment out cause this'll make tests take forever
#             for i, req in enumerate(self.rawReqs):
#                 assert self.r.getRawReq(i) == req
            
#             # Hashed reqs
#             assert self.r.getHashedReqs() == self.hashedReqs
#             assert self.r.getHashedReqsSlice(0, len(self.hashedReqs)) == self.hashedReqs
#             assert self.r.getHashedReqsLen() == len(self.hashedReqs)
#             # Can probably comment out cause this'll make tests take forever
#             for i, req in enumerate(self.hashedReqs):
#                 assert self.r.getHashedReq(i) == req
            
#             # Hashed unverified reqs
#             assert self.r.getHashedReqsUnveri() == self.hashedReqsUnveri
#             assert self.r.getHashedReqsUnveriSlice(0, len(self.hashedReqsUnveri)) == self.hashedReqsUnveri
#             assert self.r.getHashedReqsUnveriLen() == len(self.hashedReqsUnveri)
#             # Can probably comment out cause this'll make tests take forever
#             for i, req in enumerate(self.hashedReqsUnveri):
#                 assert self.r.getHashedReqUnveri(i) == req
            
#             # Action counters
#             for sender in self.senders:
#                 assert self.r.getReqCountOf(sender) == self.rawReqCounts[sender]
#                 assert self.r.getExecCountOf(sender) == self.hashedReqCounts[sender]
#                 assert self.r.getReferalCountOf(sender) == self.hashedReqUnveriCounts[sender]
            
#             # Target
#             assert self.target.x() == self.tarX
#             assert self.target.userAddr() == self.tarUserAddr
#             assert self.target.msgSender() == self.tarMsgSender


        

#         # Print how many rules were executed at the end of each run
#         def teardown(self):
#             print(f'Total rules executed = {self.numTxsTested-1}')

    
#     state_machine(StateMachine, a, cleanAUTO, settings=settings)