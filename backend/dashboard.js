// ===============================
// 🔐 LOGIN PROTECTION
// ===============================
const photographerId = localStorage.getItem("photographer_id");

if (!photographerId) {
  window.location.href = "/";
}

function logout() {
  localStorage.clear();
  window.location.href = "/";
}

// ===============================
// 📦 DRAG & DROP
// ===============================
document.addEventListener("DOMContentLoaded", function () {

  const dropArea = document.getElementById("dropArea");
  const fileInput = document.getElementById("photos");

  dropArea.addEventListener("click", () => fileInput.click());

  dropArea.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropArea.classList.add("dragging");
  });

  dropArea.addEventListener("dragleave", () => {
    dropArea.classList.remove("dragging");
  });

  dropArea.addEventListener("drop", (e) => {
    e.preventDefault();
    dropArea.classList.remove("dragging");
    fileInput.files = e.dataTransfer.files;
  });

  loadEvents();
});

// ===============================
// 📦 LOAD EVENTS
// ===============================
async function loadEvents() {

  try {

    const response = await fetch(`/my-events/${photographerId}`);
    const data = await response.json();

    const container = document.getElementById("eventsContainer");
    const totalEvents = document.getElementById("totalEvents");

    container.innerHTML = "";

    if (!data.success || data.events.length === 0) {

      totalEvents.innerText = 0;
      container.innerHTML = "<p>No events created yet</p>";
      return;
    }

    totalEvents.innerText = data.events.length;

    data.events.forEach(event => {

      const card = document.createElement("div");
      card.className = "event-card";

      card.innerHTML = `
        <div class="event-info">
          <h3>${event.event_id}</h3>
          <p>${event.created_at}</p>
          <button class="manage-btn" onclick="manageEvent('${event.event_id}')">Manage</button>
        </div>
      `;

      container.appendChild(card);

    });

  } catch (error) {

    console.error("Error loading events:", error);

  }

}

// ===============================
// 🎯 GO TO MANAGE PAGE
// ===============================
function manageEvent(eventId) {

  window.location.href = `manage.html?event=${eventId}`;

}

// ===============================
// 📤 UPLOAD WITH PROGRESS
// ===============================
function uploadPhotos() {

  const eventId = document.getElementById("eventId").value.trim();
  const files = document.getElementById("photos").files;
  const status = document.getElementById("status");
  const progressBar = document.getElementById("progressBar");
  const uploadBtn = document.getElementById("uploadBtn");

  if (!eventId || files.length === 0) {

    status.innerText = "Create Event ID & select photos";
    return;

  }

  const formData = new FormData();

  formData.append("event_id", eventId);
  formData.append("photographer_id", localStorage.getItem("photographerId"));

  for (let i = 0; i < files.length; i++) {

    formData.append("photos", files[i]);

  }

  const xhr = new XMLHttpRequest();

  xhr.open("POST", `/upload-photos`, true);

  uploadBtn.disabled = true;
  status.innerText = "Uploading...";

  xhr.upload.onprogress = function (e) {

    if (e.lengthComputable) {

      const percent = (e.loaded / e.total) * 100;
      progressBar.style.width = percent + "%";

    }

  };

  xhr.onload = function () {

    uploadBtn.disabled = false;
    progressBar.style.width = "0%";

    if (xhr.status === 200) {

      status.innerText = "Upload Successful 📸";
      document.getElementById("eventId").value = "";
      document.getElementById("photos").value = "";

      loadEvents();

    } else {

      status.innerText = "Upload Failed";

    }

  };

  xhr.send(formData);

}