pragma solidity ^0.7.0;


interface IStakeManager {
    function stake(uint numStakes) external returns (uint, uint, address);
    function unstake(uint[] calldata idxs) external;
    function isCurExec(address addr) external returns (bool);
}
