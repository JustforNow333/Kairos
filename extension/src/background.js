// track active tabs and idle time
const API_URL = "http://localhost:8000/api/v1/idle";

let activeTabId = null;
let activeDomain = null;
let startTime = Date.now();
const IDLE_THRESHOLD = 60 * 5; // 5 minutes of idle time triggers intervention

chrome.idle.setDetectionInterval(60);

// Watch for tab changes
chrome.tabs.onActivated.addListener((activeInfo) => {
    handleTabChange(activeInfo.tabId);
});

chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.status === 'complete' && tabId === activeTabId) {
        handleTabChange(tabId);
    }
});

function handleTabChange(tabId) {
    chrome.tabs.get(tabId, (tab) => {
        if (chrome.runtime.lastError || !tab.url) return;

        const url = new URL(tab.url);
        const domain = url.hostname;

        // If we changed to a different domain, flush the previous time
        if (activeDomain && domain !== activeDomain) {
            flushTime(activeDomain, startTime);
        }

        activeTabId = tabId;
        activeDomain = domain;
        startTime = Date.now();
    });
}

function flushTime(domain, start) {
    const durationMinutes = Math.floor((Date.now() - start) / 60000);

    if (durationMinutes >= 1) { // Only log if they spent at least a minute
        const isDistraction = ["youtube.com", "reddit.com", "twitter.com", "instagram.com"]
            .some(dist => domain.includes(dist));

        if (isDistraction) {
            sendIdleEvent(domain, durationMinutes);
        }
    }
}

async function sendIdleEvent(domain, durationMinutes) {
    console.log(`Sending idle event: ${domain} for ${durationMinutes}m`);
    try {
        const response = await fetch(API_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                source: "chrome_extension",
                app_name: domain,
                duration_minutes: durationMinutes
            })
        });

        if (response.ok) {
            const intervention = await response.json();
            if (intervention && intervention.status !== "no_action_needed") {
                triggerInterventionOverlay(intervention);
            }
        }
    } catch (err) {
        console.warn("Failed to ping Kairos engine:", err);
    }
}

function triggerInterventionOverlay(interventionData) {
    if (activeTabId) {
        chrome.tabs.sendMessage(activeTabId, {
            action: "show_intervention",
            data: interventionData
        }).catch(() => console.log("Content script not ready in active tab."));
    }
}

// Periodically flush active tab if it's been open for a while
setInterval(() => {
    if (activeDomain) {
        flushTime(activeDomain, startTime);
        startTime = Date.now(); // reset timer
    }
}, 60000 * 5); // Check every 5 mins
