module.exports = {
    networks: {
        hardhat: {
            hardfork: "london",
            initialBaseFeePerGas: 0,
            throwOnTransactionFailures: true,
            throwOnCallFailures: true
       }
    }
}