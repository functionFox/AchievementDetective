let lastEventTimestamp = 0;
let hasInitializedEventTimestamp = false;
let currentOverlayState = null;
let pendingOverlayState = null;
let overlayCycleMode = null;
let obeliskCycleTimeoutId = null;

async function fetchJson(url) {
    const response = await fetch(url);
    return await response.json();
}

function applyOverlayTextSettings(settings) {
  document.documentElement.style.setProperty(
    "--overlay-text-color",
    settings.text_color || "#000000"
  );
  document.documentElement.style.setProperty(
    "--overlay-text-stroke-width",
    `${settings.text_stroke_width || 0}px`
  );
  document.documentElement.style.setProperty(
    "--overlay-text-stroke-color",
    settings.text_stroke_color || "#ffffff"
  );
  document.documentElement.style.setProperty(
    "--obelisk-angle",
    `${settings.obelisk_angle || 63}deg`
  );

  const tickerColor = settings.ticker_strip_color || "#141a28";
  const tickerOpacity = Number(settings.ticker_strip_opacity ?? 78) / 100;

  const hex = tickerColor.replace("#", "");
  const normalized = hex.length === 3
    ? hex.split("").map(ch => ch + ch).join("")
    : hex;

  const r = parseInt(normalized.slice(0, 2), 16);
  const g = parseInt(normalized.slice(2, 4), 16);
  const b = parseInt(normalized.slice(4, 6), 16);

  document.documentElement.style.setProperty(
    "--ticker-strip-bg",
    `rgba(${r}, ${g}, ${b}, ${tickerOpacity})`
  );
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

    const content = [
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

    return `
        <div class="obelisk-crawl">
            <div class="obelisk-track">
                ${content}
            </div>
        </div>
    `;
}

function getObeliskDurationMs(state) {
    const count = state.achievements.length;

    const baseMs = 8000;
    const perItemMs = 650;

    return baseMs + (count * perItemMs);
}

function getTickerDurationMs(state) {
    const count = state.achievements.length;

    const baseMs = 12000;
    const perItemMs = 1800;

    return baseMs + (count * perItemMs);
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
        <div class="ticker-viewport">
            <div class="ticker-track">
                ${content}
                ${content}
            </div>
        </div>
    `;
}

function startTickerCycle() {
    overlayCycleMode = "ticker";

    const list = document.getElementById("list");
    const track = list.querySelector(".ticker-track");

    if (!track) {
        return;
    }

    track.addEventListener("animationiteration", () => {
        if (overlayCycleMode !== "ticker") {
            return;
        }

            if (commitPendingOverlayState()) {
                const nextDurationMs = getTickerDurationMs(currentOverlayState);
                list.style.setProperty("--ticker-duration", `${nextDurationMs}ms`);
                list.innerHTML = renderTicker(currentOverlayState);
                startTickerCycle();
        } else {
            startTickerCycle();
        }
    }, { once: true });
}

function startObeliskCycle() {
    overlayCycleMode = "obelisk";

    const list = document.getElementById("list");
    const track = list.querySelector(".obelisk-track");

    if (!track) {
        return;
    }

    track.addEventListener("animationiteration", () => {
        if (overlayCycleMode !== "obelisk") {
            return;
        }

        if (commitPendingOverlayState()) {
            const nextDurationMs = getObeliskDurationMs(currentOverlayState);
            list.style.setProperty("--obelisk-duration", `${nextDurationMs}ms`);
            list.innerHTML = renderObelisk(currentOverlayState);
            startObeliskCycle();
        } else {
            startObeliskCycle();
        }
    }, { once: true });
}

async function updateOverlay() {
    const latestState = await fetchJson("/api/state");
    const event = await fetchJson("/api/event");

    const isNewGame =
    currentOverlayState &&
    String(currentOverlayState.appid) !== String(latestState.appid);

    if (!currentOverlayState || isNewGame) {
        currentOverlayState = latestState;
        pendingOverlayState = null;

        const list = document.getElementById("list");
        if (list) {
            list.innerHTML = "";
        }

        overlayCycleMode = null;
    } else {
        pendingOverlayState = latestState;
    }

    const state = currentOverlayState;

    document.getElementById("counter").innerText = `${state.unlocked} / ${state.total}`;

    const list = document.getElementById("list");
    const activeGame = await fetchJson("/api/active-game");
    const displayMode = activeGame.display_mode || "obelisk";
    document.documentElement.dataset.displayMode = displayMode;

    applyOverlayTextSettings(activeGame);

    list.classList.remove("mode-obelisk", "mode-ticker");
    list.classList.add(displayMode === "ticker" ? "mode-ticker" : "mode-obelisk");

    if (overlayCycleMode !== displayMode) {
        list.innerHTML = "";
        overlayCycleMode = null;

        if (obeliskCycleTimeoutId) {
            clearTimeout(obeliskCycleTimeoutId);
            obeliskCycleTimeoutId = null;
        }
    }

    if (!list.innerHTML.trim()) {
        if (displayMode === "ticker") {
            const durationMs = getTickerDurationMs(state);
            list.style.setProperty("--ticker-duration", `${durationMs}ms`);
            list.innerHTML = renderTicker(state);
            startTickerCycle();
        } else {
            const durationMs = getObeliskDurationMs(state);
            list.style.setProperty("--obelisk-duration", `${durationMs}ms`);
            list.innerHTML = renderObelisk(state);
            startObeliskCycle();
        }
    }

        if (!hasInitializedEventTimestamp) {
            lastEventTimestamp = event.timestamp || 0;
            hasInitializedEventTimestamp = true;
        }

        if (event.timestamp > lastEventTimestamp && event.latest) {
        lastEventTimestamp = event.timestamp;

        const latest = document.getElementById("latest");
        const latestIcon = event.latest.icon || event.latest.icon_gray || "";
        const latestDescription = event.latest.description || "";

        latest.innerHTML = `
            <div class="achievement-toast unlocked">
            <img class="achievement-toast-icon" src="/static/${latestIcon}" alt="">
                <div class="achievement-toast-text">
                    <div class="achievement-toast-title">
                        Unlocked: ${event.latest.display_name}
                    </div>
                    ${latestDescription ? `
                        <div class="achievement-toast-description">
                            ${latestDescription}
                        </div>
                    ` : ""}
                    </div>
                </div>
               `;
        latest.classList.remove("toast-anim-jump");
        void latest.offsetWidth;
        latest.classList.add("show", "toast-anim-jump");

        setTimeout(() => {
            latest.classList.remove("toast-anim-jump");
        }, 1200);

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

async function rescanGames() {
    const button = document.getElementById("rescan-games-button");
    const select = document.getElementById("game-select");
    const previousValue = select.value;

    button.disabled = true;
    button.textContent = "Rescanning...";

    const response = await fetch("/api/rescan-games", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        }
    });

    await response.json();
    await loadGames();

    if (previousValue) {
        select.value = previousValue;
    }

    button.disabled = false;
    button.textContent = "Rescan Steam Games";
}

async function loadActiveGame(syncControls = true) {
  const response = await fetch("/api/active-game");
  const data = await response.json();

  const output = document.getElementById("active-game-output");
  output.textContent = JSON.stringify(data, null, 2);

  if (syncControls) {
    if (data.active_app_id) {
      document.getElementById("game-select").value = data.active_app_id;
    }

    if (data.display_mode) {
      document.getElementById("display-mode-select").value = data.display_mode;
    }
        if (data.text_color) {
      const textColorInput = document.getElementById("text-color-input");
      if (textColorInput) {
        textColorInput.value = data.text_color;
      }
    }

    if (data.text_stroke_width !== undefined) {
      const textStrokeWidthInput = document.getElementById("text-stroke-width-input");
      if (textStrokeWidthInput) {
        textStrokeWidthInput.value = data.text_stroke_width;
      }
    }

    if (data.text_stroke_color) {
      const textStrokeColorInput = document.getElementById("text-stroke-color-input");
      if (textStrokeColorInput) {
        textStrokeColorInput.value = data.text_stroke_color;
      }
    }

    if (data.ticker_strip_color) {
      const tickerStripColorInput = document.getElementById("ticker-strip-color-input");
      if (tickerStripColorInput) {
        tickerStripColorInput.value = data.ticker_strip_color;
      }
    }

    if (data.ticker_strip_opacity !== undefined) {
      const tickerStripOpacityInput = document.getElementById("ticker-strip-opacity-input");
      if (tickerStripOpacityInput) {
        tickerStripOpacityInput.value = data.ticker_strip_opacity;
      }
    }
    if (data.obelisk_angle !== undefined) {
      const obeliskAngleInput = document.getElementById("obelisk-angle-input");
      if (obeliskAngleInput) {
        obeliskAngleInput.value = data.obelisk_angle;
      }
    }
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
    const textColorInput = document.getElementById("text-color-input");
    const textStrokeWidthInput = document.getElementById("text-stroke-width-input");
    const textStrokeColorInput = document.getElementById("text-stroke-color-input");

    const appId = select.value;
    const displayMode = modeSelect.value;
    const textColor = textColorInput.value;
    const textStrokeWidth = textStrokeWidthInput.value;
    const textStrokeColor = textStrokeColorInput.value;
    const tickerStripColorInput = document.getElementById("ticker-strip-color-input");
    const tickerStripOpacityInput = document.getElementById("ticker-strip-opacity-input");
    const tickerStripColor = tickerStripColorInput ? tickerStripColorInput.value : null;
    const tickerStripOpacity = tickerStripOpacityInput ? tickerStripOpacityInput.value : null;
    const obeliskAngleInput = document.getElementById("obelisk-angle-input");
    const obeliskAngle = obeliskAngleInput ? obeliskAngleInput.value : null;

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
              display_mode: displayMode,
              text_color: textColor,
              text_stroke_width: textStrokeWidth,
              text_stroke_color: textStrokeColor,
              ticker_strip_color: tickerStripColor,
              ticker_strip_opacity: tickerStripOpacity,
              obelisk_angle: obeliskAngle
            })
    });

    const state = await response.json();

    await loadActiveGame();

    await loadAchievements(appId);
}

async function refreshSelectedGame() {
    const activeGame = await loadActiveGame();
    const appId = activeGame.active_app_id;

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
    await loadAchievements(appId);
}

if (document.getElementById("counter")) {
    updateOverlay();

    setInterval(async () => {
        const activeGame = await fetchJson("/api/active-game");

        if (activeGame.active_app_id) {
            await fetch("/api/refresh-achievements", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                }
            });
        }

        await updateOverlay();
    }, 1000);
}

document.addEventListener("DOMContentLoaded", async () => {
    await loadGames();
    const activeGame = await loadActiveGame(true);

    if (activeGame.active_app_id) {
        document.getElementById("game-select").value = activeGame.active_app_id;
        await loadAchievements(activeGame.active_app_id);
    }

    document
        .getElementById("apply-game-button")
        .addEventListener("click", applySelectedGame);

    document
        .getElementById("refresh-game-button")
        .addEventListener("click", refreshSelectedGame);

    document
        .getElementById("rescan-games-button")
        .addEventListener("click", rescanGames);

    if (document.getElementById("game-select")) {
        setInterval(async () => {
            const activeGame = await loadActiveGame(false);

            if (activeGame.active_app_id) {
                await loadAchievements(activeGame.active_app_id);
            }
        }, 5000);
    }
});