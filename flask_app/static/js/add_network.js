// flask_app/static/js/add_network.js
window.addEventListener("load", function () {
  if (typeof window.ethereum !== "undefined") {
    console.log("MetaMask is installed!");
  } else {
    document.getElementById("status").innerText =
      "MetaMask is not installed. Please install it to continue.";
    return;
  }

  const addNetworkButton = document.getElementById("addNetworkButton");
  addNetworkButton.addEventListener("click", async () => {
    try {
      await ethereum.request({
        method: "wallet_addEthereumChain",
        params: [networkParams],
      });
      document.getElementById("status").innerText =
        "Network added successfully!";
    } catch (error) {
      console.error("Error:", error);
      document.getElementById("status").innerText = error.message;
    }
  });
});
