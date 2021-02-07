pragma solidity ^0.7.0;
pragma abicoder v2;


import "OpenZeppelin/openzeppelin-contracts@3.3.0-solc-0.7/contracts/token/ERC20/IERC20.sol";
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