// ===============================
// 🔐 LOGIN PROTECTION
// ===============================
if (localStorage.getItem("photographer") !== "loggedIn") {
  window.location.href = "login.html";
}

function logout() {
  localStorage.removeItem("photographer");
  window.location.href = "login.html";
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
    const response = await fetch("http://localhost:5000/events");
    const data = await response.json();

    const container = document.getElementById("eventsContainer");
    const totalEvents = document.getElementById("totalEvents");
    const totalPhotos = document.getElementById("totalPhotos");

    container.innerHTML = "";

    if (!data.success || data.events.length === 0) {
      totalEvents.innerText = 0;
      totalPhotos.innerText = 0;
      container.innerHTML = "<p>No events created yet</p>";
      return;
    }

    totalEvents.innerText = data.events.length;

    let photoCount = 0;

    data.events.forEach(event => {
      photoCount += event.totalPhotos;

      const card = document.createElement("div");
      card.className = "event-card";

      card.addEventListener("click", () => {
        manageEvent(event.eventId);
      });

      card.innerHTML = `
        <img src="${event.coverPhoto || 'https://via.placeholder.com/400x200'}" class="cover-img">
        <div class="event-info">
          <h3>${event.eventId}</h3>
          <p>${event.totalPhotos} Photos</p>
          <button class="manage-btn" onclick="event.stopPropagation(); manageEvent('${event.eventId}')">Manage</button>
          <button class="delete-event-btn" onclick="event.stopPropagation(); deleteEvent('${event.eventId}')">Delete</button>
        </div>
      `;

      container.appendChild(card);
    });

    totalPhotos.innerText = photoCount;

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
// 🗑 DELETE EVENT
// ===============================
async function deleteEvent(eventId) {
  const confirmDelete = confirm(`Delete "${eventId}"? This cannot be undone.`);
  if (!confirmDelete) return;

  await fetch(`http://localhost:5000/events/${eventId}`, {
    method: "DELETE"
  });

  loadEvents();
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
  for (let i = 0; i < files.length; i++) {
    formData.append("photos", files[i]);
  }

  const xhr = new XMLHttpRequest();
  xhr.open("POST", `http://localhost:5000/upload/${eventId}`, true);

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
      status.innerText = "Upload Successful!";
      document.getElementById("eventId").value = "";
      document.getElementById("photos").value = "";
      loadEvents();
    } else {
      status.innerText = "Upload Failed!";
    }
  };

  xhr.send(formData);
}