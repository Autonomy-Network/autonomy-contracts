pragma solidity ^0.8;


import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "../StakeManager.sol";


contract VulnerableStaker is StakeManager {

    IERC20 private _ASCoin;

    constructor(IOracle oracle, IERC20 ASCoin) StakeManager(oracle, ASCoin) {
        _ASCoin = ASCoin;
    }

    function vulnerableTransfer(address receiver, uint amount) external {
        _ASCoin.transfer(receiver, amount);
    }

}