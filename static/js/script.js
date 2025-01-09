document.addEventListener("DOMContentLoaded", function () {
  const executeCommand = async (ip, username, password, command,machine_count) => {
    try {
      // Use an API or backend service to execute the SSH command
      const response = await fetch("/execute-command", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ip, username, password, command, machine_count }),
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
      const machine_count = document.getElementById("nodes").value;
      if (ip && username && password) {
        try {
          // Send a test command to the backend
          const response = await fetch("/check-connection", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ ip, username, password,machine_count }),
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
    const machine_count = document.getElementById("nodes").value;
    executeCommand(ip, username, password, command,machine_count);
  });

  document
    .getElementById("relaunch-btn")
    .addEventListener("click", function () {
      const ip = document.getElementById("ip").value;
      const username = document.getElementById("username").value;
      const password = document.getElementById("password").value;
      const command = "lg_relaunch"; //command
      const machine_count = document.getElementById("nodes").value;
      executeCommand(ip, username, password, command,machine_count);
    });

    document
    .getElementById("power_off_btn")
    .addEventListener("click", function () {
      const ip = document.getElementById("ip").value;
      const username = document.getElementById("username").value;
      const password = document.getElementById("password").value;
      console.log("POWER OFF");
      const command = "power_off__lg"; // command
      const machine_count = document.getElementById("nodes").value;
      executeCommand(ip, username, password, command,machine_count);
    });

  document
    .getElementById("clear-logo-btn")
    .addEventListener("click", function () {
      const ip = document.getElementById("ip").value;
      const username = document.getElementById("username").value;
      const password = document.getElementById("password").value;
      const command = "clear_logo"; // command
      const machine_count = document.getElementById("nodes").value;
      executeCommand(ip, username, password, command,machine_count);
    });

  document
    .getElementById("show-logo-btn")
    .addEventListener("click", function () {
      const ip = document.getElementById("ip").value;
      const username = document.getElementById("username").value;
      const password = document.getElementById("password").value;
      const command = "show_logo"; // command
      const machine_count = document.getElementById("nodes").value;
      executeCommand(ip, username, password, command,machine_count);
    });

  document
    .getElementById("show-kml-btn")
    .addEventListener("click", function () {
      const ip = document.getElementById("ip").value;
      const username = document.getElementById("username").value;
      const password = document.getElementById("password").value;
      const command = "show_kml"; // command
      const machine_count = document.getElementById("nodes").value;
      executeCommand(ip, username, password, command,machine_count);
    });

  document
    .getElementById("clear-kml-btn")
    .addEventListener("click", function () {
      //alert("KML Being Cleared !!!");
      const ip = document.getElementById("ip").value;
      const username = document.getElementById("username").value;
      const password = document.getElementById("password").value;
      const command = "clear_kml"; // command
      const machine_count = document.getElementById("nodes").value;
      executeCommand(ip, username, password, command,machine_count);
    });

  
});
