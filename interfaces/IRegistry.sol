pragma solidity ^0.8;


import "@openzeppelin/contracts/token/ERC20/IERC20.sol";


interface IRegistry {
    
    struct Request {
        address payable requester;
        address target;
        bytes callData;
        bool verifySender;
        bool payWithASC;
        uint initEthSent;
        uint ethForCall;
        address payable referer;
    }


    //////////////////////////////////////////////////////////////
    //                                                          //
    //                       Raw Requests                       //
    //                                                          //
    //////////////////////////////////////////////////////////////
    
    function newRawReq(
        address target,
        bytes calldata callData,
        bool verifySender,
        bool payWithASC,
        uint ethForCall,
        address payable referer
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
        bytes calldata callData,
        bool verifySender,
        bool payWithASC,
        uint ethForCall,
        address payable referer,
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
        bytes memory dataPrefix,
        bytes memory r,
        bytes memory dataPostfix
    ) external pure returns (bytes memory);

    function getHashedIpfsReq(
        bytes memory dataPrefix,
        bytes memory r,
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
    
    function getASCoin() external view returns (IERC20);
    
    function getStakeManager() external view returns (address);
    
    function getVerifiedForwarder() external view returns (address);
    
    function getReqCountOf(address addr) external view returns (uint);
    
    function getExecCountOf(address addr) external view returns (uint);
    
    function getReferalCountOf(address addr) external view returns (uint);

    function divAOverB(uint a, uint b) external view returns (uint);
}
