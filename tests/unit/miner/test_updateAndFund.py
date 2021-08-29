from consts import *
from brownie.test import given, strategy
from brownie import reverts


# Might aswell test all conditions at once /shrug
@given(
    minerInitBal=strategy('uint', max_value=MAX_UPDATE_BAL * 2),
    newAUTOPerReq=strategy('uint'),
    newAUTOPerExec=strategy('uint'),
    newAUTOPerReferal=strategy('uint'),
    amountToFund=strategy('uint', max_value=MAX_UPDATE_BAL * 2),
    sender=strategy('address')
)
def test_udateAndFund(a, auto, freshMiner, minerInitBal, newAUTOPerReq, newAUTOPerExec, newAUTOPerReferal, amountToFund, sender):
    auto.AUTO.transfer(freshMiner, minerInitBal, auto.FR_DEPLOYER)
    if auto.AUTO.balanceOf(freshMiner) > MAX_UPDATE_BAL:
        with reverts(REV_MSG_BAL_TOO_HIGH):
            freshMiner.updateAndFund(newAUTOPerReq, newAUTOPerExec, newAUTOPerReferal, amountToFund, {'from': sender})

    elif newAUTOPerReq < MIN_REWARD or newAUTOPerExec < MIN_REWARD or newAUTOPerReferal < MIN_REWARD:
        with reverts(REV_MSG_RATES_TOO_LOW):
            freshMiner.updateAndFund(newAUTOPerReq, newAUTOPerExec, newAUTOPerReferal, amountToFund, {'from': sender})
    
    elif amountToFund < MIN_FUND:
        with reverts(REV_MSG_FUND_TOO_LOW):
            freshMiner.updateAndFund(newAUTOPerReq, newAUTOPerExec, newAUTOPerReferal, amountToFund, {'from': sender})
    
    else:
        auto.AUTO.transfer(sender, amountToFund, auto.FR_DEPLOYER)
        startBal = auto.AUTO.balanceOf(sender)

        tx = freshMiner.updateAndFund(newAUTOPerReq, newAUTOPerExec, newAUTOPerReferal, amountToFund, {'from': sender})

        assert freshMiner.getAUTOPerReq() == newAUTOPerReq
        assert freshMiner.getAUTOPerExec() == newAUTOPerExec
        assert freshMiner.getAUTOPerReferal() == newAUTOPerReferal
        assert freshMiner.getAvailableMiningRewards(sender) == (0, 0, 0, 0)
        assert auto.AUTO.balanceOf(sender) - startBal == -amountToFund
        assert auto.AUTO.balanceOf(freshMiner) == minerInitBal + amountToFund
        assert tx.events["RatesUpdated"][0].values() == (newAUTOPerReq, newAUTOPerExec, newAUTOPerReferal)


# When the caller hasn't called AUTO.approve
def test_udateAndFund_rev_allowance(a, auto, freshMiner):
    with reverts(REV_MSG_EXCEED_ALLOWANCE):
        freshMiner.updateAndFund(E_18, E_18, E_18, MIN_FUND, auto.FR_DEPLOYER)