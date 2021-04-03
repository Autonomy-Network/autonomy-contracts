pragma solidity ^0.7.0;


contract MockTarget {
    
    address public veriForwarderAddr;
    uint public x;
    // bytes public y;
    address public addr;


    constructor(address newVeriForwarderAddr) {
        veriForwarderAddr = newVeriForwarderAddr;
    }


    function setX(uint newX) public {
        x = newX;
    }

    function setXPay(uint newX) public payable {
        x = newX;
    }

    // function setY(bytes calldata newY) public {
    //     y = newY;
    // }

    function setAddr(address newAddr) public {
        addr = newAddr;
    }

    function setAddrPay(address newAddr) public payable {
        addr = newAddr;
    }

    function setAddrPayVeri(address newAddr) public payable {
        require(msg.sender == veriForwarderAddr, "Not sent from veriForwarder");
        addr = newAddr;
    }
}