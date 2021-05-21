pragma solidity ^0.8;


import "../../interfaces/mocks/IUniswapV2Router02.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";


contract MockUniLimit {

    IUniswapV2Router02 public constant uni = IUniswapV2Router02(0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D);
    address public autonomyVF;


    constructor(address autonomyVF_) {
        autonomyVF = autonomyVF_;
    }

    function ethToTokenLimitOrder(
        address sender,
        uint amountOutMin,
        address[] calldata path,
        address to,
        uint deadline
    ) external payable onlyAutonomy {
        uni.swapExactETHForTokens{value: msg.value}(amountOutMin, path, to, deadline);
    }

    function tokenToEthLimitOrder(
        address payable sender,
        uint inputAmount,
        uint amountOutMin,
        address[] calldata path,
        address to,
        uint deadline
    ) external onlyAutonomy {
        IERC20 token = IERC20(path[0]);
        token.transferFrom(sender, address(this), inputAmount);
        if (token.allowance(address(this), address(uni)) < inputAmount) {
            token.approve(address(uni), 2**255);
        }
        uni.swapExactTokensForETH(inputAmount, amountOutMin, path, to, deadline);
    }

    modifier onlyAutonomy() {
        require(msg.sender == autonomyVF, "Only Autonomy. Nice try");
        _;
    }

}