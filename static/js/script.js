document.addEventListener("DOMContentLoaded", function () {
  const executeCommand = async (ip, username, password, command) => {
    try {
      // Use an API or backend service to execute the SSH command
      const response = await fetch("/execute-command", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ip, username, password, command }),
      });

      const result = await response.json();
      if (result.success) {
        alert("Command executed successfully!");
      } else {
        alert(`Error: ${result.error}`);
      }
    } catch (error) {
      alert(
        "Failed to execute command. Ensure your backend service is running."
      );
    }
  };

  document
    .getElementById("connect-btn")
    .addEventListener("click", async function () {
      const ip = document.getElementById("ip").value;
      const username = document.getElementById("username").value;
      const password = document.getElementById("password").value;
      if (ip && username && password) {
        try {
          // Send a test command to the backend
          const response = await fetch("/check-connection", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ ip, username, password }),
          });

          const result = await response.json();
          if (result.success) {
            document.getElementById("status").textContent = "Master Node Ready";
            document.getElementById("status").style.color = "green";
          } else {
            document.getElementById(
              "status"
            ).textContent = `Error: ${result.error}`;
            document.getElementById("status").style.color = "red";
          }
        } catch (error) {
          document.getElementById("status").textContent = "Connection Failed";
          document.getElementById("status").style.color = "red";
        }
      } else {
        document.getElementById("status").textContent = "Invalid Input";
        document.getElementById("status").style.color = "red";
      }
    });

  document.getElementById("reboot_btn").addEventListener("click", function () {
    alert("reboot");
    console.log("Reboot");
    const ip = document.getElementById("ip").value;
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    const command = "reboot_lg"; // command
    executeCommand(ip, username, password, command);
  });

  document
    .getElementById("relaunch-btn")
    .addEventListener("click", function () {
      const ip = document.getElementById("ip").value;
      const username = document.getElementById("username").value;
      const password = document.getElementById("password").value;
      const command = "lg_relaunch"; //command
      executeCommand(ip, username, password, command);
    });

    document
    .getElementById("power_off_btn")
    .addEventListener("click", function () {
      const ip = document.getElementById("ip").value;
      const username = document.getElementById("username").value;
      const password = document.getElementById("password").value;
      console.log("POWER OFF");
      const command = "power_off__lg"; // command
      executeCommand(ip, username, password, command);
    });

  document
    .getElementById("clear-logo-btn")
    .addEventListener("click", function () {
      const ip = document.getElementById("ip").value;
      const username = document.getElementById("username").value;
      const password = document.getElementById("password").value;
      const command = "clear_logo"; // command
      executeCommand(ip, username, password, command);
    });

  document
    .getElementById("show-logo-btn")
    .addEventListener("click", function () {
      const ip = document.getElementById("ip").value;
      const username = document.getElementById("username").value;
      const password = document.getElementById("password").value;
      const command = "show_logo"; // command
      executeCommand(ip, username, password, command);
    });

  document
    .getElementById("show-kml-btn")
    .addEventListener("click", function () {
      const ip = document.getElementById("ip").value;
      const username = document.getElementById("username").value;
      const password = document.getElementById("password").value;
      const command = "show_kml"; // command
      executeCommand(ip, username, password, command);
    });

  document
    .getElementById("clear-kml-btn")
    .addEventListener("click", function () {
      const ip = document.getElementById("ip").value;
      const username = document.getElementById("username").value;
      const password = document.getElementById("password").value;
      const command = "clear_kml"; // command
      executeCommand(ip, username, password, command);
    });

  
});
