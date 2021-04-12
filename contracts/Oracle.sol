pragma solidity ^0.8;


import "@openzeppelin/contracts/access/Ownable.sol";
import "../interfaces/IOracle.sol";
import "../interfaces/IPriceOracle.sol";


contract Oracle is IOracle, Ownable {

    IPriceOracle private _priceOracle;


    constructor(IPriceOracle priceOracle) Ownable() {
        _priceOracle = priceOracle;
    }


    function getRandNum(uint seed) external override view returns (uint) {
        return uint(blockhash(seed));
    }

    function getPriceOracle() external override view returns (IPriceOracle) {
        return _priceOracle;
    }

    function getASCPerETH() external override view returns (uint) {
        return _priceOracle.getASCPerETH();
    }

    function setPriceOracle(IPriceOracle newPriceOracle) external override onlyOwner {
        _priceOracle = newPriceOracle;
    }
}