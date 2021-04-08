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

    function getCurEpoch() public view returns (uint) {
        return (block.number / BLOCKS_IN_EPOCH) * BLOCKS_IN_EPOCH;
    }

    function getExecutor() external view returns (Executor memory) {
        return _executor;
    }

    function isCurExec(address addr) external view override returns (bool) {
        // TODO: Maybe do executor ex = _executor so that the storage is only loaded once?
        // If there's no stakes, allow anyone to be the executor so that a random
        // person can bootstrap the network and nobody needs to be sent any coins
        if (
            _stakes.length == 0 ||
            (_executor.addr == addr && _executor.forEpoch == getCurEpoch())
        ) {
            return true;
        }
        return false;
    }

    function getRemainder(uint a, uint b) public pure returns (uint) {
        return a % b;
    }


    //////////////////////////////////////////////////////////////
    //                                                          //
    //                          Staking                         //
    //                                                          //
    //////////////////////////////////////////////////////////////

    // Calls updateExec()
    // function updateExecutor() public updateExec noFish returns(uint, uint, address) {}
    function updateExecutor() public noFish returns(uint, uint, address) {
        return _updateExecutor();
    }

    function stake(uint numStakes) external nzUint(numStakes) updateExec noFish override returns(uint, uint, address) {
        uint amount = numStakes * STAN_STAKE;
        // Deposit the coins
        uint balBefore = _ASCoin.balanceOf(address(this));
        _ASCoin.transferFrom(msg.sender, address(this), amount);
        require(_ASCoin.balanceOf(address(this)) - balBefore == amount, "SM: transfer failed");

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
            // element we're wanting to delete (so it doesn't leave gaps)
            _stakes[idxs[i]] = _stakes[_stakes.length-1];
            _stakes.pop();
        }
        
        _stakerToStakedAmount[msg.sender] -= amount;
        _totalStaked -= amount;
        _ASCoin.transfer(msg.sender, amount);
        emit Unstaked(msg.sender, amount);
    }

    function _updateExecutor() private returns(uint, uint, address) {
        uint epoch = getCurEpoch();
        uint randNum;
        uint idxOfExecutor;
        address exec;
        // If the executor is out of date and the system already has stake,
        // choose a new executor. This will do nothing if the system is starting
        // and allow someone to stake without needing there to already be existing stakes
        if (_executor.forEpoch != epoch && _totalStaked > 0) {
            randNum = _oracle.getRandNum(epoch);
            // idxOfExecutor = randNum % _stakes.length;
            idxOfExecutor = getRemainder(randNum, _stakes.length);
            exec = _stakes[idxOfExecutor];
            _executor = Executor(exec, epoch);
        }

        return (randNum, idxOfExecutor, exec);
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