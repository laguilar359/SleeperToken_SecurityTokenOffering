pragma solidity ^0.5.0;

import "./SLPRcoin.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20Detailed.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20Mintable.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20Pausable.sol";
import "@openzeppelin/contracts/token/ERC20/TokenTimelock.sol";
import "@openzeppelin/contracts/crowdsale/Crowdsale.sol";
import "@openzeppelin/contracts/crowdsale/emission/MintedCrowdsale.sol";
import "@openzeppelin/contracts/crowdsale/validation/CappedCrowdsale.sol";
import "@openzeppelin/contracts/crowdsale/validation/TimedCrowdsale.sol";
import "@openzeppelin/contracts/crowdsale/validation/WhitelistCrowdsale.sol";
import "@openzeppelin/contracts/crowdsale/distribution/RefundablePostDeliveryCrowdsale.sol";

/** The SLPRcoinCrowdSale contract inherits standards and properties from the following Crowdsale contracts:
 * 
 * CROWDSALE: Base architecture for crowdsales. Sets up a wallet to collect funds. Framework to send Ether to the Smart Contract &
 * compute the amount of Tokens disbursed based on the rate.
 * 
 * MINTEDCROWDSALE: The contract will mint Tokens anytime they are purchased, instead of having a preset total supply.
 * The total amount of tokens in distribution is determined by how many are actually sold.
 * 
 * TIMEDCROWDSALE: Sets parameters to start (openingTime) and end (closingTime) the Crowdsale.
 * 
 * CAPPEDCROWDSALE: Sets the max amount of runds it can raise in the Crowdsale.
 * 
 * WHITELISTCROWDSALE: Sets parameters to fullfill KYC requirements. Match contributions in the Crowdsale to real people. Investors 
 * must be WhiteListed before they can purchase Tokens.
 * 
 * STAGED CROWDSALE: Creates 2 stages (pre-sale and public sale) to set rates where investors can receive more Tokens in the pre-sale
 * vs the public sale. In pre-sale, funds go to the wallet, not to the refund escrow vault.
 * 
 * REFUNDABLECROWDSALE: Sets a minimum goal of funds to raise in the Crowdsale. If goal isn't reached, it will refund investors.
 * 
 * DISTRIBUTION & VESTING: Set amount of Tokens to distribute to Founders, Company, and Public.
 */

