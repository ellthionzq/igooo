/**
 * Lightweight Birthday Website Controller
 * 1. Live Stage 0 countdown ticker (progressive enhancement)
 * 2. Reload-free Stage 1 <-> Stage 2 transitions so the Opening Song keeps playing
 * 3. Spotify Embed IFrame API integration to auto-pause Opening Song when any
 *    song in "3 Songs That Remind Me of You" starts playing (and vice versa)
 */

(() => {
  "use strict";

  // --------------------------------------------------------------------------
  // 1. STAGE 0 LIVE COUNTDOWN
  // --------------------------------------------------------------------------
  const countdownEl = document.getElementById("stage0-countdown");
  if (countdownEl) {
    const targetIso = countdownEl.dataset.targetIso;
    const targetTime = targetIso ? new Date(targetIso).getTime() : NaN;
    const unlockUrl = countdownEl.dataset.unlockUrl || "/stage1";

    const daysEl = countdownEl.querySelector('[data-unit="days"]');
    const hoursEl = countdownEl.querySelector('[data-unit="hours"]');
    const minutesEl = countdownEl.querySelector('[data-unit="minutes"]');
    const secondsEl = countdownEl.querySelector('[data-unit="seconds"]');

    if (!Number.isNaN(targetTime) && daysEl && hoursEl && minutesEl && secondsEl) {
      const pad = (n) => String(Math.max(0, n)).padStart(2, "0");

      const tick = () => {
        const diff = targetTime - Date.now();
        if (diff <= 0) {
          window.location.href = unlockUrl;
          return;
        }
        const total = Math.floor(diff / 1000);
        daysEl.textContent = pad(Math.floor(total / 86400));
        hoursEl.textContent = pad(Math.floor((total % 86400) / 3600));
        minutesEl.textContent = pad(Math.floor((total % 3600) / 60));
        secondsEl.textContent = pad(total % 60);
      };

      tick();
      setInterval(tick, 1000);
    }
  }

  // --------------------------------------------------------------------------
  // 2. SEAMLESS STAGE 1 <-> STAGE 2 TRANSITIONS (NO IFRAME RELOAD)
  // --------------------------------------------------------------------------
  const celebrationRoot = document.getElementById("celebration-root");
  if (!celebrationRoot) return;

  const continueBtn = document.getElementById("continue-stage2-btn");
  const backBtn = document.getElementById("back-to-stage1-btn");
  const openingDock = document.getElementById("opening-player-dock");
  const dockToggleBtn = document.getElementById("dock-toggle-btn");
  const dockStatusEl = document.getElementById("dock-status-label");

  function setStage(stageNum, pushHistory = true) {
    const target = String(stageNum);
    celebrationRoot.dataset.activeStage = target;

    if (pushHistory && window.history && window.history.pushState) {
      const targetUrl =
        target === "2"
          ? celebrationRoot.dataset.stage2Url || "/stage2"
          : celebrationRoot.dataset.stage1Url || "/stage1";
      window.history.pushState({ stage: target }, "", targetUrl);
    }

    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  if (continueBtn) {
    continueBtn.addEventListener("click", (event) => {
      event.preventDefault();
      setStage("2", true);
    });
  }

  if (backBtn) {
    backBtn.addEventListener("click", (event) => {
      event.preventDefault();
      setStage("1", true);
    });
  }

  window.addEventListener("popstate", (event) => {
    if (event.state && event.state.stage) {
      setStage(event.state.stage, false);
    } else if (window.location.pathname.endsWith("/stage2")) {
      setStage("2", false);
    } else {
      setStage("1", false);
    }
  });

  if (dockToggleBtn && openingDock) {
    dockToggleBtn.addEventListener("click", () => {
      const minimized = openingDock.classList.toggle("is-minimized");
      dockToggleBtn.setAttribute("aria-expanded", String(!minimized));
      dockToggleBtn.textContent = minimized ? "Show Player" : "Minimize";
    });
  }

  // --------------------------------------------------------------------------
  // 3. SPOTIFY EMBED IFRAME API — AUTO-PAUSE WHEN ANOTHER TRACK PLAYS
  // --------------------------------------------------------------------------
  const playerTargets = Array.from(document.querySelectorAll(".spotify-api-target"));
  const controllers = {};
  let spotifyApiReady = false;

  function pauseController(ctrl) {
    if (!ctrl) return;
    if (typeof ctrl.pause === "function") {
      ctrl.pause();
    } else if (typeof ctrl.togglePlay === "function") {
      ctrl.togglePlay();
    }
  }

  function updateOpeningStatus(isPlaying) {
    if (!dockStatusEl || !openingDock) return;
    openingDock.classList.toggle("is-playing", isPlaying);
    dockStatusEl.textContent = isPlaying ? "Now Playing · Opening Song" : "Opening Song";
  }

  function mountFallbackIframes() {
    if (spotifyApiReady) return;
    playerTargets.forEach((el) => {
      if (el.dataset.mounted === "true") return;
      const fallbackUrl = el.dataset.fallbackEmbed;
      if (!fallbackUrl) return;
      const iframe = document.createElement("iframe");
      iframe.className = "spotify-iframe";
      iframe.src = fallbackUrl;
      iframe.title = el.dataset.playerTitle || "Spotify Player";
      iframe.loading = "lazy";
      iframe.allow = "autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture";
      iframe.setAttribute("allowfullscreen", "");
      el.innerHTML = "";
      el.appendChild(iframe);
      el.dataset.mounted = "true";
    });
  }

  window.onSpotifyIframeApiReady = (IFrameAPI) => {
    spotifyApiReady = true;

    playerTargets.forEach((el) => {
      const playerId = el.dataset.playerId;
      const uri = el.dataset.spotifyUri;
      if (!playerId || !uri) return;

      IFrameAPI.createController(
        el,
        {
          width: "100%",
          height: 152,
          uri: uri
        },
        (controller) => {
          el.dataset.mounted = "true";
          controllers[playerId] = { controller, isPlaying: false };

          controller.addListener("playback_update", (event) => {
            if (!event || !event.data) return;
            const isPlaying = event.data.isPaused === false;
            controllers[playerId].isPlaying = isPlaying;

            if (playerId === "opening") {
              updateOpeningStatus(isPlaying);
            }

            if (isPlaying) {
              Object.keys(controllers).forEach((otherId) => {
                if (otherId !== playerId && controllers[otherId].isPlaying) {
                  controllers[otherId].isPlaying = false;
                  pauseController(controllers[otherId].controller);
                  if (otherId === "opening") {
                    updateOpeningStatus(false);
                  }
                }
              });
            }
          });
        }
      );
    });
  };

  // Fallback to standard Spotify embed iframe if the IFrame API script is blocked
  setTimeout(mountFallbackIframes, 4500);
})();
