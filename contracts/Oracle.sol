pragma solidity ^0.7.0;


import "../interfaces/IOracle.sol";


contract Oracle is IOracle {
    function getRandNum(uint seed) external override view returns (uint) {
        return uint(blockhash(seed));
    }
}