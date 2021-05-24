pragma solidity ^0.8;


interface IPriceOracle {

    function getAUTOPerETH() external view returns (uint);

    function getGasPriceFast() external view returns (uint);
}