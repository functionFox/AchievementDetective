let lastEventTimestamp = 0;

async function fetchJson(url) {
    const response = await fetch(url);
    return await response.json();
}

async function updateOverlay() {
    const state = await fetchJson("/api/state");
    const event = await fetchJson("/api/event");

    document.getElementById("counter").innerText = `${state.unlocked} / ${state.total}`;

    const list = document.getElementById("list");
    list.innerHTML = state.achievements
        .map(achievement => `<div class="item">${achievement.display_name}</div>`)
        .join("");

    if (event.timestamp > lastEventTimestamp && event.latest) {
        lastEventTimestamp = event.timestamp;

        const latest = document.getElementById("latest");
        latest.innerText = `Unlocked: ${event.latest.display_name}`;
        latest.classList.add("show");

        setTimeout(() => {
            latest.classList.remove("show");
        }, 3000);
    }
}

setInterval(updateOverlay, 1000);
updateOverlay();