pragma solidity 0.8.6;


import "@openzeppelin/contracts/token/ERC20/IERC20.sol";


/**
* @title    Registry
* @notice   A contract which is essentially a glorified forwarder.
*           It essentially brings together people who want things executed,
*           and people who want to do that execution in return for a fee.
*           Users register the details of what they want executed, which
*           should always revert unless their execution condition is true,
*           and executors execute the request when the condition is true.
*           Only a specific executor is allowed to execute requests at any
*           given time, as determined by the StakeManager, which requires
*           staking AUTO tokens. This is infrastructure, and an integral
*           piece of the future of web3. It also provides the spark of life
*           for a new form of organism - cyber life. We are the gods now.
* @author   Quantaf1re (James Key)
*/
interface IRegistry {
    
    // The address vars are 20b, total 60, calldata is 4b + n*32b usually, which
    // has a factor of 32. uint112 since the current ETH supply of ~115m can fit
    // into that and it's the highest such that 2 * uint112 + 3 * bool is < 256b
    struct Request {
        address payable user;
        address target;
        address payable referer;
        bytes callData;
        uint112 initEthSent;
        uint112 ethForCall;
        bool verifyUser;
        bool insertFeeAmount;
        bool payWithAUTO;
        bool isAlive;
    }


    //////////////////////////////////////////////////////////////
    //                                                          //
    //                      Hashed Requests                     //
    //                                                          //
    //////////////////////////////////////////////////////////////

    /**
     * @notice  Creates a new request, logs the request info in an event, then saves
     *          a hash of it on-chain in `_hashedReqs`. Uses the default for whether
     *          to pay in ETH or AUTO
     * @param target    The contract address that needs to be called
     * @param referer       The referer to get rewarded for referring the sender
     *                      to using Autonomy. Usally the address of a dapp owner
     * @param callData  The calldata of the call that the request is to make, i.e.
     *                  the fcn identifier + inputs, encoded
     * @param ethForCall    The ETH to send with the call
     * @param verifyUser  Whether the 1st input of the calldata equals the sender.
     *                      Needed for dapps to know who the sender is whilst
     *                      ensuring that the sender intended
     *                      that fcn and contract to be called - dapps will
     *                      require that msg.sender is the Verified Forwarder,
     *                      and only requests that have `verifyUser` = true will
     *                      be forwarded via the Verified Forwarder, so any calls
     *                      coming from it are guaranteed to have the 1st argument
     *                      be the sender
     * @param insertFeeAmount     Whether the gas estimate of the executor should be inserted
     *                      into the callData
     * @param isAlive       Whether or not the request should be deleted after it's executed
     *                      for the first time. If `true`, the request will exist permanently
     *                      (tho it can be cancelled any time), therefore executing the same
     *                      request repeatedly aslong as the request is executable,
     *                      and can be used to create fully autonomous contracts - the
     *                      first single-celled cyber life. We are the gods now
     * @return id   The id of the request, equal to the index in `_hashedReqs`
     */
    function newReq(
        address target,
        address payable referer,
        bytes calldata callData,
        uint112 ethForCall,
        bool verifyUser,
        bool insertFeeAmount,
        bool isAlive
    ) external payable returns (uint id);

