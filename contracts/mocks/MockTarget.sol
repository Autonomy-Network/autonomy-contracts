pragma solidity ^0.8;


import "./VulnerableRegistry.sol";


contract MockTarget {

    address public veriForwarderAddr;
    uint public x;
    address public userAddr;
    address public msgSender;
    VulnerableRegistry public _vulnReg;


    constructor(address newVeriForwarderAddr, VulnerableRegistry vulnReg) {
        veriForwarderAddr = newVeriForwarderAddr;
        _vulnReg = vulnReg;
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

    function callVulnerableTransfer(address payable receiver, uint amount) external payable {
        _vulnReg.vulnerableTransfer(receiver, amount);
    }


    modifier updateMsgSender() {
        _;
        msgSender = msg.sender;
    }
}