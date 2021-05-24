pragma solidity ^0.8;


import "../interfaces/IPriceOracle.sol";


interface IOracle {
    // Needs to output the same number for the whole epoch
    function getRandNum(uint salt) external view returns (uint);

    function getPriceOracle() external view returns (IPriceOracle);

    function getAUTOPerETH() external view returns (uint);

    function getGasPriceFast() external view returns (uint);
}