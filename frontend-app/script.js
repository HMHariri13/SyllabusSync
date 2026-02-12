// Shared JS for BOTH pages (dashboard + upload)
// Safe to include on every page because it checks for elements before wiring events.

window.addEventListener("DOMContentLoaded", () => {
  // =========================
  // DASHBOARD: View Toggle
  // =========================
  const toggleBtn = document.getElementById("viewToggleBtn");
  const weekView = document.getElementById("weekView");
  const monthView = document.getElementById("monthView");

  if (toggleBtn && weekView && monthView) {
    let isMonthView = false;

    toggleBtn.addEventListener("click", () => {
      isMonthView = !isMonthView;

      if (isMonthView) {
        weekView.style.display = "none";
        monthView.style.display = "block";
        toggleBtn.innerText = "View Week";
      } else {
        weekView.style.display = "flex";
        monthView.style.display = "none";
        toggleBtn.innerText = "View Month";
      }
    });
  }

  // =========================
  // DASHBOARD: Day selection
  // =========================
  const days = document.querySelectorAll(".day-capsule");
  if (days.length) {
    days.forEach((day) => {
      day.addEventListener("click", () => {
        days.forEach((d) => d.classList.remove("active"));
        day.classList.add("active");
      });
    });
  }

  const monthDays = document.querySelectorAll(".month-day:not(.other-month)");
  if (monthDays.length) {
    monthDays.forEach((day) => {
      day.addEventListener("click", () => {
        document.querySelectorAll(".month-day").forEach((d) => d.classList.remove("active"));
        day.classList.add("active");
      });
    });
  }

  // =========================================
  // DASHBOARD: Simulated "new upload" insert
  // =========================================
  const scheduleList = document.getElementById("schedule-list");
  const classCount = document.getElementById("class-count");

  if (scheduleList && classCount) {
    if (localStorage.getItem("syllabusUploaded") === "true") {
      classCount.innerText = "3 Classes";

      const newEventHTML = `
        <div class="timeline-item">
          <div class="time-col">04:30 PM</div>
          <div class="event-card new-event">
            <div class="event-title">Intro to Biology (New)</div>
            <div class="event-meta">
              <span><i class="fa-regular fa-clock"></i> 1h 00m</span>
              <span><i class="fa-solid fa-location-dot"></i> Room 101</span>
            </div>
          </div>
        </div>
      `;

      scheduleList.insertAdjacentHTML("beforeend", newEventHTML);

      // Optional: clear the flag so it doesn't keep adding on refresh
      // localStorage.removeItem("syllabusUploaded");
    }
  }


  

  // =========================
  // UPLOAD: File selection UI
  // =========================
  const fileInput = document.getElementById("file-input");
  const filePreview = document.getElementById("file-preview");
  const fileName = document.getElementById("file-name");
  const submitBtn = document.getElementById("submit-btn");

  if (fileInput && filePreview && fileName && submitBtn) {
    fileInput.addEventListener("change", function () {
      if (this.files && this.files[0]) {
        fileName.textContent = this.files[0].name;
        filePreview.style.display = "flex";
        submitBtn.classList.add("active");
      }
    });

    submitBtn.addEventListener("click", async () => {
      const file = fileInput.files?.[0];
      if (!file) return;

      const formData = new FormData();
      formData.append("file", file);

      submitBtn.textContent = "Uploading...";
      submitBtn.disabled = true;

      try {
            const response = await fetch(
                "http://127.0.0.1:8000/upload-syllabus/",
                {
                    method: "POST",
                    body: formData
                }
            );

            if (!response.ok) {
                throw new Error("Upload failed");
            }

            const data = await response.json();
            console.log("Backend response:", data);

        // Simulate delay
        await new Promise((r) => setTimeout(r, 1000));

        // Flag for dashboard to show new event
        localStorage.setItem("syllabusUploaded", "true");

        alert("Syllabus processed! Redirecting...");
        window.location.href = "mainScreen.html";
      } catch (error) {
        console.error("Upload error (Simulation fallback active)", error);
        localStorage.setItem("syllabusUploaded", "true");
        window.location.href = "mainScreen.html";
      } finally {
        submitBtn.textContent = "Sync with Calendar";
        submitBtn.disabled = false;
      }

      
    });
  }
});

