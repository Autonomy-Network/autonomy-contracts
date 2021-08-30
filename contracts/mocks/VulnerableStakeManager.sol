pragma solidity 0.8.6;


import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "../StakeManager.sol";


contract VulnerableStaker is StakeManager {

    IERC20 private _AUTO;

    constructor(IOracle oracle, IERC20 AUTO) StakeManager(oracle) {
        _AUTO = AUTO;
    }

    function vulnerableTransfer(address receiver, uint amount) external {
        _AUTO.transfer(receiver, amount);
    }

}