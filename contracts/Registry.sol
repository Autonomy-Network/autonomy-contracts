pragma solidity ^0.7.0;
pragma abicoder v2;


import "OpenZeppelin/openzeppelin-contracts@3.3.0-solc-0.7/contracts/token/ERC20/IERC20.sol";
import "../interfaces/IStakeManager.sol";
import "./ASCProxy.sol";
import "./abstract/Shared.sol";


contract Registry is Shared {
    
    // Constant public
    IERC20 public constant ASCoin = IERC20(0x31E31e3703D367014BA5802B7C5E41d96E331723);
    uint public constant EXEC_GAS_OVERHEAD_NO_REF = 40000;
    uint public constant EXEC_GAS_OVERHEAD_REF = 60000;
    uint public constant ETH_BOUNTY = 10**15;

    // Constant private
    bytes private constant _EMPTY_BYTES = "";
    uint private constant _ETH_REF_BOUNTY = ETH_BOUNTY * 7 / 10;
    uint private constant _ETH_REF_REWARD = ETH_BOUNTY - _ETH_REF_BOUNTY;
    
    address private _owner;
    uint private _numRequests;
    mapping(uint => Request) private _idToRequest;
    uint private _maxRewardPerASC;
    IStakeManager private _stakeMan;
    
    
    struct Request {
        address payable requester;
        address target;
        ASCProxy proxy;
        address payable referer;
        bytes callData;
    }

    
    event RequestAdded(uint indexed id);
    event RequestRemoved(uint indexed id, bool wasExecuted);


    constructor(IStakeManager staker, uint maxRewardPerASC) {
        _owner = msg.sender;
        _stakeMan = staker;
        _maxRewardPerASC = maxRewardPerASC;
    }
    
    
    // ----------- Getters -----------
    
    function getOwner() external view returns (address) {
        return _owner;
    }
    
    function getNumRequests() external view returns (uint) {
        return _numRequests;
    }
    
    function getRequest(uint id) external view returns (Request memory) {
        return _idToRequest[id];
    }
    
    function getMaxRewardPerASC() external view returns (uint) {
        return _maxRewardPerASC;
    }
    
    function getStakeManager() external view returns (address) {
        return address(_stakeMan);
    }
    
    
    // ----------- Requests -----------
    
    function newRequest(address target, bytes calldata callData, address payable referer) external payable {
        require(target != address(this), "Registry: nice try ;)");
        require(target != _ADDR_0, "Registry: need a target contract");
        require(callData.length > 0, "Registry: need calldata");
        
        ASCProxy proxy = new ASCProxy{value: msg.value}(address(this));
        _idToRequest[_numRequests] = Request(payable(msg.sender), target, proxy, referer, callData);
        emit RequestAdded(_numRequests);
        _numRequests++;
    }
    
    function execute(uint id, uint callGas) external {
        uint startGas = gasleft();
        Request memory r = _idToRequest[id];
        require(_stakeMan.isCurExec(msg.sender), "Registry:not executor or expired");
        require(r.requester != _ADDR_0, "Registry: request doesn't exists");
        
        // Technically we shouldn't need to do this accounting, we should
        // just be able to refund the balance of this contract since the only
        // time it should have a non-zero balance is after a refund or execution,
        // but better to be explicit
        uint ethBalBefore = address(this).balance;
        
        require(r.proxy.finish(true, r.target, callGas, r.callData), "Registry: call failed");
        delete _idToRequest[id];
        emit RequestRemoved(id, true);
        
        uint gasUsed = startGas - gasleft();
        
        if (r.referer != _ADDR_0) {
            gasUsed += EXEC_GAS_OVERHEAD_REF;
        } else {
            gasUsed += EXEC_GAS_OVERHEAD_NO_REF;
        }
        
        uint ethSpent = gasUsed * tx.gasprice;
        uint ethNeeded = ethSpent + ETH_BOUNTY;
        uint ethReceived = address(this).balance - ethBalBefore;
        require(ethReceived >= ethNeeded, "Registry: not enough eth sent");
        // Refund excess
        r.requester.transfer(ethReceived - ethNeeded);
        
        if (r.referer != _ADDR_0) {
            payable(msg.sender).transfer(_ETH_REF_BOUNTY);
            r.referer.transfer(_ETH_REF_REWARD);
        } else {
            payable(msg.sender).transfer(ETH_BOUNTY);
        }
        
        // Send ASCoin rewards
        _rewardASC(r.requester);
    }
    
    function _rewardASC(address receiver) private {
        if (ASCoin.balanceOf(address(this)) > _maxRewardPerASC) {
            ASCoin.transfer(receiver, _maxRewardPerASC);
        }
    }
    
    function cancel(uint id) external {
        Request memory r = _idToRequest[id];
        require(msg.sender == r.requester, "Registry: not the requester");
        
        // Technically we shouldn't need to do this accounting, we should
        // just be able to refund the balance of this contract since the only
        // time it should have a non-zero balance is after a refund or execution,
        // but better to be explicit
        uint ethBalBefore = address(this).balance;
        
        // Cancel the request
        r.proxy.finish(false, _ADDR_0, 0, _EMPTY_BYTES);
        delete _idToRequest[id];
        emit RequestRemoved(id, false);
        
        // Send refund
        uint refundAmount = address(this).balance - ethBalBefore;
        if (refundAmount > 0) {
            r.requester.transfer(refundAmount);
        }
    }
    
    // Payment should be received by this method when a user has a way of 
    // obtaining Eth within the ASC call, e.g. for trading related activity etc
    receive() external payable {}
}
