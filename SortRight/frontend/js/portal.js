/**
 * SortRight - Staff Portal Controller
 * Role-aware data fetching and visualization
 */

document.addEventListener("DOMContentLoaded", async () => {
  const userRoleBadge = document.getElementById("userRoleBadge");
  const userNameDisplay = document.getElementById("userNameDisplay");
  const btnLogout = document.getElementById("btnLogout");
  const periodSelect = document.getElementById("periodSelect");
  const btnExportCsv = document.getElementById("btnExportCsv");
  
  const municipalityView = document.getElementById("municipalityView");
  const recyclerView = document.getElementById("recyclerView");
  const portalTitle = document.getElementById("portalTitle");
  const portalSubtitle = document.getElementById("portalSubtitle");

  let currentUser = null;
  let chartInstances = {};

  // 1. Authenticate session
  try {
    const authResp = await fetch("/api/portal/me");
    if (!authResp.ok) {
      window.location.href = "/portal/login";
      return;
    }
    const authData = await authResp.json();
    currentUser = authData.user;
  } catch (err) {
    window.location.href = "/portal/login";
    return;
  }

  // 2. Render Header Information
  userNameDisplay.textContent = currentUser.name || currentUser.email;
  if (currentUser.role === "municipality") {
    userRoleBadge.textContent = "🏛️ Municipality Officer View";
    portalTitle.textContent = "Municipal Segregation & Route Planning";
    portalSubtitle.textContent = "Ward-level metrics, contamination hotspots, and collection scheduling.";
    municipalityView.style.display = "block";
    loadMunicipalityData(30);
  } else {
    userRoleBadge.textContent = "♻️ Recycler Partner View";
    portalTitle.textContent = "Material Availability & Sourcing";
    portalSubtitle.textContent = "Estimated recoverable tonnage, quality grades, and pickup windows.";
    recyclerView.style.display = "block";
    loadRecyclerData(30);
  }

  // 3. Logout Handler
  btnLogout.addEventListener("click", async () => {
    try {
      await fetch("/api/portal/logout", { method: "POST" });
      window.location.href = "/portal/login";
    } catch (err) {
      window.location.href = "/portal/login";
    }
  });

  // 4. Period Change Handler
  periodSelect.addEventListener("change", (e) => {
    const days = parseInt(e.target.value) || 30;
    if (currentUser.role === "municipality") {
      loadMunicipalityData(days);
    } else {
      loadRecyclerData(days);
    }
  });

  // 5. CSV Export Handler
  btnExportCsv.addEventListener("click", () => {
    const days = periodSelect.value || 30;
    window.location.href = `/api/portal/export-csv?days=${days}`;
  });

  // ---------------------------------------------------------
  // MUNICIPALITY DATA LOADER
  // ---------------------------------------------------------
  async function loadMunicipalityData(days) {
    try {
      const resp = await fetch(`/api/portal/municipality-data?days=${days}`);
      if (!resp.ok) return;
      const data = await resp.json();

      // KPIs
      document.getElementById("kpiScans").textContent = Number(data.kpi.total_scans).toLocaleString();
      document.getElementById("kpiAccuracy").textContent = `${data.kpi.segregation_accuracy_pct}%`;
      document.getElementById("kpiContamination").textContent = `${data.kpi.contamination_rate_pct}%`;
      document.getElementById("kpiEwaste").textContent = `${Number(data.kpi.ewaste_routed_kg).toLocaleString()} kg`;

      // Ward Table
      const tbody = document.getElementById("wardTableBody");
      tbody.innerHTML = "";
      data.ward_table.forEach(w => {
        const tr = document.createElement("tr");
        tr.style.borderBottom = "1px solid var(--border-color)";
        const statusColor = w.status === "Good" ? "var(--cat-recyclable)" : (w.status === "Action Required" ? "var(--cat-special)" : "var(--accent-cyan)");
        
        tr.innerHTML = `
          <td style="padding: 0.6rem 0.5rem; font-weight: 600;">${w.ward_name} <span style="font-size: 0.72rem; color: var(--text-muted);">(${w.ward_id})</span></td>
          <td style="padding: 0.6rem 0.5rem;">${Number(w.scans).toLocaleString()}</td>
          <td style="padding: 0.6rem 0.5rem; color: var(--cat-recyclable);">${w.recyclable_pct}%</td>
          <td style="padding: 0.6rem 0.5rem; color: var(--cat-organic);">${w.organic_pct}%</td>
          <td style="padding: 0.6rem 0.5rem; color: var(--cat-special);">${w.contamination_pct}%</td>
          <td style="padding: 0.6rem 0.5rem;">${w.ewaste_kg} kg</td>
          <td style="padding: 0.6rem 0.5rem; font-weight: 700; color: ${statusColor};">${w.status}</td>
        `;
        tbody.appendChild(tr);
      });

      // Planning Recommendations
      const planDiv = document.getElementById("planningList");
      planDiv.innerHTML = "";
      data.planning_recommendations.forEach(r => {
        const div = document.createElement("div");
        div.style.background = "rgba(15, 23, 42, 0.6)";
        div.style.border = "1px solid var(--border-color)";
        div.style.borderRadius = "var(--radius-sm)";
        div.style.padding = "0.75rem 0.9rem";
        
        const priorityColor = r.priority === "High" ? "var(--cat-special)" : "var(--accent-cyan)";
        div.innerHTML = `
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.25rem;">
            <strong style="color: #fff; font-size: 0.88rem;">${r.target_ward}</strong>
            <span style="font-size: 0.72rem; font-weight: 700; color: ${priorityColor}; background: rgba(0,0,0,0.3); padding: 0.15rem 0.45rem; border-radius: 4px;">${r.priority} Priority</span>
          </div>
          <div style="font-size: 0.82rem; color: var(--text-secondary); margin-bottom: 0.25rem;">${r.issue}</div>
          <div style="font-size: 0.82rem; color: #a5f3fc;"><strong>Action:</strong> ${r.recommended_action}</div>
        `;
        planDiv.appendChild(div);
      });

      // Charts
      renderMuniCharts(data);

    } catch (err) {
      console.error("Failed to load municipality data:", err);
    }
  }

  function renderMuniCharts(data) {
    // Waste Mix Doughnut
    if (chartInstances.muniMix) chartInstances.muniMix.destroy();
    const ctxMix = document.getElementById("muniWasteMixChart").getContext("2d");
    chartInstances.muniMix = new Chart(ctxMix, {
      type: "doughnut",
      data: {
        labels: data.waste_mix.map(m => m.category),
        datasets: [{
          data: data.waste_mix.map(m => m.share_pct),
          backgroundColor: data.waste_mix.map(m => m.color),
          borderWidth: 0
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: "bottom", labels: { color: "#94a3b8", boxWidth: 10, padding: 10, font: { size: 11 } } }
        }
      }
    });

    // Hotspots Bar Chart
    if (chartInstances.muniHotspots) chartInstances.muniHotspots.destroy();
    const ctxHotspots = document.getElementById("muniHotspotsChart").getContext("2d");
    chartInstances.muniHotspots = new Chart(ctxHotspots, {
      type: "bar",
      data: {
        labels: data.ward_table.map(w => w.ward_name),
        datasets: [{
          label: "Contamination (%)",
          data: data.ward_table.map(w => w.contamination_pct),
          backgroundColor: "rgba(239, 68, 68, 0.75)",
          borderRadius: 4
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: { beginAtZero: true, grid: { color: "rgba(255,255,255,0.06)" }, ticks: { color: "#94a3b8" } },
          x: { grid: { display: false }, ticks: { color: "#94a3b8", font: { size: 10 } } }
        },
        plugins: { legend: { display: false } }
      }
    });
  }

  // ---------------------------------------------------------
  // RECYCLER DATA LOADER
  // ---------------------------------------------------------
  async function loadRecyclerData(days) {
    try {
      const resp = await fetch(`/api/portal/recycler-data?days=${days}`);
      if (!resp.ok) return;
      const data = await resp.json();

      // Material Availability Table
      const tbody = document.getElementById("materialTableBody");
      tbody.innerHTML = "";
      data.material_availability.forEach(m => {
        const tr = document.createElement("tr");
        tr.style.borderBottom = "1px solid var(--border-color)";
        tr.innerHTML = `
          <td style="padding: 0.6rem 0.5rem; font-weight: 600; color: #fff;">${m.material_type}</td>
          <td style="padding: 0.6rem 0.5rem; font-weight: 700; color: var(--accent-cyan);">${m.estimated_metric_tons} Tons</td>
          <td style="padding: 0.6rem 0.5rem; font-size: 0.8rem; color: var(--text-secondary);">${m.quality_grade}</td>
          <td style="padding: 0.6rem 0.5rem; font-size: 0.8rem;">${m.top_origin_wards.join(", ")}</td>
          <td style="padding: 0.6rem 0.5rem; color: var(--cat-recyclable); font-weight: 600;">${m.price_trend}</td>
        `;
        tbody.appendChild(tr);
      });

      // Pickup Suggestions
      const pickDiv = document.getElementById("pickupList");
      pickDiv.innerHTML = "";
      data.pickup_suggestions.forEach(p => {
        const div = document.createElement("div");
        div.style.background = "rgba(15, 23, 42, 0.6)";
        div.style.border = "1px solid var(--border-color)";
        div.style.borderRadius = "var(--radius-sm)";
        div.style.padding = "0.75rem 0.9rem";
        div.innerHTML = `
          <div style="font-weight: 700; font-size: 0.88rem; color: #fff;">${p.facility_name}</div>
          <div style="font-size: 0.8rem; color: var(--accent-cyan); margin-top: 0.15rem;">📦 Batch: ${p.available_batch}</div>
          <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.15rem;">⏰ Window: ${p.optimal_pickup_window}</div>
        `;
        pickDiv.appendChild(div);
      });

      // Supply Trends Chart
      if (chartInstances.recyTrend) chartInstances.recyTrend.destroy();
      const ctxTrend = document.getElementById("recyclerTrendChart").getContext("2d");
      chartInstances.recyTrend = new Chart(ctxTrend, {
        type: "line",
        data: {
          labels: data.supply_trend.labels,
          datasets: [
            {
              label: "Cardboard (Tons)",
              data: data.supply_trend.datasets[0].data,
              borderColor: "#b45309",
              backgroundColor: "rgba(180, 83, 9, 0.1)",
              tension: 0.3
            },
            {
              label: "PET Plastic (Tons)",
              data: data.supply_trend.datasets[1].data,
              borderColor: "#22c55e",
              backgroundColor: "rgba(34, 197, 94, 0.1)",
              tension: 0.3
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: { beginAtZero: true, grid: { color: "rgba(255,255,255,0.06)" }, ticks: { color: "#94a3b8" } },
            x: { grid: { display: false }, ticks: { color: "#94a3b8" } }
          },
          plugins: {
            legend: { position: "top", labels: { color: "#94a3b8", boxWidth: 10 } }
          }
        }
      });

    } catch (err) {
      console.error("Failed to load recycler data:", err);
    }
  }

});
