pragma solidity ^0.8;


import "@openzeppelin/contracts/access/Ownable.sol";
import "../interfaces/IForwarder.sol";


contract Forwarder is IForwarder, Ownable {

    address private _reg;


    constructor() Ownable() {}


    function forward(
        address target,
        bytes calldata callData
    ) external override payable returns (bool success, bytes memory returnData) {
        require(msg.sender == _reg, "Forw: caller not the Registry");
        (success, returnData) = target.call{value: msg.value}(callData);
    }

    function getReg() external view returns (address) {
        return _reg;
    }

    function setReg(address reg) external onlyOwner {
        _reg = reg;
    }

}