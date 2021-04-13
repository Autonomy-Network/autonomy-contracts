pragma solidity ^0.8;


interface IStakeManager {
    function stake(uint numStakes) external;
    function unstake(uint[] calldata idxs) external;
    function isCurExec(address addr) external returns (bool);
    function updateExecutor() external returns (uint, uint, uint, address);
    function isUpdatedExec(address addr) external returns (bool);

}
