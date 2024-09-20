// flask_app/static/js/switch_network.js
window.addEventListener("load", function () {
  if (typeof window.ethereum !== "undefined") {
    console.log("MetaMask is installed!");
  } else {
    document.getElementById("status").innerText =
      "MetaMask is not installed. Please install it to continue.";
    return;
  }

  const switchNetworkButton = document.getElementById("switchNetworkButton");
  switchNetworkButton.addEventListener("click", async () => {
    try {
      // Try to switch to the network
      await ethereum.request({
        method: "wallet_switchEthereumChain",
        params: [{ chainId: networkParams.chainId }],
      });
      document.getElementById("status").innerText =
        "Network switched successfully!";
      // Proceed to register wallet
      registerWallet();
    } catch (switchError) {
      if (switchError.code === 4902) {
        // The network is not added yet, so add it
        try {
          await ethereum.request({
            method: "wallet_addEthereumChain",
            params: [networkParams],
          });
          document.getElementById("status").innerText =
            "Network added and switched successfully!";
          // Proceed to register wallet
          registerWallet();
        } catch (addError) {
          console.error("Error adding network:", addError);
          document.getElementById("status").innerText =
            "Failed to add network.";
        }
      } else {
        console.error("Error switching network:", switchError);
        document.getElementById("status").innerText =
         switchError.message;
      }
    }
  });

  async function registerWallet() {
    try {
      const accounts = await ethereum.request({
        method: "eth_requestAccounts",
      });
      const walletAddress = accounts[0];

      // Send wallet address and Discord ID to backend
      fetch("/register_wallet", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          discord_user_id: discordUserId,
          wallet_address: walletAddress,
        }),
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.status === "success") {
            document.getElementById("status").innerText +=
              "\nWallet registered successfully!";
          } else {
            document.getElementById("status").innerText +=
              "\nFailed to register wallet: " + data.message;
          }
        })
        .catch((error) => {
          console.error("Error:", error);
          document.getElementById("status").innerText += "\nAn error occurred.";
        });
    } catch (error) {
      console.error("Error requesting accounts:", error);
      document.getElementById("status").innerText +=
        "\nFailed to get wallet address.";
    }
  }
});
