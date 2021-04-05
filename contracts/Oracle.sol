pragma solidity ^0.8;


import "@openzeppelin/contracts/access/Ownable.sol";
import "../interfaces/IOracle.sol";


contract Oracle is IOracle, Ownable {

    uint private _ASCPerETH;


    constructor(uint ASCPerETH) Ownable() {
        _ASCPerETH = ASCPerETH;
    }

    function getRandNum(uint seed) external override view returns (uint) {
        return uint(blockhash(seed));
    }

    function getASCPerETH() external override view returns (uint) {
        return _ASCPerETH;
    }

    function updateASCPerETH(uint ASCPerETH) external onlyOwner override {
        _ASCPerETH = ASCPerETH;
    }
}