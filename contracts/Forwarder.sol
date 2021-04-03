pragma solidity ^0.7.0;
pragma abicoder v2;


contract Forwarder {

    function forward(
        address target,
        uint ethForCall,
        bytes calldata callData
    ) external payable returns (bool success, bytes memory returnData) {
        (success, returnData) = target.call{value: ethForCall}(callData); 
    }

}