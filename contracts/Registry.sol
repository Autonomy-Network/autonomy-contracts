pragma solidity ^0.8;


import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "../interfaces/IRegistry.sol";
import "../interfaces/IStakeManager.sol";
import "../interfaces/IOracle.sol";
import "../interfaces/IForwarder.sol";
import "./abstract/Shared.sol";


contract Registry is IRegistry, Shared, ReentrancyGuard {
    
    // Constant public
    uint public constant GAS_OVERHEAD_ASCOIN = 70500;
    uint public constant GAS_OVERHEAD_ETH = 47000;
    uint public constant BASE_BOUNTY_USD = 5;
    uint public constant ETH_BOUNTY_MULTIPLIER = 3;

    // Constant private
    bytes private constant _EMPTY_BYTES = "";
    
    IERC20 private _ASCoin;
    IStakeManager private _stakeMan;
    IOracle private _oracle;
    IForwarder private _veriForwarder;
    Request[] private _rawReqs;
    // We need to have 2 separete arrays for adding requests with and without
    // eth because, when comparing the hash of a request to be executed to the
    // stored hash, we have no idea what the request had for the eth values
    // that was originally stored as a hash and therefore would need to store
    // an extra bool saying where eth was sent with the new request. Instead, 
    // that can be known implicitly by having 2 separate arrays.
    bytes32[] private _hashedReqs;
    bytes32[] private _hashedReqsUnveri;
    // This counts the number of times each requester has had a request executed
    mapping(address => uint) private _reqCounts;
    // This counts the number of times each staker has executed a request
    mapping(address => uint) private _execCounts;
    // This counts the number of times each referer has been identified in an
    // executed tx
    mapping(address => uint) private _referalCounts;
    
    
    // This is defined in IRegistry. Here for convenience
    // The address vars are 20b, total 60, calldata is 4b + n*32b usually, which
    // has a factor of 32. uint120 since the current ETH supply of ~115m can fit
    // into that and it's the highest such that 2 * uint120 + 2 * bool is < 256b
    // struct Request {
    //     address payable requester;
    //     address target;
    //     address payable referer;
    //     bytes callData;
    //     uint120 initEthSent;
    //     uint120 ethForCall;
    //     bool verifySender;
    //     bool payWithASC;
    // }

    event RawReqAdded(uint indexed id);
    event RawReqRemoved(uint indexed id, bool wasExecuted);
    event HashedReqAdded(uint indexed id);
    event HashedReqRemoved(uint indexed id, bool wasExecuted);
    event HashedReqUnveriAdded(uint indexed id);
    event HashedReqUnveriRemoved(uint indexed id, bool wasExecuted);


    constructor(
        IERC20 ASCoin,
        IStakeManager staker,
        IOracle oracle,
        IForwarder veriForwarder
    ) ReentrancyGuard() {
        _ASCoin = ASCoin;
        _stakeMan = staker;
        _oracle = oracle;
        _veriForwarder = veriForwarder;
    }


    //////////////////////////////////////////////////////////////
    //                                                          //
    //                       Raw Requests                       //
    //                                                          //
    //////////////////////////////////////////////////////////////
    
    function newRawReq(
        address target,
        address payable referer,
        bytes calldata callData,
        uint120 ethForCall,
        bool verifySender,
        bool payWithASC
    )
        external
        payable
        override
        nzAddr(target)
        targetNotThis(target)
        validEth(payWithASC, ethForCall)
        returns (uint id)
    {
        // Annoyingly, this has to be pasted from validCalldata because of
        // a 'stack too deep' error otherwise
        if (verifySender) {
            require(abi.decode(callData[4:36], (address)) == msg.sender, "Reg: calldata not verified");
        }

        id = _rawReqs.length;
        emit RawReqAdded(id);
        _rawReqs.push(Request(payable(msg.sender), target, referer, callData, uint120(msg.value), ethForCall, verifySender, payWithASC));
    }

    function getRawReqs() external view override returns (Request[] memory) {
        return _rawReqs;
    }

    function getRawReqsSlice(uint startIdx, uint endIdx) external view returns (Request[] memory) {
        Request[] memory slice = new Request[](endIdx - startIdx);
        uint sliceIdx = 0;
        for (uint arrIdx = startIdx; arrIdx < endIdx; arrIdx++) {
            slice[sliceIdx] = _rawReqs[arrIdx];
            sliceIdx++;
        }

        return slice;
    }

    function getRawReqLen() external view override returns (uint) {
        return _rawReqs.length;
    }
    
    function getRawReq(uint id) external view override returns (Request memory) {
        return _rawReqs[id];
    }


    //////////////////////////////////////////////////////////////
    //                                                          //
    //                      Hashed Requests                     //
    //                                                          //
    //////////////////////////////////////////////////////////////

    function newHashedReq(
        address target,
        address payable referer,
        bytes calldata callData,
        uint120 ethForCall,
        bool verifySender,
        bool payWithASC,
        bytes memory dataPrefix,
        bytes memory dataSuffix
    // Stack too deep with the extra nz checks
    // ) external payable nzAddr(target) targetNotThis(target) validEth(ethForCall) returns (uint id) {
    )
        external
        payable
        override
        targetNotThis(target)
        validEth(payWithASC, ethForCall)
        returns (uint id)
    {
        Request memory r = Request(payable(msg.sender), target, referer, callData, uint120(msg.value), ethForCall, verifySender, payWithASC);
        bytes32 hashedIpfsReq = getHashedIpfsReq(dataPrefix, getReqBytes(r), dataSuffix);

        id = _hashedReqs.length;
        emit HashedReqAdded(id);
        _hashedReqs.push(hashedIpfsReq);
    }

    function getHashedReqs() external view override returns (bytes32[] memory) {
        return _hashedReqs;
    }

    function getHashedReqsSlice(uint startIdx, uint endIdx) external view returns (bytes32[] memory) {
        return _getBytes32Slice(_hashedReqs, startIdx, endIdx);
    }

    function getHashedReqsLen() external view override returns (uint) {
        return _hashedReqs.length;
    }
    
    function getHashedReq(uint id) external view override returns (bytes32) {
        return _hashedReqs[id];
    }


    //////////////////////////////////////////////////////////////
    //                                                          //
    //                Hashed Requests Unverified                //
    //                                                          //
    //////////////////////////////////////////////////////////////

    function newHashedReqUnveri(bytes32 hashedIpfsReq)
        external
        override
        nzBytes32(hashedIpfsReq)
        returns (uint id)
    {
        id = _hashedReqsUnveri.length;
        _hashedReqsUnveri.push(hashedIpfsReq);
        emit HashedReqUnveriAdded(id);
    }
    
    function getHashedReqsUnveri() external view override returns (bytes32[] memory) {
        return _hashedReqsUnveri;
    }

    function getHashedReqsUnveriSlice(uint startIdx, uint endIdx) external view returns (bytes32[] memory) {
        return _getBytes32Slice(_hashedReqsUnveri, startIdx, endIdx);
    }

    function getHashedReqsUnveriLen() external view override returns (uint) {
        return _hashedReqsUnveri.length;
    }
    
    function getHashedReqUnveri(uint id) external view override returns (bytes32) {
        return _hashedReqsUnveri[id];
    }


    //////////////////////////////////////////////////////////////
    //                                                          //
    //                        Hash Helpers                      //
    //                                                          //
    //////////////////////////////////////////////////////////////

    function getReqBytes(Request memory r) public pure override returns (bytes memory) {
        return abi.encode(r);
    }

    function getIpfsReqBytes(
        bytes memory r,
        bytes memory dataPrefix,
        bytes memory dataPostfix
    ) public pure override returns (bytes memory) {
        return abi.encodePacked(
            dataPrefix,
            r,
            dataPostfix
        );
    }

    function getHashedIpfsReq(
        bytes memory r,
        bytes memory dataPrefix,
        bytes memory dataPostfix
    ) public pure override returns (bytes32) {
        return sha256(getIpfsReqBytes(dataPrefix, r, dataPostfix));
    }

    function getReqFromBytes(bytes memory rBytes) public pure override returns (Request memory r) {
        (r) = abi.decode(rBytes, (Request));
    }
    

    //////////////////////////////////////////////////////////////
    //                                                          //
    //                         Executions                       //
    //                                                          //
    //////////////////////////////////////////////////////////////

    function executeRawReq(uint id) external override validExec nonReentrant returns (uint gasUsed) {
        uint gasss = gasleft();
        Request memory r = _rawReqs[id];
        require(r.requester != _ADDR_0, "Reg: already executed");
        uint ethStartBal = address(this).balance;
        
        uint startGas = gasleft();
        delete _rawReqs[id];
        gasUsed = _execute(r, startGas - gasleft(), 19500);
        
        emit RawReqRemoved(id, true);

        if (r.payWithASC) {
            require(address(this).balance >= ethStartBal - r.ethForCall, "Reg: something fishy here");
        } else {
            require(address(this).balance >= ethStartBal - r.initEthSent, "Reg: something fishy here");
        }
    }

    /**
     * @dev validCalldata needs to be before anything that would convert it to memory
     *      since that is persistent and would prevent validCalldata, that requries
     *      calldata, from working. Can't do the check in _execute for the same reason.
     *      Note: targetNotThis and validEth are used in newHashedReq.
     *      validCalldata is only used here because it causes an unknown
     *      'InternalCompilerError' when using it with newHashedReq
     */
    function executeHashedReq(
        uint id,
        Request calldata r,
        bytes memory dataPrefix,
        bytes memory dataSuffix
    )
        external
        override
        validExec
        nonReentrant
        noFish(r)
        validCalldata(r)
        verReq(id, r, dataPrefix, dataSuffix, _hashedReqs)
        returns (uint gasUsed)
    {
        uint startGas = gasleft();
        delete _hashedReqs[id];
        gasUsed = _execute(r, startGas - gasleft(), msg.data.length * 20);
        
        emit HashedReqRemoved(id, true);
    }

    /**
     * @dev validCalldata needs to be before anything that would convert it to memory
     *      since that is persistent and would prevent validCalldata, that requries
     *      calldata, from working. Can't do the check in _execute for the same reason
     */
    function executeHashedReqUnveri(
        uint id,
        Request calldata r,
        bytes memory dataPrefix,
        bytes memory dataSuffix
    )
        external
        override
        validExec
        nonReentrant
        noFish(r)
        targetNotThis(r.target)
        verReq(id, r, dataPrefix, dataSuffix, _hashedReqsUnveri)
        returns (uint gasUsed)
    {
        require(
            r.initEthSent == 0 &&
            r.ethForCall == 0 &&
            r.payWithASC == true &&
            r.verifySender == false,
            "Reg: cannot verify. Nice try ;)"
        );

        uint startGas = gasleft();
        delete _hashedReqsUnveri[id];
        // 1000 extra is needed compared to executeHashedReq because of the extra checks
        gasUsed = _execute(r, startGas - gasleft(), (msg.data.length * 20) + 1000);
        
        emit HashedReqUnveriRemoved(id, true);
    }

    function _execute(Request memory r, uint gasUsedInDelete, uint extraOverhead) private returns (uint gasUsed) {
        uint startGas = gasleft();

        // Make the call that the user requested
        bool success;
        bytes memory returnData;
        if (r.verifySender) {
            (success, returnData) = _veriForwarder.forward{value: r.ethForCall}(r.target, r.callData);
        } else {
            (success, returnData) = r.target.call{value: r.ethForCall}(r.callData);
        }
        // Need this if statement because if the call succeeds, the tx will revert
        // with an EVM error because it can't decode 0x00. If a tx fails with no error
        // message, maybe that's a problem? But if it failed without a message then it's
        // gonna be hard to know what went wrong regardless
        if (!success) {
            revert(abi.decode(returnData, (string)));
        }
        // require(success, string(returnData));
        
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
        // the amounts changed from were 0 or non-0
        _reqCounts[r.requester] += 1;
        _execCounts[msg.sender] += 1;
        if (r.referer != _ADDR_0) {
            _referalCounts[r.referer] += 1;
        }

        IOracle orac = _oracle;
        uint gasPrice = orac.getGasPriceFast();

        uint numStorageRefunds = (gasUsedInDelete / 5000) - 1;
        
        uint callGasUsed = (startGas - gasleft());
        gasUsed = gasUsedInDelete + callGasUsed + extraOverhead;

        uint gasRefunded = numStorageRefunds * 15000;

        if (r.payWithASC) {
            gasUsed += GAS_OVERHEAD_ASCOIN;
            if (gasRefunded > gasUsed / 2) {
                gasUsed = (gasUsed / 2) + (numStorageRefunds * 700);
            } else {
                gasUsed += (numStorageRefunds * 855);
                gasUsed -= gasRefunded;
            }

            uint gasInASC = gasUsed * gasPrice * orac.getASCPerUSD() / orac.getETHPerUSD();
            uint ASCNeeded = (orac.getASCPerUSD() * BASE_BOUNTY_USD) + gasInASC;

            // Send the executor their bounty
            require(_ASCoin.transferFrom(r.requester, msg.sender, ASCNeeded));
        } else {
            gasUsed += GAS_OVERHEAD_ETH;
            if (gasRefunded > gasUsed / 2) {
                gasUsed = (gasUsed / 2) + (numStorageRefunds * 700);
            } else {
                gasUsed += (numStorageRefunds * 855);
                gasUsed -= gasRefunded;
            }

            uint ethNeeded = (gasUsed * gasPrice) + (3 * BASE_BOUNTY_USD * orac.getETHPerUSD());
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
    }

    //////////////////////////////////////////////////////////////
    //                                                          //
    //                        Cancellations                     //
    //                                                          //
    //////////////////////////////////////////////////////////////
    
    function cancelRawReq(uint id) external override nonReentrant {
        Request memory r = _rawReqs[id];
        require(msg.sender == r.requester, "Reg: not the requester");
        
        // Cancel the request
        delete _rawReqs[id];
        emit RawReqRemoved(id, false);
        
        // Send refund
        if (r.initEthSent > 0) {
            r.requester.transfer(r.initEthSent);
        }
    }
    
    function cancelHashedReq(
        uint id,
        Request memory r,
        bytes memory dataPrefix,
        bytes memory dataSuffix
    )
        external
        override
        nonReentrant
        verReq(id, r, dataPrefix, dataSuffix, _hashedReqs)
    {
        require(msg.sender == r.requester, "Reg: not the requester");
        
        // Cancel the request
        emit HashedReqRemoved(id, false);
        delete _hashedReqs[id];
        
        // Send refund
        if (r.initEthSent > 0) {
            r.requester.transfer(r.initEthSent);
        }
    }
    
    function cancelHashedReqUnveri(
        uint id,
        Request memory r,
        bytes memory dataPrefix,
        bytes memory dataSuffix
    )
        external
        override
        nonReentrant
        verReq(id, r, dataPrefix, dataSuffix, _hashedReqsUnveri)
    {
        require(msg.sender == r.requester, "Reg: not the requester");
        
        // Cancel the request
        emit HashedReqUnveriRemoved(id, false);
        delete _hashedReqsUnveri[id];
    }
    
    
    //////////////////////////////////////////////////////////////
    //                                                          //
    //                          Getters                         //
    //                                                          //
    //////////////////////////////////////////////////////////////
    
    function getASCoin() external view override returns (IERC20) {
        return _ASCoin;
    }
    
    function getStakeManager() external view override returns (address) {
        return address(_stakeMan);
    }
    
    function getVerifiedForwarder() external view override returns (address) {
        return address(_veriForwarder);
    }

    function getReqCountOf(address addr) external view override returns (uint) {
        return _reqCounts[addr];
    }
    
    function getExecCountOf(address addr) external view override returns (uint) {
        return _execCounts[addr];
    }
    
    function getReferalCountOf(address addr) external view override returns (uint) {
        return _referalCounts[addr];
    }

    function divAOverB(uint a, uint b) external pure override returns (uint) {
        return a / b;
    }

    function _getBytes32Slice(bytes32[] memory arr, uint startIdx, uint endIdx) private pure returns (bytes32[] memory) {
        bytes32[] memory slice = new bytes32[](endIdx - startIdx);
        uint sliceIdx = 0;
        for (uint arrIdx = startIdx; arrIdx < endIdx; arrIdx++) {
            slice[sliceIdx] = arr[arrIdx];
            sliceIdx++;
        }

        return slice;
    }


    //////////////////////////////////////////////////////////////
    //                                                          //
    //                          Modifiers                       //
    //                                                          //
    //////////////////////////////////////////////////////////////

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

    modifier validCalldata(Request calldata r) {
        if (r.verifySender) {
            require(abi.decode(r.callData[4:36], (address)) == r.requester, "Reg: calldata not verified");
        }
        _;
    }

    modifier validExec() {
        require(_stakeMan.isUpdatedExec(msg.sender), "Reg: not executor or expired");
        _;
    }

    modifier noFish(Request calldata r) {
        uint ethStartBal = address(this).balance;

        _;

        if (r.payWithASC) {
            require(address(this).balance >= ethStartBal - r.ethForCall, "Reg: something fishy here");
        } else {
            require(address(this).balance >= ethStartBal - r.initEthSent, "Reg: something fishy here");
        }
    }

    // Verify that a request is the same as the one initially stored. This also
    // implicitly checks that the request hasn't been deleted as the hash of the
    // request isn't going to be address(0)
    modifier verReq(
        uint id,
        Request memory r,
        bytes memory dataPrefix,
        bytes memory dataSuffix,
        bytes32[] storage hashedIpfsReqs
    ) {
        require(
            getHashedIpfsReq(dataPrefix, getReqBytes(r), dataSuffix) == hashedIpfsReqs[id], 
            "Reg: request not the same"
        );
        _;
    }
    
    receive() external payable {}
}