    /**
     * @notice  Creates a new request, logs the request info in an event, then saves
     *          a hash of it on-chain in `_hashedReqs`
     * @param target    The contract address that needs to be called
     * @param referer       The referer to get rewarded for referring the sender
     *                      to using Autonomy. Usally the address of a dapp owner
     * @param callData  The calldata of the call that the request is to make, i.e.
     *                  the fcn identifier + inputs, encoded
     * @param ethForCall    The ETH to send with the call
     * @param verifyUser  Whether the 1st input of the calldata equals the sender.
     *                      Needed for dapps to know who the sender is whilst
     *                      ensuring that the sender intended
     *                      that fcn and contract to be called - dapps will
     *                      require that msg.sender is the Verified Forwarder,
     *                      and only requests that have `verifyUser` = true will
     *                      be forwarded via the Verified Forwarder, so any calls
     *                      coming from it are guaranteed to have the 1st argument
     *                      be the sender
     * @param insertFeeAmount     Whether the gas estimate of the executor should be inserted
     *                      into the callData
     * @param payWithAUTO   Whether the sender wants to pay for the request in AUTO
     *                      or ETH. Paying in AUTO reduces the fee
     * @param isAlive       Whether or not the request should be deleted after it's executed
     *                      for the first time. If `true`, the request will exist permanently
     *                      (tho it can be cancelled any time), therefore executing the same
     *                      request repeatedly aslong as the request is executable,
     *                      and can be used to create fully autonomous contracts - the
     *                      first single-celled cyber life. We are the gods now
     * @return id   The id of the request, equal to the index in `_hashedReqs`
     */
    function newReqPaySpecific(
        address target,
        address payable referer,
        bytes calldata callData,
        uint112 ethForCall,
        bool verifyUser,
        bool insertFeeAmount,
        bool payWithAUTO,
        bool isAlive
    ) external payable returns (uint id);

    /**
     * @notice  Gets all keccak256 hashes of encoded requests. Completed requests will be 0x00
     * @return  [bytes32[]] An array of all hashes
     */
    function getHashedReqs() external view returns (bytes32[] memory);

    /**
     * @notice  Gets part of the keccak256 hashes of encoded requests. Completed requests will be 0x00.
     *          Needed since the array will quickly grow to cost more gas than the block limit to retrieve.
     *          so it can be viewed in chunks. E.g. for an array of x = [4, 5, 6, 7], x[1, 2] returns [5],
     *          the same as lists in Python
     * @param startIdx  [uint] The starting index from which to start getting the slice (inclusive)
     * @param endIdx    [uint] The ending index from which to start getting the slice (exclusive)
     * @return  [bytes32[]] An array of all hashes
     */
    function getHashedReqsSlice(uint startIdx, uint endIdx) external view returns (bytes32[] memory);

    /**
     * @notice  Gets the total number of requests that have been made, hashed, and stored
     * @return  [uint] The total number of hashed requests
     */
    function getHashedReqsLen() external view returns (uint);
    
    /**
     * @notice      Gets a single hashed request
     * @param id    [uint] The id of the request, which is its index in the array
     * @return      [bytes32] The sha3 hash of the request
     */
    function getHashedReq(uint id) external view returns (bytes32);


    //////////////////////////////////////////////////////////////
    //                                                          //
    //                Hashed Requests Unverified                //
    //                                                          //
    //////////////////////////////////////////////////////////////

    /**
     * @notice  Creates a new hashed request by blindly storing a raw hash on-chain. It's 
     *          'unverified' because when executing it, it's impossible to tell whether any
     *          ETH was initially sent with the request etc, so executing this request requires
     *          that the request which hashes to `hashedIpfsReq` has `ethForCall` = 0,
     *          `initEthSend` = 0, `verifyUser` = false, and `payWithAUTO` = true
     * @param id    [bytes32] The hash to save. The hashing algo isn't keccak256 like with `newReq`,
     *          it instead uses sha256 so that it's compatible with ipfs - the hash stored on-chain
     *          should be able to be used in ipfs to point to the request which hashes to `hashedIpfsReq`.
     *          Because ipfs doesn't hash only the data stored, it hashes a prepends a few bytes to the
     *          encoded data and appends a few bytes to the data, the hash has to be over [prefix + data + postfix]
     * @return id   The id of the request, equal to the index in `_hashedReqsUnveri`
     */
    function newHashedReqUnveri(bytes32 hashedIpfsReq) external returns (uint id);

