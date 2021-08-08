pragma solidity ^0.8;


contract EVMMaths {
    function mul5div1(uint a, uint b, uint c, uint d, uint e) external pure returns (uint) {
        return a * b * c * d / e;
    }

    function mul4Div2(uint a, uint b, uint c, uint d, uint e, uint f) external pure returns (uint) {
        return a * b * c * d / (e * f);
    }

    function mul3div1(uint a, uint b, uint c, uint d) external pure returns (uint) {
        return a * b * c / d;
    }

    function getRemainder(uint a, uint b) public pure returns (uint) {
        return a % b;
    }
}