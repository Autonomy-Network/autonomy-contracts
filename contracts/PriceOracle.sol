pragma solidity ^0.8;


import "@openzeppelin/contracts/access/Ownable.sol";
import "../interfaces/IPriceOracle.sol";


contract PriceOracle is IPriceOracle, Ownable {


    uint private _ASCPerUSD;
    uint private _ETHPerUSD;


    constructor(uint ASCPerUSD, uint ETHPerUSD) Ownable() {
        _ASCPerUSD = ASCPerUSD;
        _ETHPerUSD = ETHPerUSD;
    }

    function getASCPerUSD() external override view returns (uint) {
        return _ASCPerUSD;
    }

    function updateASCPerUSD(uint ASCPerUSD) external onlyOwner override {
        _ASCPerUSD = ASCPerUSD;
    }

    function getETHPerUSD() external override view returns (uint) {
        return _ETHPerUSD;
    }

    function updateETHPerUSD(uint ETHPerUSD) external onlyOwner override {
        _ETHPerUSD = ETHPerUSD;
    }
}