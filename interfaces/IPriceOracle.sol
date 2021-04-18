pragma solidity ^0.8;


interface IPriceOracle {

    function getASCPerUSD() external view returns (uint);

    function updateASCPerUSD(uint ASCPerUSD) external;

    function getETHPerUSD() external view returns (uint);

    function updateETHPerUSD(uint ETHPerUSD) external;
}