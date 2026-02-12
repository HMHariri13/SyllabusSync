// Shared JS for BOTH pages (dashboard + upload)
// Safe to include on every page because it checks for elements before wiring events.

window.addEventListener("DOMContentLoaded", () => {
  // -------------------------
  // Helpers
  // -------------------------
  const pad2 = (n) => String(n).padStart(2, "0");

  // Key format: YYYY-MM-DD
  const toKey = (d) => {
    const y = d.getFullYear();
    const m = pad2(d.getMonth() + 1);
    const day = pad2(d.getDate());
    return `${y}-${m}-${day}`;
  };

  const startOfDay = (d) => new Date(d.getFullYear(), d.getMonth(), d.getDate());

  // Monday-first week (Mon=0 ... Sun=6)
  const mondayIndex = (date) => (date.getDay() + 6) % 7;

  const monthNames = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
  ];

  const weekdayShort = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

  // -------------------------
  // DASHBOARD: Dynamic Calendar
  // -------------------------
  const monthLabel = document.getElementById("monthLabel");
  const weekView = document.getElementById("weekView");
  const monthView = document.getElementById("monthView");

  // Optional: mark dates with dots (you can replace this with real data later)
  // Example: const eventDates = new Set(["2026-02-12", "2026-02-15"]);
  const eventDates = new Set();

  // If the user uploaded a syllabus (your simulation), show a dot on today as a proof-of-life.
  if (localStorage.getItem("syllabusUploaded") === "true") {
    eventDates.add(toKey(new Date()));
  }

  const renderWeek = (selectedDate) => {
    if (!weekView) return;

    const base = startOfDay(selectedDate);
    const offset = mondayIndex(base);
    const monday = new Date(base);
    monday.setDate(base.getDate() - offset);

    weekView.innerHTML = "";

    for (let i = 0; i < 7; i++) {
      const d = new Date(monday);
      d.setDate(monday.getDate() + i);

      const key = toKey(d);
      const isActive = key === toKey(selectedDate);
      const hasEvent = eventDates.has(key);

      const capsule = document.createElement("div");
      capsule.className = `day-capsule${isActive ? " active" : ""}${hasEvent ? " has-event" : ""}`;
      capsule.dataset.date = key;

      capsule.innerHTML = `
        <span class="day-name">${weekdayShort[i]}</span>
        <span class="date-num">${d.getDate()}</span>
        <div class="has-class-dot"></div>
      `;

      capsule.addEventListener("click", () => {
        document.querySelectorAll(".day-capsule").forEach((el) => el.classList.remove("active"));
        capsule.classList.add("active");

        // Keep month grid in sync
        if (monthView) {
          monthView.querySelectorAll(".month-day").forEach((el) => el.classList.remove("active"));
          const match = monthView.querySelector(`.month-day[data-date='${key}']`);
          if (match) match.classList.add("active");
        }
      });

      weekView.appendChild(capsule);
    }
  };

  const renderMonth = (selectedDate) => {
    if (!monthView) return;

    const year = selectedDate.getFullYear();
    const month = selectedDate.getMonth(); // 0-11

    // Update header label
    if (monthLabel) monthLabel.textContent = `${monthNames[month]} ${year}`;

    const firstOfMonth = new Date(year, month, 1);
    const daysInMonth = new Date(year, month + 1, 0).getDate();

    // We want the grid to start on Monday
    const leading = mondayIndex(firstOfMonth); // 0..6

    // Calculate how many total cells: 5 or 6 weeks
    const totalCells = Math.ceil((leading + daysInMonth) / 7) * 7;

    // Start date for grid
    const gridStart = new Date(year, month, 1 - leading);

    // Build month view inner HTML
    const headerHTML = `
      <div class="week-days-header">
        <span>M</span><span>T</span><span>W</span><span>T</span><span>F</span><span>S</span><span>S</span>
      </div>
      <div class="month-grid"></div>
    `;

    monthView.innerHTML = headerHTML;

    const grid = monthView.querySelector(".month-grid");

    for (let i = 0; i < totalCells; i++) {
      const d = new Date(gridStart);
      d.setDate(gridStart.getDate() + i);

      const key = toKey(d);
      const inThisMonth = d.getMonth() === month;
      const isActive = key === toKey(selectedDate);
      const hasEvent = eventDates.has(key);

      const cell = document.createElement("div");
      cell.className = `month-day${inThisMonth ? "" : " other-month"}${hasEvent ? " has-event" : ""}${isActive ? " active" : ""}`;
      cell.dataset.date = key;
      cell.innerHTML = `${d.getDate()}${hasEvent ? '<div class="dot"></div>' : ''}`;

      // Clicking month day selects it and syncs week strip
      cell.addEventListener("click", () => {
        // ignore clicks on other-month cells (optional)
        if (!inThisMonth) return;

        monthView.querySelectorAll(".month-day").forEach((el) => el.classList.remove("active"));
        cell.classList.add("active");

        // Sync week
        renderWeek(d);
      });

      grid.appendChild(cell);
    }
  };

  const renderCalendarToday = () => {
    if (!weekView && !monthView && !monthLabel) return;
    const today = startOfDay(new Date());
    renderMonth(today);
    renderWeek(today);
  };

  const scheduleMidnightRefresh = () => {
    // Refresh right after midnight so the calendar updates daily
    const now = new Date();
    const nextMidnight = new Date(now.getFullYear(), now.getMonth(), now.getDate() + 1, 0, 0, 1);
    const ms = nextMidnight.getTime() - now.getTime();

    setTimeout(() => {
      renderCalendarToday();
      scheduleMidnightRefresh();
    }, ms);
  };

  // Render dynamic calendar on load
  renderCalendarToday();
  scheduleMidnightRefresh();

  // -------------------------
  // DASHBOARD: View Toggle (Week/Month)
  // -------------------------
  const toggleBtn = document.getElementById("viewToggleBtn");

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

  // -----------------------------------------
  // DASHBOARD: Simulated "new upload" insert
  // -----------------------------------------
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

  // -------------------------
  // UPLOAD: File selection UI
  // -------------------------
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
        await fetch("http://127.0.0.1:8000/upload-syllabus/", { method: "POST", body: formData });

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
