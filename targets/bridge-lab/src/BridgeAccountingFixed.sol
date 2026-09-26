// SPDX-License-Identifier: MIT
pragma solidity ^0.8.28;

contract BridgeAccountingFixed {
    mapping(bytes32 => bool) public processed;

    receive() external payable {}

    function execute(
        bytes32 messageId,
        address payable recipient,
        uint256 amount
    ) external {
        require(!processed[messageId], "already processed");
        processed[messageId] = true;
        (bool ok,) = recipient.call{value: amount}("");
        require(ok, "transfer failed");
    }

    function balance() external view returns (uint256) {
        return address(this).balance;
    }
}