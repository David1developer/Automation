function clearFile(inputId, displayId, iconId) {
  document.getElementById(inputId).value = "";
  document.getElementById(displayId).value = "";
  if (iconId) document.getElementById(iconId).style.display = "none";
}

function showFileName(inputId, displayId, iconId) {
  const input = document.getElementById(inputId);
  const display = document.getElementById(displayId);
  const icon = document.getElementById(iconId);
  if (input.files.length > 0) {
    let name = input.files[0].webkitRelativePath || input.files[0].name;
    // For folder upload, show folder name
    if (input.files[0].webkitRelativePath) {
      name = input.files[0].webkitRelativePath.split("/")[0];
    }
    display.value = name;
    if (icon) icon.style.display = "inline-block";
  }
}
// Frontend automation control for Flask backend

function getSettings() {
  const headless = document.querySelector('input[name="headless"]').checked;
  const threads =
    parseInt(document.querySelector('input[name="threads"]').value) || 1;
  const strategy = document.querySelector('select[name="strategy"]').value;
  const mention = document.querySelector('input[name="mention"]').value;
  const platform = document.querySelector('select[name="platform"]').value;
  const category = document.querySelector('select[name="category"]').value;
  const format = document.querySelector('select[name="format"]').value;
  const formatInput = document.querySelector(
    'input[name="format_input"]'
  ).value;
  return {
    headless,
    threads,
    strategy,
    mention,
    platform,
    category,
    format,
    formatInput,
    use_proxies: true, // Always true if proxy section is present
  };
}

window.startAutomation = function () {
  // Check if account folder is selected
  const accountInput = document.getElementById("account_file_input");
  if (!accountInput.files || accountInput.files.length === 0) {
    showFlashMessage(
      "You must upload an account folder before performing this action.",
      "warning"
    );
    return;
  }
  const settings = getSettings();
  showFlashMessage("Automation starting...", "info");
  fetch("/start", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(settings),
  })
    .then((res) => res.json())
    .then((data) => {
      updateLog(data.logs);
      showFlashMessage(
        `Started automating ${
          settings.platform.charAt(0).toUpperCase() + settings.platform.slice(1)
        }!`,
        "success"
      );
    })
    .catch((err) => {
      updateLog([`Error starting automation: ${err}`]);
      showFlashMessage("Failed to start automation.", "danger");
    });
};

window.stopAutomation = function () {
  fetch("/stop", {
    method: "POST",
  })
    .then(() => {
      showFlashMessage("Automation stopped!", "warning");
    })
    .catch((err) => {
      updateLog([`Error stopping automation: ${err}`]);
      showFlashMessage("Failed to stop automation.", "danger");
    });
};

function showFlashMessage(message, category) {
  const wrapper = document.getElementById('flash-center-wrapper');
  if (!wrapper) return;
  const div = document.createElement('div');
  div.className = 'alert alert-' + category;
  div.innerText = message;
  wrapper.appendChild(div);
  setTimeout(() => div.remove(), 4000);
}

document.addEventListener('DOMContentLoaded', function() {
    const startBtn = document.getElementById('start-btn');
    const stopBtn = document.getElementById('stop-btn');

    if (startBtn) {
        startBtn.addEventListener('click', function() {
            fetch('/start', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ /* add settings if needed */ })
            })
            .then(res => res.json())
            .then(data => {
                if (data.flash) {
                    showFlashMessage(data.flash.message, data.flash.category);
                }
                // Optionally update log/status here
            });
        });
    }

    if (stopBtn) {
        stopBtn.addEventListener('click', function() {
            fetch('/stop', {method: 'POST'})
            .then(() => {
                showFlashMessage('Automation stopped', 'warning');
            });
        });
    }
});

// Example usage after AJAX call
function startAutomation() {
  fetch('/start', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ /* your settings here */ })
  })
  .then(response => response.json())
  .then(data => {
      if (data.flash) {
          showFlashMessage(data.flash.message, data.flash.category);
      }
      // ...other logic...
  });
}

function updateLog(logs) {
  const logOutput = document.getElementById("log-output");
  logOutput.value = Array.isArray(logs) ? logs.join("\n") : logs;
}

function fetchLog() {
  fetch("/log")
    .then((res) => res.json())
    .then((data) => {
      updateLog(data.logs);
      if (document.getElementById("progress-card")) {
        document.getElementById(
          "progress-card"
        ).textContent = `${data.current_progress} / ${data.total_accounts}`;
      }
      if (document.getElementById("success-rate-card")) {
        document.getElementById(
          "success-rate-card"
        ).textContent = `${data.success_rate}%`;
      }
      if (document.getElementById("runtime-status-info")) {
        document.getElementById(
          "runtime-status-info"
        ).textContent = `Status: ${data.status}`;
      }
      if (document.getElementById("total-accounts-card")) {
        document.getElementById("total-accounts-card").textContent =
          data.total_accounts;
      }
      if (document.getElementById("proxy-card")) {
        document.getElementById("proxy-card").textContent = data.proxies;
      }
      if (document.getElementById("comment-card")) {
        document.getElementById("comment-card").textContent = data.comments;
      }
    });
}

