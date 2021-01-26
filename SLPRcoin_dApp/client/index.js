import Web3 from 'web3';
import ContractDeployer from '../build/contracts/SLPRcoinCrowdSaleDeployer.json';
import TokenSale from '../build/contracts/SLPRcoinCrowdSale.json';
import Token from '../build/contracts/SLPRcoin.json';

let web3;
let contractdeployer;
let tokensale;
let token;
let tokensale_methods =[];
let token_methods=[];
let contracts;
let tokensale_address = '0xC15346b66F8C7F046d476852C0cA6a1777006872';
let token_address = '0x012eC52f7a99E0F4D0B2f1a00Da37aE2e18aE486';

const initWeb3 = () => {
  return new Promise((resolve, reject) => {
    if(typeof window.ethereum !== 'undefined') {
      const web3 = new Web3(window.ethereum);
      window.ethereum.enable()
        .then(() => {
          resolve(
            new Web3(window.ethereum)
          );
        })
        .catch(e => {
          reject(e);
        });
      return;
    }
    if(typeof window.web3 !== 'undefined') {
      return resolve(
        new Web3(window.web3.currentProvider)
      );
    }
    resolve(new Web3('http://localhost:9545'));
  });
};

const initContract = () => {
      const deploymentKey = Object.keys(ContractDeployer.networks);
      // console.log(deploymentKey);
      contractdeployer = new web3.eth.Contract(
        ContractDeployer.abi, 
        ContractDeployer
        .networks[deploymentKey]
        .address
        );
        // console.log(contractdeployer); 
        contractdeployer.methods.token_sale_address().call()
        .then(function (result) {
          //tokensale_address = result;
          console.log(result);}).catch(_e => {
            console.log(_e);
          });
        contractdeployer.methods.token_address().call()
        .then(function (result) {
          //token_address=result;
          console.log(result);})
          .catch(_e => {
            console.log(_e);
          });
        return  [new web3.eth.Contract(TokenSale.abi, tokensale_address),
        new web3.eth.Contract(Token.abi, token_address)];
      };

const initApp = () => {
  var $element = document;
  var $source = document;
  let accounts = [];

  web3.eth.getAccounts()
  .then(_accounts => {
	accounts = _accounts;
	
  });

// dynamic event handler
    document.addEventListener('click', function(evt){
        if(evt.target.parentElement.name.includes('form')){
          $element = evt.target.parentElement;
          $source = evt.target.parentElement.name.split("-")[1];
          evt.target.removeEventListener('click', document);
            
        };
      }); 

    $element.addEventListener('submit', (e) => {
    e.preventDefault();
        if ($source === "0"){
          if (e.target.elements.length > 1){
            var params = [];
            var l;
            for (l=0; l < e.target.elements.length-1; l++){
              params.push(e.target.elements[l].value);
            }
          
            if(params.length > 1){
                    //window.prompt(e.target.id);
                    tokensale.methods[e.target.id.split("-")[0]].apply(this, params).send({from: accounts[0]})
                    .on('transactionHash', function(hash){
                      document.getElementById(e.target.id + "Result").innerHTML = json.dumps(hash);
                    })
                    .on('receipt', function(receipt){
                      document.getElementById(e.target.id + "Result").innerHTML = receipt;
                    })
                    .on('confirmation', function(confirmationNumber, receipt){
                      document.getElementById(e.target.id + "Result").innerHTML = `Your Transaction Confirmation # is: ${confirmationNumber} and receipt number is : ${receipt}`; })
                    .on('error', function(error){
                      document.getElementById(e.target.id + "Result").innerHTML = error;
                    });
            }
            else {
              params = params.pop();
            }
            //window.prompt(e.target.id);
            tokensale.methods[e.target.id](params).call()
            .then(function (result) {
                  document.getElementById(e.target.id + "Result").innerHTML = result;
                })
                .catch(_e => {
                  console.log(_e);
                  document.getElementById(e.target.id + "Result").innerHTML = `Ooops... there was an error while trying to get Data...`;
                });
            }
          else{
            //window.prompt(e.target.id);
            //var cfunc = e.target.id;
            //console.log(tokensale.methods[cfunc]().call());
            tokensale.methods[e.target.id]().call()
            .then(function (result) {
              //console.log(result);
                 document.getElementById(e.target.id + "Result").innerHTML = result;
                })
                .catch(_e => {
                  console.log(_e);
                  document.getElementById(e.target.id + "Result").innerHTML = `Ooops... there was an error while trying to get Data...`;
                });
          };
        }
        else if ($source === "1"){
          if (e.target.elements.length > 1){
              let params = [];
              var l;
              for (l=0; l < e.target.elements.length -1; l++){
                params.push(e.target.elements[l].value);
              }
              if(params.length > 1){
                //window.prompt(params);
                  token.methods[e.target.id.split("-")[0]].apply(this, params).send({from: accounts[0]})
                  .on('transactionHash', function(hash){
                    document.getElementById(e.target.id + "Result").innerHTML = json.dumps(hash);
                  })
                  .on('receipt', function(receipt){
                    document.getElementById(e.target.id + "Result").innerHTML = receipt;
                  })
                  .on('confirmation', function(confirmationNumber, receipt){
                    document.getElementById(e.target.id + "Result").innerHTML = `Your Transaction Confirmation # is: ${confirmationNumber} and receipt number is : ${receipt}`; })
                  .on('error', function(error){
                    document.getElementById(e.target.id + "Result").innerHTML = error;
                  });
              }
              else {
                params = params.pop();
              }
              //window.prompt(e.target.id);
              token.methods[e.target.id](params).call()
              .then(function (result) {
                    document.getElementById(e.target.id + "Result").innerHTML = result;
                    })
                  .catch(_e => {
                    console.log(_e);
                    document.getElementById(e.target.id + "Result").innerHTML = `Ooops... there was an error while trying to get Data...`;
                  });
          }
          else{
            //window.prompt(e.target.id.split("_")[0]);
            //var cfunc = e.target.id;
            //console.log(token.methods[cfunc]().call());
            token.methods[e.target.id]().call()
            .then(function (result) {
                //console.log(result);
                  document.getElementById(e.target.id + "Result").innerHTML = result;
                })
                .catch(_e => {
                  console.log(_e);
                  document.getElementById(e.target.id + "Result").innerHTML = `Ooops... there was an error while trying to get Data...`;
                });
            };
        };
        // else if ($source === "8"){
        //     'use strict';
        //     const fs = require('fs');
        //     var formData = JSON.stringify($("registrationform_8").serializeArray());
        //     fs.writeFileSync('file.json', data, finished);
        //     function finished(err){
        //         console.log('success');
        //     }
        // };
  });
};

