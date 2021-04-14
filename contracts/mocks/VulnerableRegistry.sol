pragma solidity ^0.8;


import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "../Registry.sol";


contract VulnerableRegistry is Registry {

    constructor(
        IERC20 ASCoin,
        IStakeManager staker,
        IOracle oracle,
        IForwarder veriForwarder
    ) Registry(ASCoin, staker, oracle, veriForwarder) {}

    function vulnerableTransfer(address payable receiver, uint amount) external {
        receiver.transfer(amount);
    }

}