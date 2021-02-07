pragma solidity ^0.7.0;


interface IStakeManager {
    function stake(uint amount) external returns (uint, uint, address);
    function unstake(uint amount) external;
    function isCurExec(address addr) external returns (bool);
}
