pragma solidity ^0.7.0;
pragma abicoder v2;


import "OpenZeppelin/openzeppelin-contracts@3.3.0-solc-0.7/contracts/token/ERC20/IERC20.sol";
import "OpenZeppelin/openzeppelin-contracts@3.3.0-solc-0.7/contracts/access/Ownable.sol";
import "OpenZeppelin/openzeppelin-contracts@3.3.0-solc-0.7/contracts/utils/ReentrancyGuard.sol";
import "../interfaces/IStakeManager.sol";
// import "./ASCProxy.sol";
import "./Vault.sol";
import "./abstract/Shared.sol";


contract Registry is Shared, Ownable, ReentrancyGuard {
    
    // Constant public
    // uint public constant EXEC_GAS_OVERHEAD_NO_REF = 40000;
    // uint public constant EXEC_GAS_OVERHEAD_REF = 60000;
    uint public constant GAS_OVERHEAD_ETH = 10000;
    uint public constant GAS_OVERHEAD_ASCOIN = 20000;
    uint private constant _NET_GAS_REFUND = 10000;

    // Constant private
    bytes private constant _EMPTY_BYTES = "";
    // uint private constant _ETH_REF_BOUNTY = ETH_BOUNTY * 7 / 10;
    // uint private constant _ETH_REF_REWARD = ETH_BOUNTY - _ETH_REF_BOUNTY;
    
    IERC20 private _ASCoin;
    IStakeManager private _stakeMan;
    Vault private _vault;
    // uint private _numRequests;
    // mapping(uint => Request) private _idToRequest;
    Request[] private _requests;
    // The minimum bounty priced in Eth. This amount is converted
    // directly to the equivalent value in ASCoin if the requester wants
    // to pay with ASCoin, and is doubled if they want to pay in Eth
    uint private _baseBountyAsEth;
    uint private _requesterReward;
    uint private _executorReward;
    // The amount of ASCoin that 1 Eth is worth, scaled to 1E18 as 1:1
    uint private _ethToASCoinRate;
    mapping(address => uint) private _cumulRewards;
    
    
    struct Request {
        address payable requester;
        address target;
        bytes callData;
        bool payWithASCoin;
        uint initEthSent;
        uint ethForCall;
        address payable referer;
        // ASCProxy proxy;
    }

    
    event RequestAdded(uint indexed id);
    event RequestRemoved(uint indexed id, bool wasExecuted);


    constructor(
        IERC20 ASCoin,
        IStakeManager staker,
        Vault vault,
        uint baseBountyAsEth,
        uint requesterReward,
        uint executorReward,
        uint ethToASCoinRate
    ) Ownable() ReentrancyGuard() {
        _ASCoin = ASCoin;
        _stakeMan = staker;
        _baseBountyAsEth = baseBountyAsEth;
        _requesterReward = requesterReward;
        _executorReward = executorReward;
        _ethToASCoinRate = ethToASCoinRate;
        _vault = vault;
    }

    // setRewards
    
    
    
    // ----------- Requests -----------
    
    function newRequest(
        address target,
        bytes calldata callData,
        bool payWithASCoin,
        uint ethForCall,
        address payable referer
    ) external payable nonReentrant nzAddr(target) targetNotThis(target) nzBytes(callData) {
        _newRequest(target, callData, payWithASCoin, msg.value, ethForCall, referer);
    }

    // function newHashedRequestNoEth

    // function newBatchRequestNoEth

    // function newHashedRequestWithEth

    // function newBatchRequestWithEth

    function _newRequest(
        address target,
        bytes calldata callData,
        bool payWithASCoin,
        uint initEthSent,
        uint ethForCall,
        address payable referer
    ) private {
        emit RequestAdded(_requests.length);
        _requests.push(Request(payable(msg.sender), target, callData, payWithASCoin, initEthSent, ethForCall, referer));
    }

    event Test(uint a, uint b, uint c);

    function execute(uint id) external nonReentrant returns (uint) {
        uint startGas = gasleft();
        Request memory r = _requests[id];
        require(r.requester != _ADDR_0, "Registry: request doesn't exists");
        require(_stakeMan.isCurExec(msg.sender), "Registry:not executor or expired");
        
        // Make the call that the user requested
        // require(r.proxy.finish(true, r.target, callGas, r.callData), "Registry: call failed");
        (bool success, ) = r.target.call{value: r.ethForCall}(r.callData); 
        require(success, "Registry: call failed");
        
        // Store ASCoin rewards
        // It's cheaper to store the cumulative rewards than it is to send
        // an ASCoin transfer directly since the former changes 1 storage
        // slot whereas the latter changes 2. The rewards are actually stored
        // in a different contract that reads the reward storage of this contract
        // because of the danger of someone using call to call to ASCoin and transfer
        // out tokens. It could be prevented by preventing r.target being set to ASCoin,
        // but it's better to be paranoid and totally separate the contracts.
        // Need to include these storages in the gas cost that the user pays since
        // they benefit from part of it and the costs can vary depending on whether
        // the amounts changed were 0 or non-0
        _cumulRewards[r.requester] += _requesterReward;
        _cumulRewards[msg.sender] += _executorReward;
        if (r.referer != _ADDR_0) {
            _cumulRewards[r.referer] += _requesterReward;
        }

        emit RequestRemoved(id, true);
        delete _requests[id];

        // +1 since it never divides exactly because of the 4 bytes of methodID
        uint numStorageRefunds = (r.callData.length / 32) + 1;
        numStorageRefunds += r.referer == _ADDR_0 ? 5 : 6;
        
        uint gasUsed = 21512 + (numStorageRefunds * 5000) + startGas - gasleft();

        uint gasRefunded = numStorageRefunds * 15000;

        emit Test(startGas, gasleft(), gasUsed);
        uint ethNeeded;

        if (r.payWithASCoin) {
            gasUsed += GAS_OVERHEAD_ASCOIN;
            if (gasRefunded > gasUsed / 2) {
                gasUsed = gasUsed / 2;
            } else {
                gasUsed -= gasRefunded;
            }
            // gasUsed = gasUsed * 11 / 10;

            ethNeeded = (gasUsed * tx.gasprice) + _baseBountyAsEth;
            uint ASCoinNeeded = ethNeeded * _ethToASCoinRate / _E_18;

            // Send the executor their bounty
            emit Test(_ASCoin.balanceOf(r.requester), _ASCoin.balanceOf(msg.sender), ASCoinNeeded);
            _ASCoin.transferFrom(r.requester, msg.sender, ASCoinNeeded);
        } else {
            gasUsed += GAS_OVERHEAD_ETH;
            if (gasRefunded > gasUsed / 2) {
                gasUsed = gasUsed / 2;
            } else {
                gasUsed -= gasRefunded;
            }
            // gasUsed = gasUsed * 11 / 10;

            ethNeeded = (gasUsed * tx.gasprice) + (2 * _baseBountyAsEth);
            // uint ethReceived = _vault.withdrawEth() + r.initEthSent - r.ethForCall;
            uint ethReceived = r.initEthSent - r.ethForCall;

            // Send the executor their bounty
            require(ethReceived >= ethNeeded, "Registry: not enough eth sent");
            payable(msg.sender).transfer(ethNeeded);

            // Refund excess to the requester
            uint excess = ethReceived - ethNeeded;
            if (excess > 0) {
                r.requester.transfer(excess);
            }
        }

        return gasUsed;
    }
    
    function cancel(uint id) external nonReentrant {
        Request memory r = _requests[id];
        require(msg.sender == r.requester, "Registry: not the requester");
        
        // Cancel the request
        delete _requests[id];
        emit RequestRemoved(id, false);
        
        // Send refund
        if (r.initEthSent > 0) {
            r.requester.transfer(r.initEthSent);
        }
    }
    
    
    // ----------- Setters -----------

    function setBaseBountyAsEth(uint newBaseBountyAsEth) external nonReentrant returns (uint) {
        _baseBountyAsEth = newBaseBountyAsEth;
    }
    
    function setRequesterReward(uint newRequesterReward) external nonReentrant returns (uint) {
        _requesterReward = newRequesterReward;
    }
    
    function setExecutorReward(uint newEexecutorReward) external nonReentrant returns (uint) {
        _executorReward = newEexecutorReward;
    }
    
    function setEthToASCoinRate(uint newEthToASCoinRate) external nonReentrant returns (uint) {
        _ethToASCoinRate = newEthToASCoinRate;
    }


    // ----------- Getters -----------
    
    function getASCoin() external view returns (IERC20) {
        return _ASCoin;
    }
    
    function getStakeManager() external view returns (address) {
        return address(_stakeMan);
    }

    function getRequests() external view returns (Request[] memory) {
        return _requests;
    }

    function getRequestsLength() external view returns (uint) {
        return _requests.length;
    }
    
    function getRequest(uint id) external view returns (Request memory) {
        return _requests[id];
    }
    
    function getBaseBountyAsEth() external view returns (uint) {
        return _baseBountyAsEth;
    }
    
    function getRequesterReward() external view returns (uint) {
        return _requesterReward;
    }
    
    function getExecutorReward() external view returns (uint) {
        return _executorReward;
    }
    
    function getEthToASCoinRate() external view returns (uint) {
        return _ethToASCoinRate;
    }
    
    function getCumulRewardsOf(address addr) external view returns (uint) {
        return _cumulRewards[addr];
    }

    function divAOverB(uint a, uint b) external view returns (uint) {
        return a / b;
    }

    modifier targetNotThis(address target) {
        require(target != address(this) && target != address(_ASCoin), "Registry: nice try ;)");
        _;
    }
    
    receive() external payable {}
}