contract SLPRcoinCrowdSale is Crowdsale, MintedCrowdsale, CappedCrowdsale, TimedCrowdsale, WhitelistCrowdsale, RefundablePostDeliveryCrowdsale {
    //address token_sale_address;
    //address owner = msg.sender;
    //address token_sale_address;

    // Track investor contributions. Set Minimum and Maximum contributions.
    uint256 public investorMinCap = 2000000000000000; // 0.002 ether
    uint256 public investorHardCap = 50000000000000000000; // 50 ether
    // Create a mapping to hold record of investor contributions.
    mapping(address => uint256) public contributions;
    

    // Set Crowdsale Stages to manage presale and public token rates
    enum CrowdsaleStage { PreICO, ICO }
    // Set default stage to presale stage
    CrowdsaleStage public stage = CrowdsaleStage.PreICO;

    // Set token Distribution percentages for public sale and Token Resereves 
    // (Public: 70%, Founders, Foundation, Partners: 10% each)
    uint256 public tokenSalePercentage   = 70;
    uint256 public foundersPercentage    = 10;
    uint256 public foundationPercentage  = 10;
    uint256 public partnersPercentage    = 10;
    uint256 private _weiRaised = 0;
    
    // Create addresses for  Token Reserve funds
    address public foundersFund;
    address public foundationFund;
    address public partnersFund;
    
    // Create token Time Lock addreses to set token holding time frame
    uint256 public releaseTime;
    address public foundersTimelock;
    address public foundationTimelock;
    address public partnersTimelock;
    
    // Create the contract's constructor to pass parameters from inherited contracts 
    // Crowdsale(rate, wallet, token), CappedCrowdsale(cap), TimedCrowdsale(openingTime, closingTime), RefundableCrowdsale(goal)
    // Include addresses for investors' token reserve funds and for releaseTime
    constructor(
        uint256         rate,
        address payable wallet,
        SLPRcoin        token,
        uint256         cap,
        uint256         openingTime,
        uint256         closingTime,
        uint256         goal,
        address         _foundersFund,
        address         _foundationFund,
        address         _partnersFund,
        uint256         _releaseTime
        )
        
        Crowdsale(rate, wallet, token)
        CappedCrowdsale(cap)
        TimedCrowdsale(openingTime, closingTime)
        RefundableCrowdsale(goal)
        public
        {
            require(goal <= cap);
            foundersFund    =   _foundersFund;
            foundationFund  =   _foundationFund;
            partnersFund    =   _partnersFund;
            releaseTime     =   _releaseTime;
        }
    
    /**
    * Create public function to view current investor contriutions by address 
    * @dev Returns the amount contributed so far by a specific user.
    * @param _beneficiary Address of contributor
    * @return User contribution so far
    */
    function getUserContribution(address payable _beneficiary)
    public view returns (uint256)
    {
        return contributions[_beneficiary];
        
    }
    

    /**
     *@dev Allows admin to update the crowdsale stage
     * @param _stage Crowdsale stage
     */
    function setCrowdsaleStage(uint _stage) public {
        //require(msg.sender == owner, "You are not the owner");
        
        if(uint(CrowdsaleStage.PreICO) == _stage) {
            stage = CrowdsaleStage.PreICO;
        } else if (uint(CrowdsaleStage.ICO) == _stage) {
            stage = CrowdsaleStage.ICO;
        }
         if(stage == CrowdsaleStage.PreICO) {
             uint256 rate = 500;
         } else if (stage == CrowdsaleStage.ICO) {
             uint256 rate = 250;
         }
    }
    
    /**
     * @dev forwards funds to the wallet during the PreICO stage, then the refund vault during ICO stage
     */
    function _forwardFunds(address payable wallet) internal {
         if(stage == CrowdsaleStage.PreICO) {
             wallet.transfer(msg.value);
         } else if (stage == CrowdsaleStage.ICO) {
             super._forwardFunds();
         }
    }
    
    
    /**
    * @dev Extend parent behavior requiring purchase to respect investor min/max funding cap.
    * @param _beneficiary Token purchaser
    * @param _weiAmount Amount of wei contributed
    */
    function _preValidatePurchase(
        address payable _beneficiary, 
        uint256 _weiAmount
        ) 
        internal 
        {
        super._preValidatePurchase(_beneficiary, _weiAmount);
        uint256 _existingContribution = contributions[_beneficiary];
        uint256 _newContribution = _existingContribution.add(_weiAmount);
        require(_newContribution >= investorMinCap && _newContribution <= investorHardCap);
        contributions[_beneficiary] = _newContribution;
        
    }
    
    /**
     * @return the amount of wei raised.
     */
    function fundsRaised() public view returns (uint256) {
        return _weiRaised;
    }
    
    function _buyTokens(address beneficiary, uint256 amount) public nonReentrant payable {
        // super.buyTokens(beneficiary);
        uint256 weiAmount = amount;
        _preValidatePurchase(beneficiary, weiAmount);
    
        // calculate token amount to be created
        uint256 tokens = _getTokenAmount(weiAmount);

        // update state
        _weiRaised = _weiRaised.add(weiAmount);

        _processPurchase(beneficiary, tokens);
        emit TokensPurchased(_msgSender(), beneficiary, weiAmount, tokens);

        _updatePurchasingState(beneficiary, weiAmount);

        _forwardFunds();
        _postValidatePurchase(beneficiary, weiAmount);
    }
    
    
    /**
    *@dev enables token transfers, called when owner calls finalize()
    */
    function finalization(  ) internal {
        /**Future enhancements below will enable token transfers when goal is reached and Distribution to preset funds once 
         * releaseTime expires
         */
        
        //if(goalReached()) {
            //ERC20Mintable _mintableToken = ERC20Mintable(token);
            //uint256 _alreadyMinted = _mintableToken.totalSupply();
            
            //uint256 _finalTotalSupply = _alreadyMinted.div(tokenSalePercentage).mul(100);
            
            //foundersTimelock    = new TokenTimelock(token, foundersFund, releaseTime);
            //foundationTimelock  = new TokenTimelock(token, foundationFund, releaseTime);
            //partnersTimelock    = new TokenTimelock(token, partnersFund, releaseTime);
            
            //_mintableToken.mint(address(foundersTimelock),      _finalTotalSupply.mul(foundersPercentage).div(100));
            //_mintableToken.mint(address(foundationTimelock),    _finalTotalSupply.mul(foundationPercentage).div(100));
            //_mintableToken.mint(address(partnersTimelock),      _finalTotalSupply.mul(partnersPercentage).div(100));
            
            //_mintableToken.mint(foundersTimelock,      _finalTotalSupply.div(foundersPercentage));
            //_mintableToken.mint(foundationTimelock,    _finalTotalSupply.div(foundationPercentage));
            //_mintableToken.mint(partnersTimelock,      _finalTotalSupply.div(partnersPercentage));
            
            //_mintableToken.mint();
            
            //ERC20Pausable _pausableToken = ERC20Pausable(token);
            //_pausableToken.unpause();
            //_pausableToken.transferOwnership(wallet);
            
            //_mintableToken.transferOwnership(wallet);
        //}    
            
        super._finalization();    
    }
    
    /**
     * @dev fallback function
     */
    function () external payable {
    }
        
    
}

