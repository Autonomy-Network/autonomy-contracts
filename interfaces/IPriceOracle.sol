pragma solidity ^0.8;


interface IPriceOracle {

    function getASCPerETH() external view returns (uint);

    function updateASCPerETH(uint ASCPerETH) external;
}