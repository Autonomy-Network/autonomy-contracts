pragma solidity ^0.8;


contract MockTarget {
    
    address public veriForwarderAddr;
    uint public x;
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
    
    function setAddr(address newAddr) public {
        addr = newAddr;
    }

    function setAddrPay(address newAddr) public payable {
        emit Test(msg.sender, veriForwarderAddr);
        require(msg.sender == veriForwarderAddr, "Not sent from veriForwarder");
        addr = newAddr;
    }
    event Test(address a, address b);

    // function setAddrPayVeri(address newAddr) public payable {
    //     require(msg.sender == veriForwarderAddr, "Not sent from veriForwarder");
    //     addr = newAddr;
    // }
}