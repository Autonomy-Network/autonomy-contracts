pragma solidity ^0.7.0;


import "../Registry.sol";


contract MockReentrancyAttack {
    Registry public reg;

    constructor(Registry registry) {
        reg = registry;
    }

    function callExecute(uint id) public {
        reg.executeRawReq(id);
    }

    function callCancel(uint id) public {
        reg.cancelRawReq(id);
    }
}