chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "show_intervention") {
        renderOverlay(request.data);
    }
});

function renderOverlay(data) {
    // Prevent rendering multiple
    if (document.getElementById("kairos-enforcer-overlay")) return;

    const overlay = document.createElement("div");
    overlay.id = "kairos-enforcer-overlay";

    const friendText = data.friend_names && data.friend_names.length > 0
        ? `<strong>${data.friend_names.join(", ")}</strong> are free in ${data.social_readiness_gap_hours.toFixed(1)} hours.`
        : `You are falling behind your social goals.`;

    overlay.innerHTML = `
        <div class="kairos-modal">
            <div class="kairos-header">
                <span class="kairos-badge">KAIROS ENFORCER</span>
            </div>
            <h2>${data.headline}</h2>
            <p>${data.action}</p>
            <div class="kairos-context">
                <p>⚠️ ${friendText}</p>
            </div>
            <div class="kairos-actions">
                <button id="kairos-btn-dismiss">Give me 5 more minutes</button>
                <button id="kairos-btn-close" class="primary">Close Tab & Get Back to Work</button>
            </div>
        </div>
    `;

    document.body.appendChild(overlay);

    document.body.style.overflow = "hidden"; // lock scrolling

    document.getElementById("kairos-btn-dismiss").addEventListener("click", () => {
        document.body.style.overflow = "auto";
        overlay.remove();
    });

    document.getElementById("kairos-btn-close").addEventListener("click", () => {
        chrome.runtime.sendMessage({ action: "close_active_tab" }); // Not yet implemented in BG, but will close the tab
        window.close(); // might work depending on browser security params
    });
}