    /**
     * @notice  Gets part of the sha256 hashes of ipfs-encoded requests. Completed requests will be 0x00.
     *          Needed since the array will quickly grow to cost more gas than the block limit to retrieve.
     *          so it can be viewed in chunks. E.g. for an array of x = [4, 5, 6, 7], x[1, 2] returns [5],
     *          the same as lists in Python
     * @param startIdx  [uint] The starting index from which to start getting the slice (inclusive)
     * @param endIdx    [uint] The ending index from which to start getting the slice (exclusive)
     * @return  [bytes32[]] An array of all hashes
     */
    function getHashedReqsUnveriSlice(uint startIdx, uint endIdx) external view returns (bytes32[] memory);
    
    /**
     * @notice  Gets all sha256 hashes of ipfs-encoded requests. Completed requests will be 0x00
     * @return  [bytes32[]] An array of all hashes
     */
    function getHashedReqsUnveri() external view returns (bytes32[] memory);

    /**
     * @notice  Gets the total number of unverified requests that have been stored
     * @return  [uint] The total number of hashed unverified requests
     */
    function getHashedReqsUnveriLen() external view returns (uint);
    
    /**
     * @notice      Gets a single hashed unverified request
     * @param id    [uint] The id of the request, which is its index in the array
     * @return      [bytes32] The sha256 hash of the ipfs-encoded request
     */
    function getHashedReqUnveri(uint id) external view returns (bytes32);


    //////////////////////////////////////////////////////////////
    //                                                          //
    //                        Bytes Helpers                     //
    //                                                          //
    //////////////////////////////////////////////////////////////

    /**
     * @notice      Encode a request into bytes
     * @param r     [request] The request to be encoded
     * @return      [bytes] The bytes array of the encoded request
     */
    function getReqBytes(Request memory r) external pure returns (bytes memory);

    /**
     * @notice      Encode a request into bytes the same way ipfs does - by doing hash(prefix | request | postfix)
     * @param r     [request] The request to be encoded
     * @param dataPrefix    [bytes] The prefix that ipfs prepends to this data before hashing
     * @param dataPostfix   [bytes] The postfix that ipfs appends to this data before hashing
     * @return  [bytes] The bytes array of the encoded request
     */
    function getIpfsReqBytes(
        bytes memory r,
        bytes memory dataPrefix,
        bytes memory dataPostfix
    ) external pure returns (bytes memory);

    /**
     * @notice      Get the hash of an encoded request, encoding into bytes the same way ipfs
     *              does - by doing hash(prefix | request | postfix)
     * @param r     [request] The request to be encoded
     * @param dataPrefix    [bytes] The prefix that ipfs prepends to this data before hashing
     * @param dataPostfix   [bytes] The postfix that ipfs appends to this data before hashing
     * @return  [bytes32] The sha256 hash of the ipfs-encoded request
     */
    function getHashedIpfsReq(
        bytes memory r,
        bytes memory dataPrefix,
        bytes memory dataPostfix
    ) external pure returns (bytes32);

    /**
     * @notice      Get the decoded request back from encoded bytes
     * @param rBytes    [bytes] The encoded bytes version of a request
     * @return r    [Request] The request as a struct
     */
    function getReqFromBytes(bytes memory rBytes) external pure returns (Request memory r);

    function insertToCallData(bytes calldata callData, uint expectedGas, uint startIdx) external pure returns (bytes memory);


    //////////////////////////////////////////////////////////////
    //                                                          //
    //                         Executions                       //
    //                                                          //
    //////////////////////////////////////////////////////////////

    /**
     * @notice      Execute a hashedReq. Calls the `target` with `callData`, then
     *              charges the user the fee, and gives it to the executor
     * @param id    [uint] The index of the request in `_hashedReqs`
     * @param r     [request] The full request struct that fully describes the request.
     *              Typically known by seeing the `HashedReqAdded` event emitted with `newReq`
     * @param expectedGas   [uint] The gas that the executor expects the execution to cost,
     *                      known by simulating the the execution of this tx locally off-chain.
     *                      This can be forwarded as part of the requested call such that the
     *                      receiving contract knows how much gas the whole execution cost and
     *                      can do something to compensate the exact amount (e.g. as part of a trade).
     *                      Cannot be more than 10% above the measured gas cost by the end of execution
     * @return gasUsed      [uint] The gas that was used as part of the execution. Used to know `expectedGas`
     */
    function executeHashedReq(
        uint id,
        Request calldata r,
        uint expectedGas
    ) external returns (uint gasUsed);

