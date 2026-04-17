let lastEventTimestamp = 0;
let currentOverlayState = null;
let pendingOverlayState = null;

async function fetchJson(url) {
    const response = await fetch(url);
    return await response.json();
}

function commitPendingOverlayState() {
    if (pendingOverlayState) {
        currentOverlayState = pendingOverlayState;
        pendingOverlayState = null;
        return true;
    }

    return false;
}

function renderObelisk(state) {
    const unlocked = state.achievements.filter(a => a.achieved);
    const locked = state.achievements.filter(a => !a.achieved);

    return [
        ...unlocked.map(a => `
            <div class="item unlocked">
                <img class="achievement-icon" src="/static/${a.icon}" alt="">
                <span>${a.display_name}</span>
            </div>
        `),
        `<hr class="divider">`,
        ...locked.map(a => `
            <div class="item locked">
                <img class="achievement-icon" src="/static/${a.icon_gray || a.icon}" alt="">
                <span>${a.display_name}</span>
            </div>
        `)
    ].join("");
}

function renderTicker(state) {
    const items = state.achievements.map(a => `
        <div class="ticker-item ${a.achieved ? "unlocked" : "locked"}">
            <img class="achievement-icon" src="/static/${a.achieved ? a.icon : (a.icon_gray || a.icon)}" alt="">
            <span>${a.display_name}</span>
        </div>
    `);

    const content = items.join("");

    return `
        <div class="ticker-track">
            ${content}
            ${content}
        </div>
    `;
}

function startTickerCycle() {
    const list = document.getElementById("list");
    const track = list.querySelector(".ticker-track");

    if (!track) {
        return;
    }

    track.addEventListener("animationiteration", () => {
        if (commitPendingOverlayState()) {
            list.innerHTML = renderTicker(currentOverlayState);
            startTickerCycle();
        }
    }, { once: true });
}

async function updateOverlay() {
    const latestState = await fetchJson("/api/state");
    const event = await fetchJson("/api/event");

    if (!currentOverlayState) {
        currentOverlayState = latestState;
    } else {
        pendingOverlayState = latestState;
    }

    const state = currentOverlayState;

    document.getElementById("counter").innerText = `${state.unlocked} / ${state.total}`;

    const list = document.getElementById("list");
    const activeGame = await fetchJson("/api/active-game");
    const displayMode = activeGame.display_mode || "obelisk";

        if (!list.innerHTML.trim()) {
        if (displayMode === "ticker") {
            list.innerHTML = renderTicker(state);
            startTickerCycle();
        } else {
            list.innerHTML = renderObelisk(state);
        }
    }

        if (event.timestamp > lastEventTimestamp && event.latest) {
        lastEventTimestamp = event.timestamp;

        const latest = document.getElementById("latest");
        const latestIcon = event.latest.icon || event.latest.icon_gray || "";

        latest.innerHTML = `
            <div class="item unlocked">
                <img class="achievement-icon" src="/static/${latestIcon}" alt="">
                <span>Unlocked: ${event.latest.display_name}</span>
            </div>
        `;
        latest.classList.add("show");

        setTimeout(() => {
            latest.classList.remove("show");
        }, 3000);
    }
}

async function loadGames() {
    const response = await fetch("/api/games");
    const games = await response.json();

    const select = document.getElementById("game-select");
    select.innerHTML = "";

    for (const game of games) {
        const option = document.createElement("option");
        option.value = game.app_id;
        option.textContent = game.name;
        select.appendChild(option);
    }
}

async function loadActiveGame() {
    const response = await fetch("/api/active-game");
    const data = await response.json();

    const output = document.getElementById("active-game-output");
    output.textContent = JSON.stringify(data, null, 2);

    if (data.active_app_id) {
        document.getElementById("game-select").value = data.active_app_id;
    }

    if (data.display_mode) {
        document.getElementById("display-mode-select").value = data.display_mode;
    }

    return data;
}

async function loadAchievements(appId) {
    const output = document.getElementById("achievements-output");

    if (!appId) {
        output.textContent = "No achievement data loaded.";
        return;
    }

    const response = await fetch(`/api/achievements?appid=${appId}`);
    const state = await response.json();

    const lines = [
        `Game: ${state.game_name}`,
        `Unlocked: ${state.unlocked} / ${state.total}`,
        "",
        ...state.achievements.map(achievement =>
            `[${achievement.achieved ? "Unlocked" : "Locked"}] ${achievement.display_name || achievement.apiname}`
        )
    ];

    output.textContent = lines.join("\n");
}

async function applySelectedGame() {
    const select = document.getElementById("game-select");
    const modeSelect = document.getElementById("display-mode-select");
    const appId = select.value;
    const displayMode = modeSelect.value;

    if (!appId) {
        return;
    }

    const response = await fetch("/api/select-game", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
            body: JSON.stringify({
                app_id: appId,
                display_mode: displayMode
            })
    });

        const state = await response.json();

    await loadActiveGame();

    await loadAchievements(appId);
}

async function refreshSelectedGame() {
    const select = document.getElementById("game-select");
    const appId = select.value;

    if (!appId) {
        return;
    }

    const response = await fetch("/api/refresh-achievements", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ app_id: appId })
    });

    await response.json();
    await loadActiveGame();
    await loadAchievements(appId);
}

if (document.getElementById("counter")) {
    updateOverlay();

    setInterval(async () => {
        await fetch("/api/refresh-achievements", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            }
        });

        await updateOverlay();
    }, 5000);
}

document.addEventListener("DOMContentLoaded", async () => {
    await loadGames();
    const activeGameData = await loadActiveGame();

    if (activeGameData.active_app_id) {
        await loadAchievements(activeGameData.active_app_id);
    }

    document
        .getElementById("apply-game-button")
        .addEventListener("click", applySelectedGame);

    document
        .getElementById("refresh-game-button")
        .addEventListener("click", refreshSelectedGame);

    if (document.getElementById("game-select")) {
        setInterval(async () => {
            const activeGame = await loadActiveGame();

            if (activeGame.active_app_id) {
                await loadAchievements(activeGame.active_app_id);
            }
        }, 5000);
    }
});