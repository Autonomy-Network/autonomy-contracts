pragma solidity ^0.7.0;
pragma abicoder v2;


import "OpenZeppelin/openzeppelin-contracts@3.3.0-solc-0.7/contracts/token/ERC20/IERC20.sol";
import "OpenZeppelin/openzeppelin-contracts@3.3.0-solc-0.7/contracts/utils/ReentrancyGuard.sol";
import "../interfaces/IStakeManager.sol";
// import "./ASCProxy.sol";
import "./Vault.sol";
import "./abstract/Shared.sol";


contract Registry is Shared, ReentrancyGuard {
    
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
    Request[] private _rawRequests;
    // We need to have 2 separete arrays for adding requests with and without
    // eth because, when comparing the hash of a request to be executed to the
    // stored hash, we have no idea what the request had for the eth values
    // that was originally stored as a hash and therefore would need to store
    // an extra bool saying where eth was sent with the new request. Instead, 
    // that can be known implicitly by having 2 separate arrays.
    bytes32[] private _hashedIpfsReqsEth;
    bytes32[] private _hashedIpfsReqsNoEth;
    // bytes32[] private _hashReqsPayEth;
    // bytes32[] private _hashReqsPayASC;
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
        bool payWithASC;
        uint initEthSent;
        uint ethForCall;
        address payable referer;
    }

    enum ReqType {
        Raw,
        HashEth,
        HashNoEth
    }

    
    event RawReqAdded(uint indexed id);
    event RawReqRemoved(uint indexed id, bool wasExecuted);
    event HashedReqEthAdded(uint indexed id);
    event HashedReqEthRemoved(uint indexed id, bool wasExecuted);
    event HashedReqNoEthAdded(uint indexed id);
    event HashedReqNoEthRemoved(uint indexed id, bool wasExecuted);


    constructor(
        IERC20 ASCoin,
        IStakeManager staker,
        Vault vault,
        uint baseBountyAsEth,
        uint requesterReward,
        uint executorReward,
        uint ethToASCoinRate
    ) ReentrancyGuard() {
        _ASCoin = ASCoin;
        _stakeMan = staker;
        _baseBountyAsEth = baseBountyAsEth;
        _requesterReward = requesterReward;
        _executorReward = executorReward;
        _ethToASCoinRate = ethToASCoinRate;
        _vault = vault;
    }

    // setRewards
    
    //////////////////////////////////////////////////////////////
    //                                                          //
    //                       Raw Requests                       //
    //                                                          //
    //////////////////////////////////////////////////////////////
    
    function newRawRequest(
        address target,
        bytes calldata callData,
        bool payWithASC,
        uint ethForCall,
        address payable referer
    ) external payable nzAddr(target) targetNotThis(target) nzBytes(callData) validEth(payWithASC, ethForCall) returns (uint id) {
        id = _rawRequests.length;
        _newRawRequest(target, callData, payWithASC, msg.value, ethForCall, referer);
    }

    function _newRawRequest(
        address target,
        bytes calldata callData,
        bool payWithASC,
        uint initEthSent,
        uint ethForCall,
        address payable referer
    ) private {
        emit RawReqAdded(_rawRequests.length);
        _rawRequests.push(Request(payable(msg.sender), target, callData, payWithASC, initEthSent, ethForCall, referer));
    }

    function getRawRequests() external view returns (Request[] memory) {
        return _rawRequests;
    }

    function getRawRequestsLen() external view returns (uint) {
        return _rawRequests.length;
    }
    
    function getRawRequest(uint id) external view returns (Request memory) {
        return _rawRequests[id];
    }


    //////////////////////////////////////////////////////////////
    //                                                          //
    //                    Hashed Requests Eth                   //
    //                                                          //
    //////////////////////////////////////////////////////////////

    function newHashReqWithEth(
        address target,
        bytes calldata callData,
        bool payWithASC,
        uint ethForCall,
        address payable referer,
        bytes memory dataPrefix,
        bytes memory dataSuffix
    // Stack too deep with the extra nz checks
    // ) external payable nzAddr(target) targetNotThis(target) nzBytes(callData) validEth(ethForCall) returns (uint id) {
    ) external payable targetNotThis(target) validEth(payWithASC, ethForCall) returns (uint id) {
        Request memory r = Request(payable(msg.sender), target, callData, payWithASC, msg.value, ethForCall, referer);
        bytes32 hashedIpfsReq = getHashedIpfsReq(dataPrefix, getReqBytes(r), dataSuffix);

        id = _hashedIpfsReqsEth.length;
        emit HashedReqEthAdded(id);
        _hashedIpfsReqsEth.push(hashedIpfsReq);
    }

    function getHashedIpfsReqsEth() external view returns (bytes32[] memory) {
        return _hashedIpfsReqsEth;
    }

    function getHashedIpfsReqsEthLen() external view returns (uint) {
        return _hashedIpfsReqsEth.length;
    }
    
    function getHashedIpfsReqEth(uint id) external view returns (bytes32) {
        return _hashedIpfsReqsEth[id];
    }


    //////////////////////////////////////////////////////////////
    //                                                          //
    //                  Hashed Requests No Eth                  //
    //                                                          //
    //////////////////////////////////////////////////////////////

    function newHashReqNoEth(bytes32 hashedIpfsReq) external returns (uint id) {
        id = _hashedIpfsReqsNoEth.length;
        _hashedIpfsReqsNoEth.push(hashedIpfsReq);
        emit HashedReqNoEthAdded(id);
    }
    
    function getHashedIpfsReqsNoEth() external view returns (bytes32[] memory) {
        return _hashedIpfsReqsNoEth;
    }

    function getHashedIpfsReqsNoEthLen() external view returns (uint) {
        return _hashedIpfsReqsNoEth.length;
    }
    
    function getHashedIpfsReqNoEth(uint id) external view returns (bytes32) {
        return _hashedIpfsReqsNoEth[id];
    }


    //////////////////////////////////////////////////////////////
    //                                                          //
    //                        Hash Helpers                      //
    //                                                          //
    //////////////////////////////////////////////////////////////

    function getReqBytes(Request memory r) public pure returns (bytes memory) {
        return abi.encode(r);
    }

    function getIpfsReqBytes(bytes memory dataPrefix, bytes memory r, bytes memory dataPostfix) public pure returns (bytes memory) {
        return abi.encodePacked(
            dataPrefix,
            r,
            dataPostfix
        );
    }

    function getHashedIpfsReq(bytes memory dataPrefix, bytes memory r, bytes memory dataPostfix) public pure returns (bytes32) {
        return sha256(getIpfsReqBytes(dataPrefix, r, dataPostfix));
    }

    function getReqFromBytes(bytes memory rBytes) public pure returns (Request memory r) {
        (r) = abi.decode(rBytes, (Request));
    }
    

    function executeRawReq(uint id) external validExec nonReentrant returns (uint gasUsed) {
        Request memory r = _rawRequests[id];
        require(r.requester != _ADDR_0, "Reg: already executed");
        
        gasUsed = _execute(r);
        
        emit RawReqRemoved(id, true);
        delete _rawRequests[id];
    }

    function executeHashReqEth(
        uint id,
        Request memory r,
        bytes memory dataPrefix,
        bytes memory dataSuffix
    ) external validExec nonReentrant returns (uint gasUsed) {
        require(
            getHashedIpfsReq(dataPrefix, getReqBytes(r), dataSuffix) == _hashedIpfsReqsEth[id], 
            "Reg: request not the same"
        );

        gasUsed = _execute(r);
        
        emit HashedReqEthRemoved(id, true);
        delete _hashedIpfsReqsEth[id];
    }

    function executeHashReqNoEth(
        uint id,
        Request memory r,
        bytes memory dataPrefix,
        bytes memory dataSuffix
    ) external targetNotThis(r.target) validExec nonReentrant returns (uint gasUsed) {
        require(
            getHashedIpfsReq(dataPrefix, getReqBytes(r), dataSuffix) == _hashedIpfsReqsNoEth[id], 
            "Reg: request not the same"
        );
        require(
            r.initEthSent == 0 &&
            r.ethForCall == 0 &&
            r.payWithASC == true, 
            "Reg: no eth. Nice try ;)"
        );

        gasUsed = _execute(r);
        
        emit HashedReqNoEthRemoved(id, true);
        delete _hashedIpfsReqsNoEth[id];
    }


    function _execute(Request memory r) private returns (uint) {
        uint startGas = gasleft();

        // if (reqType == ReqType.Raw) {
        //     r = _rawRequests[id];
        // } else if (reqType == ReqType.HashEth) {
        //     r = _hashedIpfsReqsEth[id];
        // } else if (reqType == ReqType.HashNoEth) {
        //     r = _hashedIpfsReqsNoEth[id];
        // }

        
        // Make the call that the user requested
        // require(r.proxy.finish(true, r.target, callGas, r.callData), "Reg: call failed");
        (bool success, bytes memory returnData) = r.target.call{value: r.ethForCall}(r.callData); 
        require(success, string(returnData));
        
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

        // +1 since it never divides exactly because of the 4 bytes of methodID
        uint numStorageRefunds = (r.callData.length / 32) + 1;
        numStorageRefunds += r.referer == _ADDR_0 ? 5 : 6;
        
        uint gasUsed = 21512 + (numStorageRefunds * 5000) + startGas - gasleft();

        uint gasRefunded = numStorageRefunds * 15000;

        uint ethNeeded;

        if (r.payWithASC) {
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
            require(ethReceived >= ethNeeded, "Reg: not enough eth sent");
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
        Request memory r = _rawRequests[id];
        require(msg.sender == r.requester, "Reg: not the requester");
        
        // Cancel the request
        delete _rawRequests[id];
        emit RawReqRemoved(id, false);
        
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
        require(target != address(this) && target != address(_ASCoin), "Reg: nice try ;)");
        _;
    }

    modifier validEth(bool payWithASC, uint ethForCall) {
        if (payWithASC) {
            // When paying with ASC, there's no reason to send more ETH than will
            // be used in the future call
            require(ethForCall == msg.value, "Reg: ethForCall not msg.value");
        } else {
            // When paying with ETH, ethForCall needs to be lower than msg.value
            // since some ETH is needed to be left over for paying the fee + bounty
            require(ethForCall <= msg.value, "Reg: ethForCall too high");
        }
        _;
    }

    modifier validExec() {
        require(_stakeMan.isCurExec(msg.sender), "Registry:not executor or expired");
        _;
    }
    
    receive() external payable {}
}
