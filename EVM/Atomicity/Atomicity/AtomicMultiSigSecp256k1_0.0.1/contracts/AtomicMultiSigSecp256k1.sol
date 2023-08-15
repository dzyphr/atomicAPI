// SPDX-License-Identifier: GPL-3.0-only
pragma solidity >=0.8.0 <0.9.0;

import "ReentrancyGuard.sol";
import "EllipticCurve.sol";


contract AtomicMultiSigSecp256k1 is ReentrancyGuard
{
	event Deposit(address indexed sender, uint amount, uint balance);
        address payable public sender;
        address payable public receiver;
        uint private constant DURATION = 100;
        uint public lockHeight;
        uint256 public gxX;
	uint256 public gxY;

        receive() external payable
        {
                emit Deposit(msg.sender, msg.value, address(this).balance);
        }

        constructor(address payable rec, uint256 gxX_, uint256 gxY_) payable
        {
                require(rec != address(0), "reciever is a null addr");
		require(onCurve(gxX_, gxY_) == true);
                sender = payable(msg.sender);
                receiver = rec;
                lockHeight = block.timestamp + DURATION;
		gxX = gxX_;
		gxY = gxY_;
        }

        function receiverWithdraw(uint256 x) external  nonReentrant
        {
                require(msg.sender == receiver);
		(uint256 checkx, uint256 checky) = ecMulG_Secp256k1(x);
                require(checkx == gxX && checky == gxY);
                (bool sent, ) = receiver.call{value: address(this).balance}("");
                require(sent, "Failed to send !");
        }

        function senderReclaim() external
        {
                require(msg.sender == sender);
                require(block.timestamp >= lockHeight, "timelock has not expired!");
                selfdestruct(sender); //this selfdestruct makes some sense but will replace if its bad practice
        }

	//secp256k1 constants
        uint256 public constant GX =
        0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798;
        uint256 public constant GY =
        0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8;
        uint256 public constant AA = 0;
        uint256 public constant BB = 7;
        uint256 public constant PP =
        0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F;

        function ecMulG_Secp256k1( uint256 k) pure public returns (uint256, uint256)
        {
                return EllipticCurve.ecMul(k, GX, GY,AA,PP);
        }

        function onCurve(uint256 x, uint256 y) pure public returns (bool)
        {
                return EllipticCurve.isOnCurve(x,y,AA,BB,PP);
        }

}
