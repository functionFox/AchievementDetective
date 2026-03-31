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

    const unlocked = state.achievements.filter(a => a.achieved);
    const locked = state.achievements.filter(a => !a.achieved);

    const sorted = [...unlocked, ...locked];

    const html = [
        ...unlocked.map(a => `<div class="item unlocked">${a.display_name}</div>`),
        `<hr class="divider">`,
        ...locked.map(a => `<div class="item locked">${a.display_name}</div>`)
    ].join("");

    list.innerHTML = html;

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