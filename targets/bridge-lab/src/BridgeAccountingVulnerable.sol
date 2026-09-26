// SPDX-License-Identifier: MIT
pragma solidity ^0.8.28;

contract BridgeAccountingVulnerable {
    mapping(bytes32 => bool) public processed;

    receive() external payable {}

    function execute(
        bytes32 messageId,
        address payable recipient,
        uint256 amount
    ) external {
        require(!processed[messageId], "already processed");
        (bool ok,) = recipient.call{value: amount}("");
        require(ok, "transfer failed");
        processed[messageId] = true;
    }

    function balance() external view returns (uint256) {
        return address(this).balance;
    }
}