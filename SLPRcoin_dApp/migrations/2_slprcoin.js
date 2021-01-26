var SLPR_Deployer = artifacts.require("SLPRcoinCrowdSaleDeployer");
var SLPR_Sale = artifacts.require("SLPRcoinCrowdSale");
var SLPR_Token = artifacts.require("SLPRcoin");

module.exports = function(deployer) {
  deployer.deploy(SLPR_Deployer, "SLPRCoin", "SLPR", 500, "0x57f524C137Ad3f20D3FBe8C2c0324018D2980D3A", 200, 100,
"0x6Ec140069b8ae2Fc79876D7a3c9f6FcF090711F6", "0x7A5835F929D3941D440048714D38C9Fa4704A129",
"0xbF8624CdEAFbeD3676193050ECcB5d04D479B5a5");

};


