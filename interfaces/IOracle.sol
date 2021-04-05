pragma solidity ^0.8;


interface IOracle {
    // Needs to output the same number for the whole epoch
    function getRandNum(uint salt) external returns (uint);

    function getASCPerETH() external view returns (uint);

    function updateASCPerETH(uint ASCPerETH) external;
}