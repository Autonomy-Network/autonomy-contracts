from consts import *


def test_constructor(asc, ASCProxy):
    ascProxy = asc.DEPLOYER.deploy(ASCProxy, asc.ALICE)
    
    print(ascProxy.tx.gas_used)
    assert False