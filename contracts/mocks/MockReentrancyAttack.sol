pragma solidity 0.8.6;


import "../Registry.sol";
import "../../interfaces/IRegistry.sol";


contract MockReentrancyAttack {
    Registry public reg;

    constructor(Registry registry) {
        reg = registry;
    }


    function callExecuteHashedReq(
        uint id,
        IRegistry.Request calldata r,
        uint expectedGas
    ) public {
        reg.executeHashedReq(id, r, expectedGas);
    }

    function callExecuteHashedReqUnveri(
        uint id,
        IRegistry.Request calldata r,
        bytes memory dataPrefix,
        bytes memory dataSuffix,
        uint expectedGas
    ) public {
        reg.executeHashedReqUnveri(id, r, dataPrefix, dataSuffix, expectedGas);
    }

    function callCancelHashedReq(
        uint id,
        IRegistry.Request memory r
    ) public {
        reg.cancelHashedReq(id, r);
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