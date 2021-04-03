pragma solidity ^0.8;


import "../interfaces/IOracle.sol";


contract Oracle is IOracle {
    function getRandNum(uint seed) external override view returns (uint) {
        return uint(blockhash(seed));
    }
}