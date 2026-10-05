/**
 * SortRight - AI Waste Classification Assistant
 * Frontend Client Controller (Accessible, SVG-only, No Emoji)
 */

document.addEventListener("DOMContentLoaded", () => {
  // Elements
  const tabBtns = document.querySelectorAll(".segment-btn");
  const inputPanels = document.querySelectorAll(".input-panel");
  const langSelect = document.getElementById("langSelect");
  
  // Camera Elements
  const btnNativeCamera = document.getElementById("btnNativeCamera");
  const cameraNativeInput = document.getElementById("cameraNativeInput");
  const btnStartCamera = document.getElementById("btnStartCamera");
  const btnSnapPhoto = document.getElementById("btnSnapPhoto");
  const btnFlipCamera = document.getElementById("btnFlipCamera");
  const cameraVideo = document.getElementById("cameraVideo");
  const cameraPlaceholder = document.getElementById("cameraPlaceholder");
  const cameraNotice = document.getElementById("cameraNotice");
  
  // File Upload Elements
  const dropzone = document.getElementById("dropzone");
  const fileInput = document.getElementById("fileInput");

  // Text Input Elements
  const textInputForm = document.getElementById("textInputForm");
  const textItemInput = document.getElementById("textItemInput");

  // Loading & Result Elements
  const loadingContainer = document.getElementById("loadingContainer");
  const loadingText = document.getElementById("loadingText");
  const resultContainer = document.getElementById("resultContainer");
  const resultCard = document.getElementById("resultCard");
  const categoryBadge = document.getElementById("categoryBadge");
  const potentialPill = document.getElementById("potentialPill");
  const itemTitle = document.getElementById("itemTitle");
  const itemReason = document.getElementById("itemReason");
  const verifyNote = document.getElementById("verifyNote");
  const verifyText = document.getElementById("verifyText");
  const stepPrepare = document.getElementById("stepPrepare");
  const stepSeparate = document.getElementById("stepSeparate");
  const stepRoute = document.getElementById("stepRoute");
  const cardDisclaimer = document.getElementById("cardDisclaimer");
  const cardSource = document.getElementById("cardSource");
  const itemQueryLine = document.getElementById("itemQueryLine");
  const itemQueryText = document.getElementById("itemQueryText");
  const translationNoteEl = document.getElementById("translationNote");

  // Clarification & Fallback Elements
  const clarificationBox = document.getElementById("clarificationBox");
  const clarificationQuestion = document.getElementById("clarificationQuestion");
  const btnClarifyYes = document.getElementById("btnClarifyYes");
  const btnClarifyNo = document.getElementById("btnClarifyNo");
  const fallbackBox = document.getElementById("fallbackBox");
  const fallbackText = document.getElementById("fallbackText");

  // History Elements
  const historyList = document.getElementById("historyList");
  const btnClearHistory = document.getElementById("btnClearHistory");

  // State
  let currentStream = null;
  let currentFacingMode = "environment";
  let currentCardData = null;
  let currentLanguage = "en";

  // SVG Icons for Category Badges
  const ICONS = {
    special: `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>`,
    recyclable: `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 4 23 10 17 10"></polyline><polyline points="1 20 1 14 7 14"></polyline><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path></svg>`,
    organic: `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z"></path><path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"></path></svg>`,
    other: `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>`
  };

  // Check if getUserMedia is supported in current browser context (HTTPS or localhost)
  const hasGetUserMedia = !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia);
  const isSecure = window.isSecureContext || window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1";

  if (hasGetUserMedia && isSecure) {
    btnStartCamera.style.display = "inline-flex";
  } else {
    cameraNotice.textContent = "Tap 'Take Photo' below to use phone camera natively";
  }

  // ---------------------------------------------------------
  // 1. Segmented Control Tab Switching (with Keyboard Arrow Nav)
  // ---------------------------------------------------------
  function activateTab(targetBtn) {
    tabBtns.forEach(b => {
      b.setAttribute("aria-selected", "false");
    });
    inputPanels.forEach(p => p.classList.remove("active"));
    
    targetBtn.setAttribute("aria-selected", "true");
    const targetPanel = document.getElementById(targetBtn.dataset.target);
    if (targetPanel) targetPanel.classList.add("active");

    if (targetBtn.dataset.target !== "cameraPanel" && currentStream) {
      stopCamera();
    }
  }

  tabBtns.forEach((btn, idx) => {
    btn.addEventListener("click", () => activateTab(btn));

    // Keyboard navigation: Left/Right Arrow keys
    btn.addEventListener("keydown", (e) => {
      let targetIdx = idx;
      if (e.key === "ArrowRight") {
        targetIdx = (idx + 1) % tabBtns.length;
        tabBtns[targetIdx].focus();
        activateTab(tabBtns[targetIdx]);
      } else if (e.key === "ArrowLeft") {
        targetIdx = (idx - 1 + tabBtns.length) % tabBtns.length;
        tabBtns[targetIdx].focus();
        activateTab(tabBtns[targetIdx]);
      }
    });
  });

  // ---------------------------------------------------------
  // 2. Camera Handling
  // ---------------------------------------------------------
  btnNativeCamera.addEventListener("click", () => {
    cameraNativeInput.click();
  });

  cameraNativeInput.addEventListener("change", (e) => {
    if (e.target.files && e.target.files[0]) {
      classifyImageFile(e.target.files[0], "phone_camera.jpg");
      cameraNativeInput.value = "";
    }
  });

  async function startCamera() {
    if (!hasGetUserMedia || !isSecure) {
      cameraNativeInput.click();
      return;
    }
    if (currentStream) {
      stopCamera();
    }
    try {
      const constraints = {
        video: {
          facingMode: currentFacingMode,
          width: { ideal: 1280 },
          height: { ideal: 720 }
        },
        audio: false
      };
      currentStream = await navigator.mediaDevices.getUserMedia(constraints);
      cameraVideo.srcObject = currentStream;
      cameraPlaceholder.style.display = "none";
      cameraVideo.style.display = "block";
      btnStartCamera.style.display = "none";
      btnNativeCamera.style.display = "none";
      btnSnapPhoto.style.display = "inline-flex";
      btnFlipCamera.style.display = "inline-flex";
    } catch (err) {
      console.warn("getUserMedia failed:", err);
      cameraNativeInput.click();
    }
  }

  function stopCamera() {
    if (currentStream) {
      currentStream.getTracks().forEach(track => track.stop());
      currentStream = null;
    }
    cameraVideo.style.display = "none";
    cameraPlaceholder.style.display = "flex";
    if (hasGetUserMedia && isSecure) {
      btnStartCamera.style.display = "inline-flex";
    }
    btnNativeCamera.style.display = "inline-flex";
    btnSnapPhoto.style.display = "none";
    btnFlipCamera.style.display = "none";
  }

  btnStartCamera.addEventListener("click", startCamera);

  btnFlipCamera.addEventListener("click", () => {
    currentFacingMode = currentFacingMode === "environment" ? "user" : "environment";
    startCamera();
  });

  btnSnapPhoto.addEventListener("click", () => {
    if (!currentStream) return;
    const canvas = document.createElement("canvas");
    canvas.width = cameraVideo.videoWidth || 640;
    canvas.height = cameraVideo.videoHeight || 480;
    const ctx = canvas.getContext("2d");
    ctx.drawImage(cameraVideo, 0, 0, canvas.width, canvas.height);
    
    canvas.toBlob(blob => {
      if (blob) {
        stopCamera();
        classifyImageFile(blob, "camera_snap.jpg");
      }
    }, "image/jpeg", 0.85);
  });

  // ---------------------------------------------------------
  // 3. File Upload Handling
  // ---------------------------------------------------------
  dropzone.addEventListener("click", () => fileInput.click());
  
  dropzone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropzone.classList.add("dragover");
  });

  dropzone.addEventListener("dragleave", () => {
    dropzone.classList.remove("dragover");
  });

  dropzone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropzone.classList.remove("dragover");
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      classifyImageFile(e.dataTransfer.files[0]);
    }
  });

  fileInput.addEventListener("change", (e) => {
    if (e.target.files && e.target.files[0]) {
      classifyImageFile(e.target.files[0]);
      fileInput.value = "";
    }
  });

  // ---------------------------------------------------------
  // 4. Text Input Handling
  // ---------------------------------------------------------
  textInputForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const query = textItemInput.value.trim();
    if (!query) return;

    showLoading("Analyzing waste item with deterministic rules...");
    try {
      const response = await fetch("/api/classify-text", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: query, language: currentLanguage })
      });
      const data = await response.json();
      data.input_type = "text";
      data.raw_query = query;
      hideLoading();
      handleClassificationResult(data);
    } catch (err) {
      hideLoading();
      showFallbackUI("Server connection error. Please try again.");
    }
  });

  // ---------------------------------------------------------
  // 5. Image Classification API Call
  // ---------------------------------------------------------
  async function classifyImageFile(fileBlob, filename = "upload.jpg") {
    showLoading("Running AI perception & municipal rules engine...");
    const formData = new FormData();
    formData.append("file", fileBlob, filename);
    formData.append("language", currentLanguage);

    try {
      const response = await fetch("/api/classify-image", {
        method: "POST",
        body: formData
      });
      const data = await response.json();
      data.input_type = "image";
      hideLoading();

      if (!data.success && data.fallback_to_text) {
        showFallbackUI(data.message || "Vision analysis is currently unavailable. Please type the item name below.");
        switchToTextTab(textItemInput.value);
        return;
      }

      handleClassificationResult(data);
    } catch (err) {
      hideLoading();
      showFallbackUI("Image processing encountered an error. Please enter the item name as text.");
      switchToTextTab("");
    }
  }

  // ---------------------------------------------------------
  // 6. Result Card Rendering & Confidence Logic
  // ---------------------------------------------------------
  function handleClassificationResult(data) {
    currentCardData = data;
    hideAllFeedback();

    const confidenceStatus = data.ai_perception?.confidence_status || "high";
    const isNotSure = data.ai_perception?.is_not_sure || confidenceStatus === "fallback" || !data.success;

    if (isNotSure) {
      showFallbackUI(data.ai_perception?.confidence_message || "I'm not sure. Please retake the photo or describe the item.");
      return;
    }

    if (data.needs_clarification && data.clarifying_question) {
      clarificationQuestion.textContent = data.clarifying_question;
      clarificationBox.classList.add("active");
    }

    if (confidenceStatus === "verify") {
      verifyText.textContent = data.ai_perception?.confidence_message || "Please verify: item detected with moderate confidence.";
      verifyNote.classList.add("active");
    }

    renderCardData(data);
    resultContainer.classList.add("active");

    saveScanHistory(data);
  }

  function renderCardData(data) {
    resultCard.className = "result-card";
    categoryBadge.className = "category-badge";

    // Category Styling and SVG Icons (No Emoji)
    if (data.special === true) {
      resultCard.classList.add("is-special");
      categoryBadge.classList.add("badge-special");
      categoryBadge.innerHTML = `${ICONS.special} <span>Special Handling</span>`;
    } else if (data.category === "recyclable") {
      resultCard.classList.add("is-recyclable");
      categoryBadge.classList.add("badge-recyclable");
      categoryBadge.innerHTML = `${ICONS.recyclable} <span>Recyclable</span>`;
    } else if (data.category === "organic") {
      resultCard.classList.add("is-organic");
      categoryBadge.classList.add("badge-organic");
      categoryBadge.innerHTML = `${ICONS.organic} <span>Organic</span>`;
    } else {
      resultCard.classList.add("is-other");
      categoryBadge.classList.add("badge-other");
      categoryBadge.innerHTML = `${ICONS.other} <span>Reject / Other</span>`;
    }

    // Query Line
    if (itemQueryLine && itemQueryText) {
      const isTextQuery = data.input_type === "text" || !data.ai_perception?.model_used?.includes("vision");
      const labelPrefix = isTextQuery ? "You entered: " : "Detected from image: ";
      const rawText = data.raw_query || data.ai_perception?.item_detected || data.item_name || "-";
      itemQueryLine.childNodes[0].nodeValue = labelPrefix;
      itemQueryText.textContent = `"${rawText}"`;
    }

    // Title & Potential
    itemTitle.textContent = data.item_name || data.ai_perception?.item_detected || "Identified Item";
    const potLabel = data.potential_label || (data.category === "organic" ? "Composting potential" : "Recycling potential");
    potentialPill.textContent = `${potLabel}: ${data.recycling_potential || "Medium"}`;
    
    // Reason & Steps
    itemReason.textContent = data.reason || "";
    stepPrepare.textContent = data.steps?.prepare || "Inspect for cleanliness and residue.";
    stepSeparate.textContent = data.steps?.separate || "Keep separate from other waste streams.";
    stepRoute.textContent = data.steps?.route || "Dispose into designated municipal bin.";

    // Translation Note
    if (translationNoteEl) {
      if (data.translation_note) {
        translationNoteEl.textContent = data.translation_note;
        translationNoteEl.style.display = "block";
      } else {
        translationNoteEl.style.display = "none";
      }
    }

    // Disclaimer & Source
    cardDisclaimer.textContent = data.disclaimer || "Sample rules. Verify with local municipality.";
    cardSource.textContent = `City: ${data.city || "Coimbatore"} • ${data.source || "CCMC Guidelines"} (${data.last_updated || "2026"})`;
  }

  // ---------------------------------------------------------
  // 7. Clarification Question Handlers (Yes/No)
  // ---------------------------------------------------------
  btnClarifyYes.addEventListener("click", () => answerClarification(true));
  btnClarifyNo.addEventListener("click", () => answerClarification(false));

  async function answerClarification(isGreasy) {
    if (!currentCardData) return;
    showLoading("Updating classification based on condition...");
    
    try {
      const response = await fetch("/api/clarify", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          item: currentCardData.ai_perception?.item_detected || currentCardData.item_name,
          material: currentCardData.ai_perception?.material_detected || "cardboard",
          is_greasy_or_food_soiled: isGreasy,
          language: currentLanguage
        })
      });
      const updatedData = await response.json();
      hideLoading();
      clarificationBox.classList.remove("active");
      handleClassificationResult(updatedData);
    } catch (err) {
      hideLoading();
      alert("Failed to update classification. Please try again.");
    }
  }

  // ---------------------------------------------------------
  // 8. Language Dropdown Translation
  // ---------------------------------------------------------
  langSelect.addEventListener("change", async (e) => {
    currentLanguage = e.target.value;
    if (currentCardData && resultContainer.classList.contains("active")) {
      showLoading("Translating display card...");
      try {
        const response = await fetch("/api/translate", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            card: currentCardData,
            target_language: currentLanguage
          })
        });
        const translatedCard = await response.json();
        hideLoading();
        currentCardData = translatedCard;
        renderCardData(translatedCard);
      } catch (err) {
        hideLoading();
        console.error("Translation error:", err);
      }
    }
  });

  // ---------------------------------------------------------
  // 9. Scan History (localStorage: Text only, SVG icons)
  // ---------------------------------------------------------
  function loadScanHistory() {
    historyList.innerHTML = "";
    const history = JSON.parse(localStorage.getItem("sortright_history") || "[]");
    if (history.length === 0) {
      historyList.innerHTML = `<div style="color: var(--text-subtle); font-size: 0.85rem; text-align: center; padding: 0.75rem;">No recent scans yet.</div>`;
      return;
    }

    history.slice(0, 8).forEach(item => {
      const div = document.createElement("div");
      div.className = "history-item";
      
      let badgeHtml = "";
      if (item.special) {
        badgeHtml = `<span style="color: var(--cat-special); font-weight:700; display:inline-flex; align-items:center; gap:0.3rem;">${ICONS.special} Special</span>`;
      } else if (item.category === "recyclable") {
        badgeHtml = `<span style="color: var(--cat-recyclable); font-weight:700; display:inline-flex; align-items:center; gap:0.3rem;">${ICONS.recyclable} Recyclable</span>`;
      } else if (item.category === "organic") {
        badgeHtml = `<span style="color: var(--cat-organic); font-weight:700; display:inline-flex; align-items:center; gap:0.3rem;">${ICONS.organic} Organic</span>`;
      } else {
        badgeHtml = `<span style="color: var(--cat-other); font-weight:700; display:inline-flex; align-items:center; gap:0.3rem;">${ICONS.other} Other</span>`;
      }

      div.innerHTML = `
        <div>
          <div class="history-name">${item.item_name}</div>
          <div class="history-time">${item.time}</div>
        </div>
        <div>${badgeHtml}</div>
      `;
      historyList.appendChild(div);
    });
  }

  function saveScanHistory(data) {
    if (!data.item_name) return;
    const history = JSON.parse(localStorage.getItem("sortright_history") || "[]");
    const newEntry = {
      item_name: data.item_name,
      category: data.category,
      special: data.special,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
    history.unshift(newEntry);
    localStorage.setItem("sortright_history", JSON.stringify(history.slice(0, 20)));
    loadScanHistory();
  }

  btnClearHistory.addEventListener("click", () => {
    localStorage.removeItem("sortright_history");
    loadScanHistory();
  });

  // ---------------------------------------------------------
  // 10. Helper UI Functions
  // ---------------------------------------------------------
  function showLoading(msg) {
    loadingText.textContent = msg || "Processing...";
    loadingContainer.classList.add("active");
    resultContainer.classList.remove("active");
    clarificationBox.classList.remove("active");
    fallbackBox.classList.remove("active");
  }

  function hideLoading() {
    loadingContainer.classList.remove("active");
  }

  function showFallbackUI(msg) {
    fallbackText.textContent = msg || "I'm not sure. Please retake the photo or describe the item.";
    fallbackBox.classList.add("active");
    resultContainer.classList.remove("active");
  }

  function hideAllFeedback() {
    clarificationBox.classList.remove("active");
    verifyNote.classList.remove("active");
    fallbackBox.classList.remove("active");
  }

  function switchToTextTab(prefillText = "") {
    const textTab = document.getElementById("tabText");
    if (textTab) {
      activateTab(textTab);
      if (prefillText) textItemInput.value = prefillText;
      textItemInput.focus();
    }
  }

  // Initialize
  loadScanHistory();
});
