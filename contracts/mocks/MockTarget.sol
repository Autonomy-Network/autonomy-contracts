pragma solidity ^0.7.0;


contract MockTarget {
    uint public x;

    function setX(uint newX) public {
        x = newX;
    }
}