pragma solidity ^0.8;


contract MockTarget {
    
    address public veriForwarderAddr;
    address public unveriForwarderAddr;
    uint public x;
    address public userAddr;
    address public msgSender;


    constructor(address newVeriForwarderAddr, address newUnveriForwarderAddr) {
        veriForwarderAddr = newVeriForwarderAddr;
        unveriForwarderAddr = newUnveriForwarderAddr;
    }


    function setX(uint newX) public onlyUnverifiedSender updateMsgSender {
        x = newX;
    }

    function setXPay(uint newX) public payable onlyUnverifiedSender updateMsgSender {
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

    modifier onlyUnverifiedSender() {
        require(msg.sender == unveriForwarderAddr, "Not sent from unveriForwarder");
        _;
    }
}