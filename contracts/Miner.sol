pragma solidity ^0.8;


import "../interfaces/IRegistry.sol";


contract Miner {

    IERC20 private _ASCoin;
    IRegistry private _reg;
    uint private _ASCPerReq;
    uint private _ASCPerExec;
    uint private _ASCPerReferal;
    uint public constant MAX_UPDATE_BAL = 10**21;
    uint public constant MIN_REWARD = 10**18;
    // This counts the number of executed requests that the requester
    // has mined rewards for
    mapping(address => uint) private _minedReqCounts;
    // This counts the number of executions that the executor has
    // mined rewards for
    mapping(address => uint) private _minedExecCounts;
    // This counts the number of executed requests that the requester
    // has mined rewards for
    mapping(address => uint) private _minedReferalCounts;


    constructor(
        IERC20 ASCoin,
        IRegistry reg,
        uint ASCPerReq,
        uint ASCPerExec,
        uint ASCPerReferal
    ) {
        _ASCoin = ASCoin;
        _reg = reg;
        _ASCPerReq = ASCPerReq;
        _ASCPerExec = ASCPerExec;
        _ASCPerReferal = ASCPerReferal;
    }

    function getMiningRewards(address addr) public view returns (uint, uint, uint, uint) {
        uint reqRewardCount = _reg.getReqCountOf(addr) - _minedReqCounts[addr];
        uint execRewardCount = _reg.getExecCountOf(addr) - _minedExecCounts[addr];
        uint referalRewardCount = _reg.getReferalCountOf(addr) - _minedReferalCounts[addr];

        uint rewards = 
            (reqRewardCount * _ASCPerReq) +
            (execRewardCount * _ASCPerExec) +
            (referalRewardCount * _ASCPerReferal);
        
        return (reqRewardCount, execRewardCount, referalRewardCount, rewards);
    }

    function claimMiningRewards() external {
        (uint reqRewardCount, uint execRewardCount, uint referalRewardCount, uint rewards) = 
            getMiningRewards(msg.sender);
        
        _minedReqCounts[msg.sender] += reqRewardCount;
        _minedExecCounts[msg.sender] += execRewardCount;
        _minedReferalCounts[msg.sender] += referalRewardCount;
        _ASCoin.transfer(msg.sender, rewards);
    }

    function claimReqMiningReward(uint claimCount) external {
        _claimSpecificMiningReward(_minedReqCounts, _reg.getReqCountOf(msg.sender), claimCount, _ASCPerReq);
    }

    function claimExecMiningReward(uint claimCount) external {
        _claimSpecificMiningReward(_minedExecCounts, _reg.getExecCountOf(msg.sender), claimCount, _ASCPerExec);
    }

    function claimReferalMiningReward(uint claimCount) external {
        _claimSpecificMiningReward(_minedReferalCounts, _reg.getReferalCountOf(msg.sender), claimCount, _ASCPerReferal);
    }

    function _claimSpecificMiningReward(
        mapping(address => uint) storage counter,
        uint regCount,
        uint claimCount,
        uint rate
    ) private {
        require(
            claimCount <= regCount - counter[msg.sender],
            "Miner: not enough"
        );

        counter[msg.sender] += claimCount;
        _ASCoin.transfer(msg.sender, claimCount * rate);
    }

    function getMinedReqCountOf(address addr) external view returns (uint) {
        return _minedReqCounts[addr];
    }

    function getMinedExecCountOf(address addr) external view returns (uint) {
        return _minedExecCounts[addr];
    }

    function getMinedReferalCountOf(address addr) external view returns (uint) {
        return _minedReferalCounts[addr];
    }

    function updateAndFund(
        uint newASCPerReq,
        uint newASCPerExec,
        uint newASCPerReferal,
        uint amountToFund
    ) external {
        require(_ASCoin.balanceOf(address(this)) <= MAX_UPDATE_BAL, "Miner: ASC bal too high");
        // So that nobody updates with a small amount of ASC and makes the rates
        // 1 wei, effectively bricking the contract
        require(
            newASCPerExec >= MIN_REWARD &&
            newASCPerReferal >= MIN_REWARD &&
            newASCPerReferal >= MIN_REWARD,
            "Miner: new rates not high enough"
        );

        // Update rates and fund the Miner
        _ASCPerReq = newASCPerReq;
        _ASCPerExec = newASCPerExec;
        _ASCPerReferal = newASCPerReferal;
        _ASCoin.transferFrom(msg.sender, address(this), amountToFund);
    }
}