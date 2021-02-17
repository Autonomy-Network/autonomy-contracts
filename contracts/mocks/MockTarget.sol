pragma solidity ^0.7.0;


contract MockTarget {
    uint public x;
    bytes public y;

    function setX(uint newX) public {
        x = newX;
    }

    function setXPay(uint newX) public payable {
        x = newX;
    }

    function setY(bytes calldata newY) public {
        y = newY;
    }
}