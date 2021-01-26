const PupperCoinSaleDeployer = artifacts.require('SLPRcoinCrowdSaleDeployer');
const PupperCoinSale = artifacts.require('SLPRcoinCrowdSale');
const PupperCoin = artifacts.require('SLPRcoin');

contract('PupperCoinSaleDeployer', () => {
 
	it('should return deployed contract addresses', async () => {
		const pupperCoinSaleDeployer = await PupperCoinSaleDeployer.deployed();
		console.log(pupperCoinSaleDeployer.address);
		assert(pupperCoinSaleDeployer.address !== '');
		const sale_address = await pupperCoinSaleDeployer.token_sale_address();
		console.log(sale_address);
		assert(sale_address !== '');
		const token_address = await pupperCoinSaleDeployer.token_address();		
		console.log(token_address );
		assert(token_address !== '');
		let coinSale = await PupperCoinSale.at(sale_address);
		const wallet = await coinSale.wallet();	
		console.log(wallet);
		assert(wallet !== '');	
		let token = await PupperCoin.at(token_address);
		const name = await token.name();	
		console.log(name);
		assert(name !== '');
		const symbol = await token.symbol();	
		console.log(symbol);
		assert(symbol !== '');		

		
	});

});

