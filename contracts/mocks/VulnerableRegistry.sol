pragma solidity 0.8.6;


import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "../Registry.sol";


contract VulnerableRegistry is Registry {

    function vulnerableTransfer(address payable receiver, uint amount) external {
        receiver.transfer(amount);
    }

}