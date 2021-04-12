pragma solidity ^0.8;


import "../interfaces/IPriceOracle.sol";


interface IOracle {
    // Needs to output the same number for the whole epoch
    function getRandNum(uint salt) external returns (uint);

    function getPriceOracle() external view returns (IPriceOracle);

    function getASCPerETH() external view returns (uint);

    function setPriceOracle(IPriceOracle newPriceOracle) external;
}