// Auto-update table every 5 seconds if accounts might have changed
setInterval(() => {
  updateAccountTable();
  updateStats();
}, 5000);

function saveLog() {
  const logOutput = document.getElementById("log-output");
  fetch("/save_log", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ log: logOutput.value }),
  })
    .then((res) => res.json())
    .then((data) => {
      if (data.status === "saved") {
        showFlashMessage("Log saved!", "success");
      } else {
        showFlashMessage("Error saving log.", "danger");
      }
    })
    .catch(() => showFlashMessage("Error saving log.", "danger"));
}

function clearLog() {
  // Call backend to permanently clear the log
  fetch("/clear_log", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  })
    .then((res) => res.json())
    .then((data) => {
      if (data.status === "cleared") {
        updateLog(""); // Clear the frontend display
        showFlashMessage("Log cleared permanently!", "success");
      } else {
        showFlashMessage("Error clearing log.", "danger");
      }
    })
    .catch(() => {
      // If backend call fails, at least clear the frontend
      updateLog("");
      showFlashMessage("Log cleared (frontend only).", "warning");
    });
}

function clearAllAccounts() {
  // Call backend to clear ALL files including samples
  if (
    confirm(
      "Are you sure you want to delete ALL account files including sample files? This cannot be undone."
    )
  ) {
    fetch("/clear_all_accounts", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.status === "cleared") {
          showFlashMessage(
            "All account files cleared including samples!",
            "warning"
          );
          // Update table dynamically without page reload
          updateAccountTable();
          updateStats();
        } else {
          showFlashMessage("Error clearing all account files.", "danger");
        }
      })
      .catch(() => {
        showFlashMessage("Error clearing all account files.", "danger");
      });
  }
}

function updateAccountTable() {
  // Fetch updated account table data
  fetch("/get_accounts")
    .then((res) => res.json())
    .then((data) => {
      const tableBody = document.querySelector(".user-accounts-table tbody");
      if (tableBody) {
        // Clear existing rows
        tableBody.innerHTML = "";
        
        // Add new rows
        data.accounts.forEach((account) => {
          const row = document.createElement("tr");
          row.innerHTML = `
            <td>${account.no}</td>
            <td>${account.username}</td>
            <td>${account.privatekey}</td>
            <td>${account.cookies}</td>
            <td>${account.email}</td>
            <td>${account.passmail}</td>
            <td>${account.phone}</td>
            <td>${account.recoverymail}</td>
          `;
          tableBody.appendChild(row);
        });
      }
    })
    .catch((err) => {
      console.error("Error updating account table:", err);
    });
}

function updateStats() {
  // Update stats cards without full page reload
  fetch("/get_stats")
    .then((res) => res.json())
    .then((data) => {
      if (document.getElementById("total-accounts-card")) {
        document.getElementById("total-accounts-card").textContent = data.accounts;
      }
      // Update other stats as needed
    })
    .catch((err) => {
      console.error("Error updating stats:", err);
    });
}

setInterval(fetchLog, 2000);

// Function to show flash messages dynamically
function showFlashMessage(message, category) {
  // Remove existing flash messages
  const existingFlashes = document.querySelectorAll('.flash');
  existingFlashes.forEach(flash => flash.remove());
  
  // Create new flash message
  const flashWrapper = document.createElement('div');
  flashWrapper.id = 'flash-center-wrapper';
  
  const flashDiv = document.createElement('div');
  flashDiv.className = `flash ${category}`;
  flashDiv.textContent = message;
  
  flashWrapper.appendChild(flashDiv);
  
  // Insert after header
  const header = document.querySelector('.header');
  if (header && header.nextSibling) {
    header.parentNode.insertBefore(flashWrapper, header.nextSibling);
  } else {
    document.body.insertBefore(flashWrapper, document.body.firstChild);
  }
  
  // Auto-remove after 5 seconds
  setTimeout(() => {
    flashWrapper.remove();
  }, 5000);
}

// Handle file upload form submission
function handleFileUpload(event) {
  event.preventDefault(); // Prevent default form submission
  
  const form = event.target;
  const formData = new FormData(form);
  
  fetch('/upload', {
    method: 'POST',
    body: formData
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      showFlashMessage(data.message || 'Files uploaded successfully!', 'success');
      // Update table and stats dynamically
      updateAccountTable();
      updateStats();
    } else {
      showFlashMessage(data.message || 'Upload failed!', 'danger');
    }
  })
  .catch(error => {
    console.error('Upload error:', error);
    showFlashMessage('Upload failed!', 'danger');
  });
}

// Attach upload handler when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
  const uploadForm = document.querySelector('form[action="/upload"]');
  if (uploadForm) {
    uploadForm.addEventListener('submit', handleFileUpload);
  }
});
