// SPDX-License-Identifier: MIT
pragma solidity ^0.8.28;

import "forge-std/Test.sol";
import "../src/BridgeAccountingVulnerable.sol";
import "../src/BridgeAccountingFixed.sol";

contract ReentrantReceiver {
    BridgeAccountingVulnerable public vulnerable;
    bytes32 public messageId;
    uint256 public amount;
    bool public entered;

    constructor(BridgeAccountingVulnerable target) {
        vulnerable = target;
    }

    function arm(bytes32 id, uint256 value) external {
        messageId = id;
        amount = value;
    }

    receive() external payable {
        if (!entered) {
            entered = true;
            vulnerable.execute(messageId, payable(address(this)), amount);
        }
    }
}

contract BridgeRegressionTest is Test {
    function testVulnerableAllowsSameMessageTwiceInOneTransaction() public {
        BridgeAccountingVulnerable bridge = new BridgeAccountingVulnerable();
        ReentrantReceiver receiver = new ReentrantReceiver(bridge);
        uint256 amount = 1 ether;
        bytes32 id = keccak256("demo-message");
        receiver.arm(id, amount);
        vm.deal(address(bridge), 2 ether);
        bridge.execute(id, payable(address(receiver)), amount);
        assertEq(address(receiver).balance, 2 ether);
        assertTrue(bridge.processed(id));
    }

    function testFixedBlocksReentrantReplay() public {
        BridgeAccountingFixed bridge = new BridgeAccountingFixed();
        vm.deal(address(bridge), 2 ether);
        bytes32 id = keccak256("demo-message");
        bridge.execute(id, payable(address(this)), 1 ether);
        assertEq(bridge.processed(id), true);
        vm.expectRevert("already processed");
        bridge.execute(id, payable(address(this)), 1 ether);
    }
}