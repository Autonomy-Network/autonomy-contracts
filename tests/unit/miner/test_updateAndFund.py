from consts import *
from brownie.test import given, strategy
from brownie import reverts


# Might aswell test all conditions at once /shrug
@given(
    minerInitBal=strategy('uint', max_value=MAX_UPDATE_BAL * 2),
    newASCPerReq=strategy('uint'),
    newASCPerExec=strategy('uint'),
    newASCPerReferal=strategy('uint'),
    amountToFund=strategy('uint', max_value=MAX_UPDATE_BAL * 2),
    sender=strategy('address')
)
def test_udateAndFund(a, asc, freshMiner, minerInitBal, newASCPerReq, newASCPerExec, newASCPerReferal, amountToFund, sender):
    asc.ASC.transfer(freshMiner, minerInitBal, asc.FR_DEPLOYER)
    if asc.ASC.balanceOf(freshMiner) > MAX_UPDATE_BAL:
        with reverts(REV_MSG_BAL_TOO_HIGH):
            freshMiner.updateAndFund(newASCPerReq, newASCPerExec, newASCPerReferal, amountToFund, {'from': sender})

    elif newASCPerReq < MIN_REWARD or newASCPerExec < MIN_REWARD or newASCPerReferal < MIN_REWARD:
        with reverts(REV_MSG_RATES_TOO_LOW):
            freshMiner.updateAndFund(newASCPerReq, newASCPerExec, newASCPerReferal, amountToFund, {'from': sender})
    
    elif amountToFund < MIN_FUND:
        with reverts(REV_MSG_FUND_TOO_LOW):
            freshMiner.updateAndFund(newASCPerReq, newASCPerExec, newASCPerReferal, amountToFund, {'from': sender})
    
    else:
        asc.ASC.transfer(sender, amountToFund, asc.FR_DEPLOYER)
        asc.ASC.approve(freshMiner, amountToFund, {'from': sender})
        startBal = asc.ASC.balanceOf(sender)

        tx = freshMiner.updateAndFund(newASCPerReq, newASCPerExec, newASCPerReferal, amountToFund, {'from': sender})

        assert freshMiner.getASCPerReq() == newASCPerReq
        assert freshMiner.getASCPerExec() == newASCPerExec
        assert freshMiner.getASCPerReferal() == newASCPerReferal
        assert freshMiner.getAvailableMiningRewards(sender) == (0, 0, 0, 0)
        assert asc.ASC.balanceOf(sender) - startBal == -amountToFund
        assert asc.ASC.balanceOf(freshMiner) == minerInitBal + amountToFund
        assert tx.events["RatesUpdated"][0].values() == (newASCPerReq, newASCPerExec, newASCPerReferal)


# When the caller hasn't called ASC.approve
def test_udateAndFund_rev_allowance(a, asc, freshMiner):
    with reverts(REV_MSG_EXCEED_ALLOWANCE):
        freshMiner.updateAndFund(E_18, E_18, E_18, MIN_FUND, asc.FR_DEPLOYER)