document.addEventListener('DOMContentLoaded', () => {
   initWeb3()
    .then(_web3 => {
      web3 = _web3;
      contracts = initContract();
      tokensale=contracts[0];
      token=contracts[1];
      //console.log(tokensale_address);
      //console.log(token_address);
      
      loadform()
      
    initApp(); 
  })
	.catch(e => console.log(e.message));
});

const loadform = () => {
  const $contractaddress = document.getElementById("ContractAddress"); 
  $contractaddress.innerHTML = `Coin Sale Address: ${tokensale_address} <br> Coin Address : ${token_address}`;
  var k;
  for (k=0; k < contracts.length; k++){
    var methods = contracts[k].methods;
    
    methods.f = function f() {};
    for(var method in methods){
      if (!method.startsWith('0x') && method.includes(')') && method.length > 2) {
        if(k==0){
          tokensale_methods.push(method);
          var func_count = tokensale_methods.length;
           var func_names = tokensale_methods;
        }
        else if(!tokensale_methods.includes(method)){
          token_methods.push(method);
          var func_count = token_methods.length;
           var func_names = token_methods;
        };
      };
  };
  //console.log(func_names);
  var i; 
    for(i=0; i < Number(func_count); i++){
        var func_args = func_names[i].split("(")[1].split(")")[0];
        if (func_args.includes(",")){
          func_args = func_args.split(",");
        };
        var form = document.createElement("form");
        form.setAttribute("name", func_names[i].split("(")[0]+"form-"+k); 
        form.setAttribute("id", func_names[i].split("(")[0]); 
        form.setAttribute("action", "");
        form.setAttribute("onsubmit", "return false");
        //var title = document.createElement("h4", func_names[i]);
        
        if (typeof func_args =='object' && func_args.length > 0){
          var j;
          for (j=0; j <= func_args.length; j++){
            if (func_args[j]){
              var ID = document.createElement("input");
              ID.setAttribute("id", func_args[j] +i+j); 
              ID.setAttribute("type", "text"); 
              ID.setAttribute("name", func_args[j]); 
              ID.setAttribute("placeholder", func_args[j]); 
              form.append(ID);
            };
          };
        };

        if (func_args.length > 0 && typeof func_args !=='object'){
          var ID = document.createElement("input");
          ID.setAttribute("id", func_args + i + func_count); 
          ID.setAttribute("type", "text"); 
          ID.setAttribute("name", func_args); 
          ID.setAttribute("placeholder", func_args); 
          form.append(ID);
        };
      
        // if(func_names[i].split("(")[0].includes("buy")){
        //   var token = document.createElement("input");
        //   token.setAttribute("id", "Amount"); 
        //   token.setAttribute("type", "text"); 
        //   token.setAttribute("name", "Amount"); 
        //   token.setAttribute("placeholder", "Amount in Ether"); 
        //   form.append(token);
        // };

        var s = document.createElement("input"); 
        s.setAttribute("type", "submit"); 
        s.setAttribute("id", func_names[i].split("(")[0]+"Submit"); 
        s.setAttribute("class", "btn btn-primary");
        s.setAttribute("value", func_names[i].split("(")[0]); 
        if (func_args.length > 0){
          s.setAttribute("background-color", "#f44336"); 
        };

        var result = document.createElement("p");
        result.setAttribute("id", func_names[i].split("(")[0]+"Result");
        form.append(s);
        form.append(result);  
        if(["buyTokens", "claimRefund", "balanceOf", "token", "name", "symbol", "rate", "isWhitelistAdmin", "isWhitelisted", 
         "isOpen", "closingTime",  "decimals"].includes(func_names[i].split("(")[0])){
          document.getElementById('tokens').append(form);
        }else if(["addWhitelistAdmin", "addWhitelisted", "contributions", "removeWhitelisted", "renounceWhitelistAdmin", "renounceWhitelisted", "setCrowdsaleStage", "addMinter", "addPauser", "pause", "unpause", "isMinter", "renounceMinter", "decreaseAllowance", "increaseAllowance", "Allowance",
        "approve", "finalize", "mint", "transfer", "transferFrom", "withdrawTokens", "getUserContribution", "allowance", "isPauser", "renouncePauser", "_buyTokens"].includes(func_names[i].split("(")[0])){
          document.getElementById('supply').append(form);
        }else {
        document.getElementById('contract').append(form);
        };
      document.styleSheets[0];
    };
  };
};
