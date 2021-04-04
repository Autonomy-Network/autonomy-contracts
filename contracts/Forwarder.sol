pragma solidity ^0.8;


contract Forwarder {

    function forward(
        address target,
        bytes calldata callData
    ) external payable returns (bool success, bytes memory returnData) {
        (success, returnData) = target.call{value: msg.value}(callData);
    }

}