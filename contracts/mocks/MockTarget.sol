pragma solidity ^0.8;


contract MockTarget {

    address public veriForwarderAddr;
    uint public x;
    address public userAddr;
    address public msgSender;


    constructor(address newVeriForwarderAddr) {
        veriForwarderAddr = newVeriForwarderAddr;
    }


    function setX(uint newX) public updateMsgSender {
        x = newX;
    }

    function setXPay(uint newX) public payable updateMsgSender {
        x = newX;
    }
    
    function setAddrPayVerified(address newUserAddr) public payable updateMsgSender {
        require(msg.sender == veriForwarderAddr, "Not sent from veriForwarder");
        userAddr = newUserAddr;
    }


    modifier updateMsgSender() {
        _;
        msgSender = msg.sender;
    }
}