pragma solidity ^0.7.0;


interface IOracle {
    // Needs to output the same number for the whole epoch
    function getRandNum(uint salt) external returns (uint);
    // function getPrice(address tokenAddr) external returns (uint);
}