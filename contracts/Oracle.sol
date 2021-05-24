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

    function getAUTOPerETH() external override view returns (uint) {
        return _priceOracle.getAUTOPerETH();
    }

    function getGasPriceFast() external override view returns (uint) {
        return _priceOracle.getGasPriceFast();
    }

    function setPriceOracle(IPriceOracle newPriceOracle) external onlyOwner {
        _priceOracle = newPriceOracle;
    }
}