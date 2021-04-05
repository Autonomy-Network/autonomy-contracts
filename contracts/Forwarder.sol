pragma solidity ^0.8;


import "../interfaces/IForwarder.sol";


contract Forwarder is IForwarder {

    address private _reg;

    constructor(address reg) {
        _reg = reg;
    }

    function forward(
        address target,
        bytes calldata callData
    ) external override payable returns (bool success, bytes memory returnData) {
        require(msg.sender == _reg, "Caller not the Registry");
        (success, returnData) = target.call{value: msg.value}(callData);
    }

}