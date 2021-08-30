pragma solidity 0.8.6;


import "../interfaces/IRegistry.sol";
import "./abstract/Shared.sol";


contract Miner is Shared {

    IERC20 private _AUTO;
    IRegistry private _reg;
    uint private _AUTOPerReq;
    uint private _AUTOPerExec;
    uint private _AUTOPerReferal;
    // 1k AUTO
    uint public constant MAX_UPDATE_BAL = 1000 * _E_18;
    // 1 AUTO
    uint public constant MIN_REWARD = _E_18;
    // 10k AUTO
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


    event RatesUpdated(uint newAUTOPerReq, uint newAUTOPerExec, uint newAUTOPerReferal);


    constructor(
        IERC20 AUTO,
        IRegistry reg,
        uint AUTOPerReq,
        uint AUTOPerExec,
        uint AUTOPerReferal
    ) {
        _AUTO = AUTO;
        _reg = reg;
        _AUTOPerReq = AUTOPerReq;
        _AUTOPerExec = AUTOPerExec;
        _AUTOPerReferal = AUTOPerReferal;
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
        require(_AUTO.transfer(msg.sender, rewards));
    }

    function claimReqMiningReward(uint claimCount) external nzUint(claimCount) {
        _claimSpecificMiningReward(_minedReqCounts, _reg.getReqCountOf(msg.sender), claimCount, _AUTOPerReq);
    }

    function claimExecMiningReward(uint claimCount) external nzUint(claimCount) {
        _claimSpecificMiningReward(_minedExecCounts, _reg.getExecCountOf(msg.sender), claimCount, _AUTOPerExec);
    }

    function claimReferalMiningReward(uint claimCount) external nzUint(claimCount) {
        _claimSpecificMiningReward(_minedReferalCounts, _reg.getReferalCountOf(msg.sender), claimCount, _AUTOPerReferal);
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
        require(_AUTO.transfer(msg.sender, claimCount * rate));
    }


    //////////////////////////////////////////////////////////////
    //                                                          //
    //                      Updating params                     //
    //                                                          //
    //////////////////////////////////////////////////////////////

    function updateAndFund(
        uint newAUTOPerReq,
        uint newAUTOPerExec,
        uint newAUTOPerReferal,
        uint amountToFund
    ) external {
        require(_AUTO.balanceOf(address(this)) <= MAX_UPDATE_BAL, "Miner: AUTO bal too high");
        // So that nobody updates with a small amount of AUTO and makes the rates
        // 1 wei, effectively bricking the contract
        require(
            newAUTOPerReq >= MIN_REWARD &&
            newAUTOPerExec >= MIN_REWARD &&
            newAUTOPerReferal >= MIN_REWARD,
            "Miner: new rates too low"
        );
        require(amountToFund >= MIN_FUND, "Miner: funding too low, peasant");

        // Update rates and fund the Miner
        _AUTOPerReq = newAUTOPerReq;
        _AUTOPerExec = newAUTOPerExec;
        _AUTOPerReferal = newAUTOPerReferal;
        require(_AUTO.transferFrom(msg.sender, address(this), amountToFund));
        emit RatesUpdated(newAUTOPerReq, newAUTOPerExec, newAUTOPerReferal);
    }


    //////////////////////////////////////////////////////////////
    //                                                          //
    //                          Getters                         //
    //                                                          //
    //////////////////////////////////////////////////////////////

    function getAUTOPerReq() external view returns (uint) {
        return _AUTOPerReq;
    }

    function getAUTOPerExec() external view returns (uint) {
        return _AUTOPerExec;
    }

    function getAUTOPerReferal() external view returns (uint) {
        return _AUTOPerReferal;
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
            (reqRewardCount * _AUTOPerReq) +
            (execRewardCount * _AUTOPerExec) +
            (referalRewardCount * _AUTOPerReferal);
        
        return (reqRewardCount, execRewardCount, referalRewardCount, rewards);
    }
}