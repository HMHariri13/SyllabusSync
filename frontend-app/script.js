// --- 1. View Toggle Logic ---
const toggleBtn = document.getElementById("viewToggleBtn");
const weekView = document.getElementById("weekView");
const monthView = document.getElementById("monthView");

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

// --- 2. Interaction Logic ---
// Click interaction for Week Capsules
const days = document.querySelectorAll(".day-capsule");
days.forEach((day) => {
  day.addEventListener("click", () => {
    days.forEach((d) => d.classList.remove("active"));
    day.classList.add("active");
  });
});

// Click interaction for Month Days
const monthDays = document.querySelectorAll(".month-day:not(.other-month)");
monthDays.forEach((day) => {
  day.addEventListener("click", () => {
    document.querySelectorAll(".month-day").forEach((d) => d.classList.remove("active"));
    day.classList.add("active");
  });
});

// --- 3. CHECK FOR NEW DATA (The Connection Logic) ---
// Simulates fetching data from your backend
window.addEventListener("load", () => {
  if (localStorage.getItem("syllabusUploaded") === "true") {
    const container = document.getElementById("schedule-list");
    const count = document.getElementById("class-count");

    // Update Count
    count.innerText = "3 Classes";

    // Add New Event Card HTML
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

    // Append it (Simulation)
    container.insertAdjacentHTML("beforeend", newEventHTML);

    // Optional: Clear flag so it doesn't keep adding it on refresh
    // localStorage.removeItem('syllabusUploaded');
  }
});
