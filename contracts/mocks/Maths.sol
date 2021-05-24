pragma solidity ^0.8;


contract EVMMaths {
    function mul4Div2(uint a, uint b, uint c, uint d, uint e, uint f) external pure returns (uint) {
        return a * b * c * d / (e * f);
    }
}