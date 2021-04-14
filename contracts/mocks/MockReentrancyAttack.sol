pragma solidity ^0.8;


import "../Registry.sol";
import "../../interfaces/IRegistry.sol";


contract MockReentrancyAttack {
    Registry public reg;

    constructor(Registry registry) {
        reg = registry;
    }

    function callExecuteRawReq(uint id) public {
        reg.executeRawReq(id);
    }

    function callExecuteHashedReq(
        uint id,
        IRegistry.Request calldata r,
        bytes memory dataPrefix,
        bytes memory dataSuffix
    ) public {
        reg.executeHashedReq(id, r, dataPrefix, dataSuffix);
    }

    function callExecuteHashedReqUnveri(
        uint id,
        IRegistry.Request calldata r,
        bytes memory dataPrefix,
        bytes memory dataSuffix
    ) public {
        reg.executeHashedReqUnveri(id, r, dataPrefix, dataSuffix);
    }

    function callCancelRawReq(uint id) public {
        reg.cancelRawReq(id);
    }

    function callCancelHashedReq(
        uint id,
        IRegistry.Request memory r,
        bytes memory dataPrefix,
        bytes memory dataSuffix
    ) public {
        reg.cancelHashedReq(id, r, dataPrefix, dataSuffix);
    }

    function callCancelHashedReqUnveri(
        uint id,
        IRegistry.Request memory r,
        bytes memory dataPrefix,
        bytes memory dataSuffix
    ) public {
        reg.cancelHashedReqUnveri(id, r, dataPrefix, dataSuffix);
    }
}