    /**
     * @notice      Execute a hashedReqUnveri. Hashes `r`, `dataPrefix`, and `dataSuffix`
     *              together in the same way that ipfs does such that the hash stored on-chain
     *              is the same as the hash used to look up on ipfs to see the raw request.
     *              Since `newHashedReqUnveri` does no verification at all since it can't,
     *              `executeHashedReqUnveri` has to instead. There are some things it can't
     *              know, like the amount of ETH sent in the original request call, so they're
     *              forced to be zero
     * @param id    [uint] The index of the request in `_hashedReqs`
     * @param r     [request] The full request struct that fully describes the request. Typically
     *              known by looking up the hash on ipfs
     * @param dataPrefix    [bytes] The data prepended to the bytes form of `r` before being hashed
     *                      in ipfs
     * @param dataSuffix    [bytes] The data appended to the bytes form of `r` before being hashed
     *                      in ipfs
     * @param expectedGas   [uint] The gas that the executor expects the execution to cost,
     *                      known by simulating the the execution of this tx locally off-chain.
     *                      This can be forwarded as part of the requested call such that the
     *                      receiving contract knows how much gas the whole execution cost and
     *                      can do something to compensate the exact amount (e.g. as part of a trade).
     *                      Cannot be more than 10% above the measured gas cost by the end of execution
     * @return gasUsed      [uint] The gas that was used as part of the execution. Used to know `expectedGas`
     */
    function executeHashedReqUnveri(
        uint id,
        Request calldata r,
        bytes memory dataPrefix,
        bytes memory dataSuffix,
        uint expectedGas
    ) external returns (uint gasUsed);


    //////////////////////////////////////////////////////////////
    //                                                          //
    //                        Cancellations                     //
    //                                                          //
    //////////////////////////////////////////////////////////////
    
    /**
     * @notice      Execute a hashedReq. Calls the `target` with `callData`, then
     *              charges the user the fee, and gives it to the executor
     * @param id    [uint] The index of the request in `_hashedReqs`
     * @param r     [request] The full request struct that fully describes the request.
     *              Typically known by seeing the `HashedReqAdded` event emitted with `newReq`
     */
    function cancelHashedReq(
        uint id,
        Request memory r
    ) external;
    
    /**
     * @notice      Execute a hashedReq. Calls the `target` with `callData`, then
     *              charges the user the fee, and gives it to the executor
     * @param id    [uint] The index of the request in `_hashedReqs`
     * @param r     [request] The full request struct that fully describes the request. Typically
     *              known by looking up the hash on ipfs
     * @param dataPrefix    [bytes] The data prepended to the bytes form of `r` before being hashed
     *                      in ipfs
     * @param dataSuffix    [bytes] The data appended to the bytes form of `r` before being hashed
     *                      in ipfs
     */
    function cancelHashedReqUnveri(
        uint id,
        Request memory r,
        bytes memory dataPrefix,
        bytes memory dataSuffix
    ) external;
    
    
    //////////////////////////////////////////////////////////////
    //                                                          //
    //                          Getters                         //
    //                                                          //
    //////////////////////////////////////////////////////////////
    
    function getAUTOAddr() external view returns (address);
    
    function getStakeManager() external view returns (address);

    function getOracle() external view returns (address);
    
    function getUserForwarder() external view returns (address);
    
    function getGasForwarder() external view returns (address);
    
    function getUserGasForwarder() external view returns (address);
    
    function getReqCountOf(address addr) external view returns (uint);
    
    function getExecCountOf(address addr) external view returns (uint);
    
    function getReferalCountOf(address addr) external view returns (uint);
}
