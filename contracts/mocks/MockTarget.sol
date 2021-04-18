pragma solidity ^0.8;


import "./VulnerableRegistry.sol";


contract MockTarget {

    address public veriForwarderAddr;
    uint public x;
    address public userAddr;
    address public msgSender;
    VulnerableRegistry public _vulnReg;
    uint[] public gasWaster;
    address[] public gasWasterAddr;


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

    function useGasWithArray(uint num) external {
        for (uint i; i < num; i++) {
            gasWaster.push(i);
        }
    }

    function useGasWithCallData(uint[] calldata arr) external {}

    function useGasCallDataAndArray(uint[] calldata arr) external {
        for (uint i; i < arr.length; i++) {
            gasWaster.push(arr[i]);
        }
    }

    function useGasCallDataAndAddrArray(address[] calldata arr) external {
        for (uint i; i < arr.length; i++) {
            gasWasterAddr.push(arr[i]);
        }
    }

    function useGasCallDataAndSpecificAddrArray(address[] calldata arr, uint numToPush) external {
        for (uint i; i < numToPush; i++) {
            gasWasterAddr.push(arr[i]);
        }
    }

    function useGasCallDataAndAddrArrayMultiple(address[] calldata arr, uint numCycles) external {
        for (uint j; j < numCycles; j++) {
            for (uint i; i < arr.length; i++) {
                gasWasterAddr.push(arr[i]);
            }
        }
        
    }


    modifier updateMsgSender() {
        _;
        msgSender = msg.sender;
    }
}