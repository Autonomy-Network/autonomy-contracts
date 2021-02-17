// pragma solidity ^0.7.0;


// import "../interfaces/IASCProxy.sol";


// contract ASCProxy is IASCProxy {
    
//     /// @dev    intentionally no fallback function so that ASCs have to send Eth
//     ///         to the registry
    
//     /// @dev Could optimise further by adding the registry address
//     /// as a constant
//     address private _owner;
    
//     constructor(address owner) payable {
//         _owner = owner;
//     }
    
//     // Roll execute and cancel into 1 because it should save on gas for deploying this contract?
//     function finish(bool shouldExecute, address target, uint callGas, bytes calldata callData) external override returns (bool success) {
//         // A message would be nice for when this fails, but 
//         // it would increase the cost of creating an ASC
//         require(msg.sender == _owner);
//         if (shouldExecute) {
//             (success, ) = target.call{gas: callGas}(callData); 
//         }
//         selfdestruct(payable(msg.sender));
//     }
// }
