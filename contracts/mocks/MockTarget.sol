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

    function setAddrPayVerified(address newUserAddr) public payable updateMsgSender veri {
        userAddr = newUserAddr;
    }

    function callVulnerableTransfer(address payable receiver, uint amount) external payable {
        _vulnReg.vulnerableTransfer(receiver, amount);
    }

    /// @dev    See how gas measurement accuracy changes as calldata size doesn't change and the
    ///         gas of the actual call increases
    function useGasWithArray(uint num) external {
        for (uint i; i < num; i++) {
            gasWaster.push(i);
        }
    }

    /// @dev    See how gas measurement accuracy changes as both calldata size increases and the
    ///         gas of the actual call increase at a consistent rate
    function useGasWithCallData(uint[] calldata arr) external {}

    /// @dev    See how gas measurement accuracy changes as calldata size increases and the
    ///         gas of the actual call doesn't change
    function useGasCallDataAndArray(uint[] calldata arr) external {
        for (uint i; i < arr.length; i++) {
            gasWaster.push(arr[i]);
        }
    }

    /// @dev    See how gas measurement accuracy changes as both calldata size increases and the
    ///         gas of the actual call increase at a consistent rate, using addresses instead
    function useGasCallDataAndAddrArray(address[] calldata arr) external {
        for (uint i; i < arr.length; i++) {
            gasWasterAddr.push(arr[i]);
        }
    }

    /// @dev    See how gas measurement accuracy changes as the calldata is large and the gas of the
    ///         actual call increases, but the overall gas of the former is greater than the latter
    function useGasCallDataAndSpecificAddrArray(address[] calldata arr, uint numToPush) external {
        for (uint i; i < numToPush; i++) {
            gasWasterAddr.push(arr[i]);
        }
    }

    /// @dev    See how gas measurement accuracy changes as the calldata is large and the gas of the
    ///         actual call increases, but the overall gas of the former is lesser than the latter
    function useGasCallDataAndAddrArrayMultiple(address[] calldata arr, uint numCycles) external {
        for (uint j; j < numCycles; j++) {
            for (uint i; i < arr.length; i++) {
                gasWasterAddr.push(arr[i]);
            }
        }
    }

    /// @dev    See how gas measurement accuracy changes as calldata size doesn't change and the
    ///         gas of the actual call increases
    function useGasWithArrayVeri(address user, uint num) external veri {
        for (uint i; i < num; i++) {
            gasWaster.push(i);
        }
    }

    /// @dev    See how gas measurement accuracy changes as both calldata size increases and the
    ///         gas of the actual call increase at a consistent rate
    function useGasWithCallDataVeri(address user, uint[] calldata arr) external veri {}

    /// @dev    See how gas measurement accuracy changes as calldata size increases and the
    ///         gas of the actual call doesn't change
    function useGasCallDataAndArrayVeri(address user, uint[] calldata arr) external veri {
        for (uint i; i < arr.length; i++) {
            gasWaster.push(arr[i]);
        }
    }

    /// @dev    See how gas measurement accuracy changes as both calldata size increases and the
    ///         gas of the actual call increase at a consistent rate, using addresses instead
    function useGasCallDataAndAddrArrayVeri(address user, address[] calldata arr) external veri {
        for (uint i; i < arr.length; i++) {
            gasWasterAddr.push(arr[i]);
        }
    }

    /// @dev    See how gas measurement accuracy changes as the calldata is large and the gas of the
    ///         actual call increases, but the overall gas of the former is greater than the latter
    function useGasCallDataAndSpecificAddrArrayVeri(address user, address[] calldata arr, uint numToPush) external veri {
        for (uint i; i < numToPush; i++) {
            gasWasterAddr.push(arr[i]);
        }
    }

    /// @dev    See how gas measurement accuracy changes as the calldata is large and the gas of the
    ///         actual call increases, but the overall gas of the former is lesser than the latter
    function useGasCallDataAndAddrArrayMultipleVeri(address user, address[] calldata arr, uint numCycles) external veri {
        for (uint j; j < numCycles; j++) {
            for (uint i; i < arr.length; i++) {
                gasWasterAddr.push(arr[i]);
            }
        }
    }

    function revertWithMessage() external {
        require(false, "You dun goofed boy");
    }

    function revertWithoutMessage() external {
        require(false);
    }


    modifier updateMsgSender() {
        _;
        msgSender = msg.sender;
    }

    modifier veri() {
        require(msg.sender == veriForwarderAddr, "Not sent from veriForwarder");
        _;
    }
}