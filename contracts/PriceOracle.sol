pragma solidity ^0.8;


import "@openzeppelin/contracts/access/Ownable.sol";
import "../interfaces/IPriceOracle.sol";


contract PriceOracle is IPriceOracle, Ownable {


    uint private _ASCPerUSD;
    uint private _ETHPerUSD;
    uint private _gasPrice;


    constructor(uint ASCPerUSD, uint ETHPerUSD, uint gasPrice) Ownable() {
        _ASCPerUSD = ASCPerUSD;
        _ETHPerUSD = ETHPerUSD;
        _gasPrice = gasPrice;
    }

    function getASCPerUSD() external override view returns (uint) {
        return _ASCPerUSD;
    }

    function updateASCPerUSD(uint ASCPerUSD) external onlyOwner {
        _ASCPerUSD = ASCPerUSD;
    }

    function getETHPerUSD() external override view returns (uint) {
        return _ETHPerUSD;
    }

    function updateETHPerUSD(uint ETHPerUSD) external onlyOwner {
        _ETHPerUSD = ETHPerUSD;
    }

    function getGasPriceFast() external override view returns (uint) {
        return _gasPrice;
    }

    function updateGasPriceFast(uint gasPrice) external onlyOwner {
        _gasPrice = gasPrice;
    }
}