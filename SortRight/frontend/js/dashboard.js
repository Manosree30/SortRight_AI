/**
 * SortRight - Simulated Analytics Dashboard
 * Clear notice: Simulated demo data. Not real scan data.
 */

document.addEventListener("DOMContentLoaded", () => {
  // Chart 1: Waste Mix by Category
  const ctxMix = document.getElementById("wasteMixChart").getContext("2d");
  new Chart(ctxMix, {
    type: "doughnut",
    data: {
      labels: ["Recyclables (Dry)", "Organic (Wet)", "Reject / Other", "Hazardous / E-Waste"],
      datasets: [{
        data: [42, 38, 14, 6],
        backgroundColor: [
          "#22c55e", // Green
          "#b45309", // Brown
          "#64748b", // Grey
          "#ef4444"  // Red
        ],
        borderWidth: 0
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: "bottom",
          labels: { color: "#94a3b8", boxWidth: 12, padding: 15 }
        }
      }
    }
  });

  // Chart 2: Contamination Hotspots by Ward / Zone
  const ctxHotspots = document.getElementById("hotspotsChart").getContext("2d");
  new Chart(ctxHotspots, {
    type: "bar",
    data: {
      labels: ["RS Puram", "Gandhipuram", "Peelamedu", "Singanallur", "Saibaba Colony"],
      datasets: [{
        label: "Contamination Incident Rate (%)",
        data: [12.4, 28.6, 18.2, 24.1, 9.8],
        backgroundColor: "rgba(239, 68, 68, 0.75)",
        borderColor: "#ef4444",
        borderWidth: 1,
        borderRadius: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          grid: { color: "rgba(255,255,255,0.06)" },
          ticks: { color: "#94a3b8" }
        },
        x: {
          grid: { display: false },
          ticks: { color: "#94a3b8" }
        }
      },
      plugins: {
        legend: { display: false }
      }
    }
  });

  // Chart 3: E-Waste & Special Handling Volume Trend (Monthly kg)
  const ctxTrend = document.getElementById("trendChart").getContext("2d");
  new Chart(ctxTrend, {
    type: "line",
    data: {
      labels: ["Oct", "Nov", "Dec", "Jan", "Feb", "Mar"],
      datasets: [{
        label: "E-Waste Collected (kg)",
        data: [320, 410, 390, 520, 680, 840],
        borderColor: "#06b6d4",
        backgroundColor: "rgba(6, 182, 212, 0.15)",
        fill: true,
        tension: 0.35,
        pointRadius: 4,
        pointBackgroundColor: "#06b6d4"
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          grid: { color: "rgba(255,255,255,0.06)" },
          ticks: { color: "#94a3b8" }
        },
        x: {
          grid: { display: false },
          ticks: { color: "#94a3b8" }
        }
      },
      plugins: {
        legend: {
          position: "top",
          labels: { color: "#94a3b8", boxWidth: 12 }
        }
      }
    }
  });
});
