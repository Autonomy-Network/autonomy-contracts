pragma solidity ^0.8;


interface IPriceOracle {

    function getASCPerUSD() external view returns (uint);

    function getETHPerUSD() external view returns (uint);

    function getGasPriceFast() external view returns (uint);
}