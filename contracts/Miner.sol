pragma solidity ^0.8;


import "../interfaces/IRegistry.sol";
import "./abstract/Shared.sol";


contract Miner is Shared {

    IERC20 private _ASCoin;
    IRegistry private _reg;
    uint private _ASCPerReq;
    uint private _ASCPerExec;
    uint private _ASCPerReferal;
    // 1k ASC
    uint public constant MAX_UPDATE_BAL = 1000 * _E_18;
    // 1 ASC
    uint public constant MIN_REWARD = _E_18;
    // 10k ASC
    uint public constant MIN_FUND = 10000 * _E_18;
    // This counts the number of executed requests that the requester
    // has mined rewards for
    mapping(address => uint) private _minedReqCounts;
    // This counts the number of executions that the executor has
    // mined rewards for
    mapping(address => uint) private _minedExecCounts;
    // This counts the number of executed requests that the requester
    // has mined rewards for
    mapping(address => uint) private _minedReferalCounts;


    event RatesUpdated(uint newASCPerReq, uint newASCPerExec, uint newASCPerReferal);


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


    //////////////////////////////////////////////////////////////
    //                                                          //
    //                          Claiming                        //
    //                                                          //
    //////////////////////////////////////////////////////////////

    function claimMiningRewards() external {
        (uint reqRewardCount, uint execRewardCount, uint referalRewardCount, uint rewards) = 
            getAvailableMiningRewards(msg.sender);
        require(rewards > 0, "Miner: no pending rewards");
        
        _minedReqCounts[msg.sender] += reqRewardCount;
        _minedExecCounts[msg.sender] += execRewardCount;
        _minedReferalCounts[msg.sender] += referalRewardCount;
        require(_ASCoin.transfer(msg.sender, rewards));
    }

    function claimReqMiningReward(uint claimCount) external nzUint(claimCount) {
        _claimSpecificMiningReward(_minedReqCounts, _reg.getReqCountOf(msg.sender), claimCount, _ASCPerReq);
    }

    function claimExecMiningReward(uint claimCount) external nzUint(claimCount) {
        _claimSpecificMiningReward(_minedExecCounts, _reg.getExecCountOf(msg.sender), claimCount, _ASCPerExec);
    }

    function claimReferalMiningReward(uint claimCount) external nzUint(claimCount) {
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
            "Miner: claim too large"
        );

        counter[msg.sender] += claimCount;
        require(_ASCoin.transfer(msg.sender, claimCount * rate));
    }


    //////////////////////////////////////////////////////////////
    //                                                          //
    //                      Updating params                     //
    //                                                          //
    //////////////////////////////////////////////////////////////

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
            newASCPerReq >= MIN_REWARD &&
            newASCPerExec >= MIN_REWARD &&
            newASCPerReferal >= MIN_REWARD,
            "Miner: new rates too low"
        );
        require(amountToFund >= MIN_FUND, "Miner: funding too low, peasant");

        // Update rates and fund the Miner
        _ASCPerReq = newASCPerReq;
        _ASCPerExec = newASCPerExec;
        _ASCPerReferal = newASCPerReferal;
        require(_ASCoin.transferFrom(msg.sender, address(this), amountToFund));
        emit RatesUpdated(newASCPerReq, newASCPerExec, newASCPerReferal);
    }


    //////////////////////////////////////////////////////////////
    //                                                          //
    //                          Getters                         //
    //                                                          //
    //////////////////////////////////////////////////////////////

    function getASCPerReq() external view returns (uint) {
        return _ASCPerReq;
    }

    function getASCPerExec() external view returns (uint) {
        return _ASCPerExec;
    }

    function getASCPerReferal() external view returns (uint) {
        return _ASCPerReferal;
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

    function getAvailableMiningRewards(address addr) public view returns (uint, uint, uint, uint) {
        uint reqRewardCount = _reg.getReqCountOf(addr) - _minedReqCounts[addr];
        uint execRewardCount = _reg.getExecCountOf(addr) - _minedExecCounts[addr];
        uint referalRewardCount = _reg.getReferalCountOf(addr) - _minedReferalCounts[addr];

        uint rewards = 
            (reqRewardCount * _ASCPerReq) +
            (execRewardCount * _ASCPerExec) +
            (referalRewardCount * _ASCPerReferal);
        
        return (reqRewardCount, execRewardCount, referalRewardCount, rewards);
    }
}