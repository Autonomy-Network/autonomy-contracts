pragma solidity 0.8.6;


import "@openzeppelin/contracts/access/Ownable.sol";
import "../interfaces/IPriceOracle.sol";


contract PriceOracle is IPriceOracle, Ownable {


    uint private _AUTOPerETH;

    constructor(uint AUTOPerETH) Ownable() {
        _AUTOPerETH = AUTOPerETH;
    }

    function getAUTOPerETH() external override view returns (uint) {
        return _AUTOPerETH;
    }

    function updateAUTOPerETH(uint AUTOPerETH) external onlyOwner {
        _AUTOPerETH = AUTOPerETH;
    }

    function getGasPriceFast() external override view returns (uint) {
        return tx.gasprice;
    }
}