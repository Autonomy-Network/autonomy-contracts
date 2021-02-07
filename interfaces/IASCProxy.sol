pragma solidity ^0.7.0;


interface IASCProxy {
    function finish(bool shouldExecute, address target, uint gasAmount, bytes calldata data) external returns (bool success);
}
