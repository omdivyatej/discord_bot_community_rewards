// flask_app/static/js/app.js
window.addEventListener("load", function () {
  if (typeof window.ethereum !== "undefined") {
    console.log("MetaMask is installed!");
  } else {
    document.getElementById("status").innerText =
      "MetaMask is not installed. Please install it to continue.";
    return;
  }

  const connectButton = document.getElementById("connectButton");
  connectButton.addEventListener("click", async () => {
    const accounts = await ethereum.request({ method: "eth_requestAccounts" });
    const walletAddress = accounts[0];
    const discordUserId = window.discordUserId;

    console.log("Discord User ID:", discordUserId);
    console.log("Wallet Address:", walletAddress);

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
          document.getElementById("status").innerText =
            "Wallet connected successfully!";
        } else {
          document.getElementById("status").innerText =
            "Failed to connect wallet: " + data.message;
        }
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  });
});
