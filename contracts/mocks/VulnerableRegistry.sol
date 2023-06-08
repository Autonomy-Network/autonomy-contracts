pragma solidity 0.8.6;


import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "../Registry.sol";


contract VulnerableRegistry is Registry {

    constructor(
        // IStakeManager stakeMan,
        IOracle oracle,
        IForwarder userForwarder,
        IForwarder gasForwarder,
        IForwarder userGasForwarder,
        string memory tokenName,
        string memory tokenSymbol,
        uint totalAUTOSupply
    ) Registry(
        oracle,
        userForwarder,
        gasForwarder,
        userGasForwarder
    ) {}

    function vulnerableTransfer(address payable receiver, uint amount) external {
        receiver.transfer(amount);
    }

}