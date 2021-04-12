pragma solidity ^0.8;


import "@openzeppelin/contracts/access/Ownable.sol";
import "../interfaces/IPriceOracle.sol";


contract PriceOracle is IPriceOracle, Ownable {


    uint private _ASCPerETH;


    constructor(uint ASCPerETH) Ownable() {
        _ASCPerETH = ASCPerETH;
    }


    function getASCPerETH() external override view returns (uint) {
        return _ASCPerETH;
    }

    function updateASCPerETH(uint ASCPerETH) external onlyOwner override {
        _ASCPerETH = ASCPerETH;
    }
}