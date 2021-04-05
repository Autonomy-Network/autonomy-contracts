pragma solidity ^0.8;


import "@openzeppelin/contracts/access/Ownable.sol";
import "../interfaces/IForwarder.sol";


contract Forwarder is IForwarder, Ownable {

    address private _reg;


    constructor() Ownable() {}


    event Test(address a, address b);
    function forward(
        address target,
        bytes calldata callData
    ) external override payable returns (bool success, bytes memory returnData) {
        emit Test(msg.sender, _reg);
        require(msg.sender == _reg, "Caller not the Registry");
        (success, returnData) = target.call{value: msg.value}(callData);
    }

    function getReg() external returns (address) {
        return _reg;
    }

    function setReg(address reg) external onlyOwner {
        _reg = reg;
    }

}