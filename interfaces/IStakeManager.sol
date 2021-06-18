pragma solidity ^0.8;


import "./IOracle.sol";


interface IStakeManager {

    struct Executor{
        address addr;
        uint forEpoch;
    }


    //////////////////////////////////////////////////////////////
    //                                                          //
    //                          Getters                         //
    //                                                          //
    //////////////////////////////////////////////////////////////
    
    function getOracle() external view returns (IOracle);

    function getAUTO() external view returns (address);

    function getTotalStaked() external view returns (uint);

    function getStake(address staker) external view returns (uint);

    function getStakes() external view returns (address[] memory);

    function getStakesLength() external view returns (uint);

    function getStakesSlice(uint startIdx, uint endIdx) external view returns (address[] memory);

    function getCurEpoch() external view returns (uint);

    function getExecutor() external view returns (Executor memory);

    function isCurExec(address addr) external view returns (bool);

    function getUpdatedExecRes() external view returns (uint epoch, uint randNum, uint idxOfExecutor, address exec);

    //////////////////////////////////////////////////////////////
    //                                                          //
    //                          Staking                         //
    //                                                          //
    //////////////////////////////////////////////////////////////

    function updateExecutor() external returns (uint, uint, uint, address);

    function isUpdatedExec(address addr) external returns (bool);

    function stake(uint numStakes) external;

    function unstake(uint[] calldata idxs) external;
}