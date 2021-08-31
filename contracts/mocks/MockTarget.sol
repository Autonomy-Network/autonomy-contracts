pragma solidity 0.8.6;


import "../../interfaces/IRegistry.sol";
import "./VulnerableRegistry.sol";


contract MockTarget {

    address public userForwarderAddr;
    address public gasForwarderAddr;
    address public userGasForwarderAddr;
    uint public x;
    address public userAddr;
    address public msgSender;
    IRegistry public reg;
    VulnerableRegistry public vulnReg;
    uint[] public gasWaster;
    address[] public gasWasterAddr;


    constructor(
        address userForwarderAddr_,
        address gasForwarderAddr_,
        address userGasForwarderAddr_,
        IRegistry reg_,
        VulnerableRegistry vulnReg_
    ) {
        userForwarderAddr = userForwarderAddr_;
        gasForwarderAddr = gasForwarderAddr_;
        userGasForwarderAddr = userGasForwarderAddr_;
        reg = reg_;
        vulnReg = vulnReg_;
    }

    function setX(uint newX) public updateMsgSender {
        x = newX;
    }

    function setXAddr(address newUserAddr, uint newX) public updateMsgSender {
        userAddr = newUserAddr;
        x = newX;
    }

    function setXAddrUserFeeVeri(address newUserAddr, uint newX) public updateMsgSender userFeeVeri {
        userAddr = newUserAddr;
        x = newX;
    }

    function setXAddrWithArr(address newUserAddr, uint newX, uint[] memory arr) public updateMsgSender {
        userAddr = newUserAddr;
        x = newX;
    }

    function setXPay(uint newX) public payable updateMsgSender {
        x = newX;
    }

    function setAddrPayUserVerified(address newUserAddr) public payable updateMsgSender userVeri {
        userAddr = newUserAddr;
    }

    function setAddrPayFeeVerified(address newUserAddr) public payable updateMsgSender feeVeri {
        userAddr = newUserAddr;
    }

    function setXPayFeeVerified(uint newX) public payable updateMsgSender feeVeri {
        x = newX;
    }

    function setAddrXPayUserFeeVerified(address newUserAddr, uint newX) public payable updateMsgSender userFeeVeri {
        userAddr = newUserAddr;
        x = newX;
    }

    function setAddrXPayUserFeeVerifiedSendEth(address newUserAddr, uint newX) public payable updateMsgSender userFeeVeri {
        userAddr = newUserAddr;
        x = newX;
        payable(address(reg)).transfer(newX);
    }

    function callVulnerableTransfer(address payable receiver, uint amount) external payable {
        vulnReg.vulnerableTransfer(receiver, amount);
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
    function useGasWithArrayVeri(address user, uint num) external userVeri {
        for (uint i; i < num; i++) {
            gasWaster.push(i);
        }
    }

    /// @dev    See how gas measurement accuracy changes as both calldata size increases and the
    ///         gas of the actual call increase at a consistent rate
    function useGasWithCallDataVeri(address user, uint[] calldata arr) external userVeri {}

    /// @dev    See how gas measurement accuracy changes as calldata size increases and the
    ///         gas of the actual call doesn't change
    function useGasCallDataAndArrayVeri(address user, uint[] calldata arr) external userVeri {
        for (uint i; i < arr.length; i++) {
            gasWaster.push(arr[i]);
        }
    }

    /// @dev    See how gas measurement accuracy changes as both calldata size increases and the
    ///         gas of the actual call increase at a consistent rate, using addresses instead
    function useGasCallDataAndAddrArrayVeri(address user, address[] calldata arr) external userVeri {
        for (uint i; i < arr.length; i++) {
            gasWasterAddr.push(arr[i]);
        }
    }

    /// @dev    See how gas measurement accuracy changes as the calldata is large and the gas of the
    ///         actual call increases, but the overall gas of the former is greater than the latter
    function useGasCallDataAndSpecificAddrArrayVeri(address user, address[] calldata arr, uint numToPush) external userVeri {
        for (uint i; i < numToPush; i++) {
            gasWasterAddr.push(arr[i]);
        }
    }

    /// @dev    See how gas measurement accuracy changes as the calldata is large and the gas of the
    ///         actual call increases, but the overall gas of the former is lesser than the latter
    function useGasCallDataAndAddrArrayMultipleVeri(address user, address[] calldata arr, uint numCycles) external userVeri {
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

    function getGasWaster() external view returns (uint[] memory) {
        return gasWaster;
    }


    modifier updateMsgSender() {
        _;
        msgSender = msg.sender;
    }

    modifier userVeri() {
        require(msg.sender == userForwarderAddr, "Not sent from userForwarder");
        _;
    }

    modifier feeVeri() {
        require(msg.sender == gasForwarderAddr, "Not sent from feeForwarder");
        _;
    }

    modifier userFeeVeri() {
        require(msg.sender == userGasForwarderAddr, "Not sent from userFeeForwarder");
        _;
    }

    receive() external payable {}
}