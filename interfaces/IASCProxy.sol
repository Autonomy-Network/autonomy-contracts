pragma solidity ^0.8;


interface IASCProxy {
    function finish(bool shouldExecute, address target, uint gasAmount, bytes calldata data) external returns (bool success);
}
