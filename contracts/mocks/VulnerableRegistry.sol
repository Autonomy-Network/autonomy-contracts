pragma solidity ^0.8;


import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "../Registry.sol";


contract VulnerableRegistry is Registry {

    constructor(
        IERC20 AUTO,
        IStakeManager staker,
        IOracle oracle,
        IForwarder veriForwarder
    ) Registry(AUTO, staker, oracle, veriForwarder) {}

    function vulnerableTransfer(address payable receiver, uint amount) external {
        receiver.transfer(amount);
    }

}