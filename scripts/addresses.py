from brownie import network, Registry, Oracle, Forwarder, Heroes, BrainOracle, MetaDungeon, BossFactory, Boss, MetaBrain, MockNFT, MockERC777, TProxyAdmin, TProxy, MockAdmin


class Context:
    pass

PUBLISH_SOURCE = True

auto = Context()


if network.show_active() == 'mainnet':
    po_addr = '0x2d08DAAE7687f4516287EBF1bF6c3819f7517Ac9'
    o_addr = '0xD73909B3924Ec5b4677E31a445220820065377B6'
    sm_addr = '0x1ae2c18eb01478B53Ab55BCe518Af2fE64Ff020e'
    uf_addr = '0x5f56BcdcCfcafD27b7E9e05D8bc663d3F2D74Fc3'
    ff_addr = '0x6e5Ec7f4C98B34e0aAAA02D8D2136e626ED33B10'
    uff_addr = '0x4e61bA21DcEcD36De254AeEdDe0213e959213B17'
    r_addr = '0x973107d4b9A5B69fd99c23a3C31eFA8fafE7Ae38'
    tl_addr = '0x951cf7124450AB10A83465aA9cE1759ceeF69aC0'