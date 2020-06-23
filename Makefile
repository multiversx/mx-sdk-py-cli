
test-cli: test-cli-accounts, test-cli-network
	
	python3 -m erdpy.cli cost gas-price --proxy=https://api.elrond.com
	python3 -m erdpy.cli cost transaction move-balance --data="foobar" --proxy="https://api.elrond.com"

test-cli-accounts:
	python3 -m erdpy.cli account get --address="erd188nydpkagtpwvfklkl2tn0w6g40zdxkwfgwpjqc2a2m2n7ne9g8q2t22sr" --proxy="https://api.elrond.com"
	python3 -m erdpy.cli account get --nonce --address="erd188nydpkagtpwvfklkl2tn0w6g40zdxkwfgwpjqc2a2m2n7ne9g8q2t22sr" --proxy="https://api.elrond.com"
	python3 -m erdpy.cli account get --balance --address="erd188nydpkagtpwvfklkl2tn0w6g40zdxkwfgwpjqc2a2m2n7ne9g8q2t22sr" --proxy="https://api.elrond.com"
	python3 -m erdpy.cli account get-transactions --address="erd188nydpkagtpwvfklkl2tn0w6g40zdxkwfgwpjqc2a2m2n7ne9g8q2t22sr" --proxy="https://api.elrond.com"

test-cli-network:
	#python3 -m erdpy.cli network num-shards --proxy="https://api.elrond.com"
	#python3 -m erdpy.cli network chain-id --proxy="https://api.elrond.com"
	#python3 -m erdpy.cli network last-block-nonce --shard-id="1" --proxy="https://api.elrond.com"
	python3 -m erdpy.cli network meta-nonce --proxy="https://api.elrond.com"
	python3 -m erdpy.cli network meta-block --proxy="https://api.elrond.com" --nonce=1
	#python3 -m erdpy.cli network meta-nonce --proxy="http://localhost:8001"
	#python3 -m erdpy.cli network meta-block --proxy="http://localhost:8001" --nonce=1

test-cli-blockatlas:
	python3 -m erdpy.cli blockatlas --url="http://localhost:8420" --coin="elrond" current-block-number
	python3 -m erdpy.cli blockatlas --url="http://localhost:8420" --coin="elrond" block-by-number --number=42
	python3 -m erdpy.cli blockatlas --url="http://localhost:8420" --coin="elrond" transactions --address="alice" 

test-cli-validators:
	python3 -m erdpy.cli --verbose stake --pem="./examples/keys/alice.pem" --number-of-nodes=1 --nodes-public-keys="blsKey1" --value="2500000000000000000000000" --proxy=https://api.elrond.com --reward-address="erd1l453hd0gt5gzdp7czpuall8ggt2dcv5zwmfdf3sd3lguxseux2fsmsgldz"
	python3 -m erdpy.cli --verbose unstake --pem="./examples/keys/alice.pem" --nodes-public-keys="blsKey1" --proxy=https://api.elrond.com
	python3 -m erdpy.cli --verbose unbond --pem="./examples/keys/alice.pem" --nodes-public-keys="blsKey1" --proxy=https://api.elrond.com
	python3 -m erdpy.cli --verbose unjail --pem="./examples/keys/alice.pem" --value=500000000000000000000 --nodes-public-keys="blsKey1" --proxy=https://api.elrond.com
	python3 -m erdpy.cli --verbose change-reward-address --pem="./examples/keys/alice.pem" --reward-address="erd1l453hd0gt5gzdp7czpuall8ggt2dcv5zwmfdf3sd3lguxseux2fsmsgldz" --proxy=https://api.elrond.com

test-cli-dispatcher:
	python3 -m erdpy.cli dispatcher enqueue --value="100" --receiver="erd1cux02zersde0l7hhklzhywcxk4u9n4py5tdxyx7vrvhnza2r4gmq4vw35r" --data="foo" --gas-price=200000000000 --gas-limit=50000000
	python3 -m erdpy.cli dispatcher enqueue --value="200" --receiver="erd1cux02zersde0l7hhklzhywcxk4u9n4py5tdxyx7vrvhnza2r4gmq4vw35r" --data="foo" --gas-price=200000000000 --gas-limit=50000000
	python3 -m erdpy.cli dispatcher enqueue --value="300" --receiver="erd1cux02zersde0l7hhklzhywcxk4u9n4py5tdxyx7vrvhnza2r4gmq4vw35r" --data="foo" --gas-price=200000000000 --gas-limit=50000000
	python3 -m erdpy.cli --verbose dispatcher dispatch --proxy="https://api.elrond.com" --pem="./examples/keys/alice.pem"
	#python3 -m erdpy.cli --verbose dispatcher dispatch-continuously --interval=1 --proxy="https://api.elrond.com" --pem="./examples/keys/alice.pem"


test-deployment:
	python3 -m examples.mycounter_testnet --proxy=https://api.elrond.com --pem=./examples/keys/alice.pem

