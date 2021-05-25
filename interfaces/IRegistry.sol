pragma solidity ^0.8;


import "@openzeppelin/contracts/token/ERC20/IERC20.sol";


interface IRegistry {
    
    // The address vars are 20b, total 60, calldata is 4b + n*32b usually, which
    // has a factor of 32. uint120 since the current ETH supply of ~115m can fit
    // into that and it's the highest such that 2 * uint120 + 2 * bool is < 256b
    struct Request {
        address payable requester;
        address target;
        address payable referer;
        bytes callData;
        uint120 initEthSent;
        uint120 ethForCall;
        bool verifySender;
        bool payWithAUTO;
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
        bool payWithAUTO
    ) external payable returns (uint id);

    function getRawReqs() external view returns (Request[] memory);

    function getRawReqLen() external view returns (uint);
    
    function getRawReq(uint id) external view returns (Request memory);


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
        bool payWithAUTO,
        bytes memory dataPrefix,
        bytes memory dataSuffix
    ) external payable returns (uint id);

    function getHashedReqs() external view returns (bytes32[] memory);

    function getHashedReqsLen() external view returns (uint);
    
    function getHashedReq(uint id) external view returns (bytes32);


    //////////////////////////////////////////////////////////////
    //                                                          //
    //                Hashed Requests Unverified                //
    //                                                          //
    //////////////////////////////////////////////////////////////

    function newHashedReqUnveri(bytes32 hashedIpfsReq) external returns (uint id);
    
    function getHashedReqsUnveri() external view returns (bytes32[] memory);

    function getHashedReqsUnveriLen() external view returns (uint);
    
    function getHashedReqUnveri(uint id) external view returns (bytes32);


    //////////////////////////////////////////////////////////////
    //                                                          //
    //                        Hash Helpers                      //
    //                                                          //
    //////////////////////////////////////////////////////////////

    function getReqBytes(Request memory r) external pure returns (bytes memory);

    function getIpfsReqBytes(
        bytes memory r,
        bytes memory dataPrefix,
        bytes memory dataPostfix
    ) external pure returns (bytes memory);

    function getHashedIpfsReq(
        bytes memory r,
        bytes memory dataPrefix,
        bytes memory dataPostfix
    ) external pure returns (bytes32);

    function getReqFromBytes(bytes memory rBytes) external pure returns (Request memory r);
    

    //////////////////////////////////////////////////////////////
    //                                                          //
    //                         Executions                       //
    //                                                          //
    //////////////////////////////////////////////////////////////

    function executeRawReq(uint id) external returns (uint gasUsed);

    function executeHashedReq(
        uint id,
        Request calldata r,
        bytes memory dataPrefix,
        bytes memory dataSuffix
    ) external returns (uint gasUsed);

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
    ) external returns (uint gasUsed);


    //////////////////////////////////////////////////////////////
    //                                                          //
    //                        Cancellations                     //
    //                                                          //
    //////////////////////////////////////////////////////////////
    
    function cancelRawReq(uint id) external;
    
    function cancelHashedReq(
        uint id,
        Request memory r,
        bytes memory dataPrefix,
        bytes memory dataSuffix
    ) external;
    
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
    
    function getAUTO() external view returns (IERC20);
    
    function getStakeManager() external view returns (address);
    
    function getVerifiedForwarder() external view returns (address);
    
    function getReqCountOf(address addr) external view returns (uint);
    
    function getExecCountOf(address addr) external view returns (uint);
    
    function getReferalCountOf(address addr) external view returns (uint);
}