contract SLPRcoinCrowdSaleDeployer {

    address public token_sale_address;
    address public token_address;
    
    uint fakenow = now;

    constructor(
        // @TODO: Fill in the constructor parameters!
        string memory   name,
        string memory   symbol,
        uint256         rate,
        address payable wallet,
        //SLPRcoin        token,
        uint256         cap,
        //uint256         openingTime,
        //uint256         closingTime,
        uint256         goal,
        address         _foundersFund,
        address         _foundationFund,
        address         _partnersFund
        //uint256         _releaseTime
        
        // block_timestamp "now" will be passed as opening_time directly in the function call instead of creating a variable
        //closing time is also passed via now + the duration. in this case we made the duration 1 hour for testing purposes
        
    )
        public
    {
        // @TODO: create the SLPRcoin and keep its address handy
            // Create the SLPRcoin by defining a variable like `SLPRcoin token` and setting it to equal new SLPRcoin(). 
            // Inside of the parameters of new SLPRcoin, pass in the name and symbol variables. 
            // For the initial_supply variable that SLPRcoin expects, pass in 0

        SLPRcoin token = new SLPRcoin(name, symbol, 0);

            // Then, store the address of the token by using token_address = address(token). 
            // This will allow us to easily fetch the token's address for later from the deploying contract.
        
        token_address = address(token);
        
        // @TODO: create the SLPRcoinCrowdSale and tell it about the token, 
        // set the goal, and set the open and close times to now and now + 24 weeks.

        SLPRcoinCrowdSale slpr_sale = new SLPRcoinCrowdSale(rate, wallet, token, cap, fakenow, fakenow + 1 days, goal, _foundersFund, _foundationFund, _partnersFund, fakenow + 104 weeks);
        token_sale_address = address(slpr_sale);
        
        // make the SLPRcoinCrowdSale contract a minter, then have the SLPRcoinCrowdSaleDeployer renounce its minter role
        token.addMinter(token_sale_address);
        token.addMinter(wallet);
        token.renounceMinter();
        
        // make the SLPRcoinCrowdSale contract the Whitelist Admin, then have the SLPRcoinCrowdSaleDeployer renounce its 
        // Whitelist Admin role.
        slpr_sale.addWhitelistAdmin(token_sale_address);
        slpr_sale.addWhitelistAdmin(wallet);
        slpr_sale.renounceWhitelistAdmin();
        
        // Give owner rights to the SLPRcoinCrowdSale contract
        //SLPRcoinCrowdSaleDeployer.transferOwnership(wallet);
    }
}
