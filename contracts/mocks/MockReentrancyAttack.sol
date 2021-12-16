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

    function callCancelHashedReq(
        uint id,
        IRegistry.Request memory r
    ) public {
        reg.cancelHashedReq(id, r);
    }
}