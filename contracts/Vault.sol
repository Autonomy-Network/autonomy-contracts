pragma solidity ^0.8;


import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";


contract Vault is Ownable {

    IERC20 private _ASCoin;
    mapping(address => bool) private authorised;

    constructor(IERC20 ASCoin) Ownable() {
        _ASCoin = ASCoin;
    }


    function getASCoin() external view returns (IERC20) {
        return _ASCoin;
    }
    
    function getAuthorised(address addr) external view returns (bool) {
        return authorised[addr];
    }


    function setAuthorisation(address receiver, bool isAuthorised) external onlyOwner {
        authorised[receiver] = isAuthorised;
    }

    function withdrawEth() external authed returns (uint bal) {
        bal = address(this).balance;
        payable(msg.sender).transfer(bal);
    }

    function withdrawASCoin(uint amount) external authed {

    }

    modifier authed() {
        require(authorised[msg.sender], "Vault: unauthorised");
        _;
    }
    
    receive() external payable {}
}