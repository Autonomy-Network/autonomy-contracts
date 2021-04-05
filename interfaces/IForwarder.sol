pragma solidity ^0.8;


interface IForwarder {

    function forward(
        address target,
        bytes calldata callData
    ) external payable returns (bool success, bytes memory returnData);

}