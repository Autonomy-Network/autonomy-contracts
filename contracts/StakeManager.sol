pragma solidity ^0.8;


import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "../interfaces/IStakeManager.sol";
import "../interfaces/IOracle.sol";
import "./abstract/Shared.sol";


contract StakeManager is IStakeManager, Shared {

    uint public constant STAN_STAKE = 10000 * _E_18;
    uint public constant BLOCKS_IN_EPOCH = 100;

    IOracle private _oracle;
    IERC20 private _ASCoin;
    uint private _totalStaked = 0;
    mapping(address => uint) private _stakerToStakedAmount;
    address[] private _stakes;
    Executor private _executor;


    struct Executor{
        address addr;
        uint forEpoch;
    }


    event Staked(address staker, uint amount);
    event Unstaked(address staker, uint amount);


    constructor(IOracle oracle, IERC20 ASCoin) {
        _oracle = oracle;
        _ASCoin = ASCoin;
    }


    //////////////////////////////////////////////////////////////
    //                                                          //
    //                          Getters                         //
    //                                                          //
    //////////////////////////////////////////////////////////////

    function getOracle() external view returns (IOracle) {
        return _oracle;
    }

    function getASCoin() external view returns (address) {
        return address(_ASCoin);
    }

    function getTotalStaked() external view returns (uint) {
        return _totalStaked;
    }

    function getStake(address staker) external view returns (uint) {
        return _stakerToStakedAmount[staker];
    }

    function getStakes() external view returns (address[] memory) {
        return _stakes;
    }

    function getStakesLength() external view returns (uint) {
        return _stakes.length;
    }

    function getStakesSlice(uint startIdx, uint endIdx) external view returns (address[] memory) {
        address[] memory slice = new address[](endIdx - startIdx);
        uint sliceIdx = 0;
        for (uint stakeIdx = startIdx; stakeIdx < endIdx; stakeIdx++) {
            slice[sliceIdx] = _stakes[stakeIdx];
            sliceIdx++;
        }

        return slice;
    }

    function getCurEpoch() public view returns (uint) {
        return (block.number / BLOCKS_IN_EPOCH) * BLOCKS_IN_EPOCH;
    }

    function getExecutor() external view returns (Executor memory) {
        return _executor;
    }

    function isCurExec(address addr) external view override returns (bool) {
        // So that the storage is only loaded once
        Executor memory ex = _executor;
        if (ex.addr == addr && ex.forEpoch == getCurEpoch()) { return true; }
        // If there're no stakes, allow anyone to be the executor so that a random
        // person can bootstrap the network and nobody needs to be sent any coins
        if (_stakes.length == 0) { return true; }

        return false;
    }

    function getUpdatedExecRes() public view returns (uint epoch, uint randNum, uint idxOfExecutor, address exec) {
        epoch = getCurEpoch();
        // So that the storage is only loaded once
        address[] memory stakes = _stakes;
        // If the executor is out of date and the system already has stake,
        // choose a new executor. This will do nothing if the system is starting
        // and allow someone to stake without needing there to already be existing stakes
        if (_executor.forEpoch != epoch && stakes.length > 0) {
            // -1 because blockhash(seed) in Oracle will return 0x00 if the
            // seed == this block's height
            randNum = _oracle.getRandNum(epoch - 1);
            idxOfExecutor = randNum % stakes.length;
            exec = stakes[idxOfExecutor];
        }
    }


    //////////////////////////////////////////////////////////////
    //                                                          //
    //                          Staking                         //
    //                                                          //
    //////////////////////////////////////////////////////////////

    function updateExecutor() external override noFish returns (uint, uint, uint, address) {
        return _updateExecutor();
    }

    function isUpdatedExec(address addr) external override noFish returns (bool) {
        // So that the storage is only loaded once
        Executor memory ex = _executor;
        if (ex.forEpoch == getCurEpoch() && ex.addr == addr) {
            return true;
        } else {
            (, , , address exec) = _updateExecutor();
            if (exec == addr) { return true; }
        }
        if (_stakes.length == 0) { return true; }

        return false;
    }

    // The 1st stake/unstake of an epoch shouldn't change the executor, otherwise
    // a staker could precalculate the effect of how much they stake in order to
    // game the staker selection algo
    function stake(uint numStakes) external nzUint(numStakes) updateExec noFish override {
        uint amount = numStakes * STAN_STAKE;
        // So that the storage is only loaded once
        IERC20 asCoin = _ASCoin;
        // Deposit the coins
        uint balBefore = asCoin.balanceOf(address(this));
        require(asCoin.transferFrom(msg.sender, address(this), amount), "SM: transfer failed");
        // This check is a bit unnecessary, but better to be paranoid than r3kt
        require(asCoin.balanceOf(address(this)) - balBefore == amount, "SM: transfer bal check failed");

        for (uint i; i < numStakes; i++) {
            _stakes.push(msg.sender);
        }

        _stakerToStakedAmount[msg.sender] += amount;
        _totalStaked += amount;
        emit Staked(msg.sender, amount);
    }

    function unstake(uint[] calldata idxs) external nzUintArr(idxs) updateExec noFish override {
        uint amount = idxs.length * STAN_STAKE;
        require(amount <= _stakerToStakedAmount[msg.sender], "SM: not enough stake, peasant");

        for (uint i = 0; i < idxs.length; i++) {
            require(_stakes[idxs[i]] == msg.sender, "SM: idx is not you");
            // Update stakes by moving the last element to the
            // element we're wanting to delete (so it doesn't leave gaps, which is
            // necessary for the _updateExecutor algo)
            _stakes[idxs[i]] = _stakes[_stakes.length-1];
            _stakes.pop();
        }
        
        _stakerToStakedAmount[msg.sender] -= amount;
        _totalStaked -= amount;
        require(_ASCoin.transfer(msg.sender, amount));
        emit Unstaked(msg.sender, amount);
    }

    function _updateExecutor() private returns (uint epoch, uint randNum, uint idxOfExecutor, address exec) {
        (epoch, randNum, idxOfExecutor, exec) = getUpdatedExecRes();
        if (exec != _ADDR_0) {
            _executor = Executor(exec, epoch);
        }
    }

    modifier updateExec() {
        // Need to update executor at the start of stake/unstake as opposed to the
        // end of the fcns because otherwise, for the 1st stake/unstake tx in an 
        // epoch, someone could influence the outcome of the executor by precalculating
        // the outcome based on how much they stake and unfairly making themselves the executor
        _updateExecutor();
        _;
    }

    // Ensure the contract is fully collateralised every time
    modifier noFish() {
        _;
        // >= because someone could send some tokens to this contract and disable it if it was ==
        require(_ASCoin.balanceOf(address(this)) >= _totalStaked, "SM: something fishy here");
    }
}