/**
 * Slovíčka — Flashcard App
 *
 * A gentle, accessible flashcard viewer for Czech–English word pairs.
 * Loads data from JSON files, renders a card grid, and provides a
 * detail overlay with 3D flip animation, audio playback, and
 * keyboard/swipe navigation.
 */

(function () {
    "use strict";

    // =========================================================
    // State
    // =========================================================
    var state = {
        currentWeek: null,     // e.g. "2026-W13"
        words: [],             // array of word objects for current week
        currentCardIndex: 0,
        isFlipped: false,
        isDetailOpen: false,
        weeksIndex: null       // the full index.json data
    };

    // =========================================================
    // DOM References
    // =========================================================
    var dom = {};

    function cacheDom() {
        dom.grid = document.getElementById("card-grid");
        dom.overlay = document.getElementById("overlay");
        dom.overlayBackdrop = document.getElementById("overlay-backdrop");
        dom.cardFlipper = document.getElementById("card-flipper");
        dom.cardScene = document.getElementById("card-scene");
        dom.cardImageFront = document.getElementById("card-image-front");
        dom.cardImageBack = document.getElementById("card-image-back");
        dom.cardWordCs = document.getElementById("card-word-cs");
        dom.cardWordEn = document.getElementById("card-word-en");
        dom.cardPronunciation = document.getElementById("card-pronunciation");
        dom.cardCounter = document.getElementById("card-counter");
        dom.weekTitle = document.getElementById("week-title");
        dom.weekSelect = document.getElementById("week-select");
        dom.btnClose = document.getElementById("btn-close");
        dom.btnPrev = document.getElementById("btn-prev");
        dom.btnNext = document.getElementById("btn-next");
        dom.btnAudioCs = document.getElementById("btn-audio-cs");
        dom.btnAudioEn = document.getElementById("btn-audio-en");
    }

    // =========================================================
    // Data Loading
    // =========================================================

    /**
     * Fetch JSON from a relative URL. Returns parsed data or null on error.
     */
    function fetchJSON(url) {
        return fetch(url)
            .then(function (res) {
                if (!res.ok) throw new Error("HTTP " + res.status);
                return res.json();
            })
            .catch(function () {
                return null;
            });
    }

    /**
     * Load the week index and determine which week to show.
     */
    function init() {
        cacheDom();
        bindEvents();

        fetchJSON("data/index.json").then(function (data) {
            if (!data || !data.weeks || data.weeks.length === 0) {
                showEmpty("Žádná slovíčka nejsou k dispozici.");
                return;
            }

            state.weeksIndex = data;
            populateWeekSelector(data.weeks, data.current_week);

            // Check URL hash for a specific week or card
            var hashWeek = getHashWeek();
            var weekToLoad = hashWeek || data.current_week || data.weeks[0].week_id;

            loadWeek(weekToLoad);
        });
    }

    /**
     * Load a week's word data and render the grid.
     */
    function loadWeek(weekId) {
        state.currentWeek = weekId;

        // Update selector to reflect loaded week
        if (dom.weekSelect.value !== weekId) {
            dom.weekSelect.value = weekId;
        }

        // Update subtitle
        var weekInfo = findWeekInfo(weekId);
        if (weekInfo) {
            dom.weekTitle.textContent = weekInfo.title + " — " + weekInfo.title_en;
        }

        showLoading();

        fetchJSON("data/week-" + weekId + ".json").then(function (data) {
            if (!data || !data.words || data.words.length === 0) {
                showEmpty("Pro tento týden nejsou žádná slovíčka.");
                return;
            }

            state.words = data.words;
            renderGrid(data.words, weekId);

            // Check hash for detail view
            var hashIndex = getHashCardIndex();
            if (hashIndex !== null && hashIndex >= 0 && hashIndex < data.words.length) {
                openDetail(hashIndex);
            }
        });
    }

    /**
     * Find week info from the index by week_id.
     */
    function findWeekInfo(weekId) {
        if (!state.weeksIndex) return null;
        for (var i = 0; i < state.weeksIndex.weeks.length; i++) {
            if (state.weeksIndex.weeks[i].week_id === weekId) {
                return state.weeksIndex.weeks[i];
            }
        }
        return null;
    }

    // =========================================================
    // Rendering
    // =========================================================

    function showLoading() {
        dom.grid.innerHTML = '<p class="loading-message">Načítám slovíčka…</p>';
    }

    function showEmpty(message) {
        dom.grid.innerHTML = '<p class="empty-message">' + escapeHtml(message) + '</p>';
    }

    /**
     * Render the card grid from word data.
     */
    function renderGrid(words, weekId) {
        var html = "";
        for (var i = 0; i < words.length; i++) {
            var word = words[i];
            var imgSrc = "data/" + weekId + "/" + word.image;
            html +=
                '<div class="grid-card" role="listitem" tabindex="0" data-index="' + i + '">' +
                    '<img class="grid-card-image" src="' + escapeAttr(imgSrc) + '"' +
                        ' alt="' + escapeAttr(word.czech) + '"' +
                        ' loading="' + (i < 4 ? "eager" : "lazy") + '">' +
                    '<p class="grid-card-label">' + escapeHtml(word.czech) + '</p>' +
                '</div>';
        }
        dom.grid.innerHTML = html;

        // Preload first few images (they should already be eager, but also preload audio)
        if (words.length > 0) {
            preloadCardAudio(0, weekId);
        }
    }

    // =========================================================
    // Detail Overlay
    // =========================================================

    /**
     * Open the detail overlay for a specific card index.
     */
    function openDetail(index) {
        state.currentCardIndex = index;
        state.isFlipped = false;
        state.isDetailOpen = true;

        // Reset flip
        dom.cardFlipper.classList.remove("flipped");

        // Populate card content
        populateCard(index);

        // Show overlay
        dom.overlay.hidden = false;
        document.body.style.overflow = "hidden";

        // Update hash
        updateHash();

        // Update navigation buttons
        updateNavButtons();

        // Auto-play Czech audio after a short delay
        setTimeout(function () {
            if (state.isDetailOpen && !state.isFlipped) {
                playAudio("cs");
            }
        }, 1000);
    }

    /**
     * Close the detail overlay and return to grid.
     */
    function closeDetail() {
        state.isDetailOpen = false;
        dom.overlay.hidden = true;
        document.body.style.overflow = "";
        stopAllAudio();

        // Clear hash
        if (window.history && window.history.replaceState) {
            window.history.replaceState(null, "", window.location.pathname + window.location.search);
        } else {
            window.location.hash = "";
        }
    }

    /**
     * Populate the detail card with word data.
     */
    function populateCard(index) {
        var word = state.words[index];
        if (!word) return;

        var weekId = state.currentWeek;
        var imgSrc = "data/" + weekId + "/" + word.image;

        dom.cardImageFront.src = imgSrc;
        dom.cardImageFront.alt = word.czech;
        dom.cardImageBack.src = imgSrc;
        dom.cardImageBack.alt = word.english;

        dom.cardWordCs.textContent = word.czech;
        dom.cardWordEn.textContent = word.english;
        dom.cardPronunciation.textContent = "[" + word.pronunciation + "]";

        // Update counter
        dom.cardCounter.textContent = (index + 1) + " / " + state.words.length;

        // Preload audio for this card and next
        preloadCardAudio(index, weekId);
        if (index + 1 < state.words.length) {
            preloadCardAudio(index + 1, weekId);
        }
    }

    /**
     * Flip the card to the other side.
     */
    function flipCard() {
        state.isFlipped = !state.isFlipped;

        if (state.isFlipped) {
            dom.cardFlipper.classList.add("flipped");
            // Play English audio after flip settles
            setTimeout(function () {
                if (state.isDetailOpen && state.isFlipped) {
                    playAudio("en");
                }
            }, 500);
        } else {
            dom.cardFlipper.classList.remove("flipped");
        }
    }

    /**
     * Navigate to the next card.
     */
    function nextCard() {
        if (state.currentCardIndex < state.words.length - 1) {
            stopAllAudio();
            openDetail(state.currentCardIndex + 1);
        }
    }

    /**
     * Navigate to the previous card.
     */
    function prevCard() {
        if (state.currentCardIndex > 0) {
            stopAllAudio();
            openDetail(state.currentCardIndex - 1);
        }
    }

    /**
     * Update prev/next button disabled state.
     */
    function updateNavButtons() {
        dom.btnPrev.disabled = state.currentCardIndex <= 0;
        dom.btnNext.disabled = state.currentCardIndex >= state.words.length - 1;
    }

    // =========================================================
    // Audio
    // =========================================================
    var audioCache = {};
    var currentAudio = null;

    /**
     * Preload audio files for a given card index.
     */
    function preloadCardAudio(index, weekId) {
        var word = state.words[index];
        if (!word) return;

        var csUrl = "data/" + weekId + "/" + word.audio_cs;
        var enUrl = "data/" + weekId + "/" + word.audio_en;

        preloadAudioFile(csUrl);
        preloadAudioFile(enUrl);
    }

    function preloadAudioFile(url) {
        if (audioCache[url]) return;
        var audio = new Audio();
        audio.preload = "auto";
        audio.src = url;
        audioCache[url] = audio;
    }

    /**
     * Play audio for the current card. lang is "cs" or "en".
     */
    function playAudio(lang) {
        var word = state.words[state.currentCardIndex];
        if (!word) return;

        var weekId = state.currentWeek;
        var audioFile = lang === "cs" ? word.audio_cs : word.audio_en;
        var url = "data/" + weekId + "/" + audioFile;

        stopAllAudio();

        // Try cached audio element
        var audio = audioCache[url];
        if (!audio) {
            audio = new Audio(url);
            audioCache[url] = audio;
        }

        currentAudio = audio;
        audio.currentTime = 0;

        var playPromise = audio.play();
        if (playPromise && playPromise.catch) {
            playPromise.catch(function () {
                // Audio failed — try speechSynthesis as fallback
                trySpeechFallback(word, lang);
            });
        }
    }

    /**
     * Use browser speechSynthesis as fallback if audio files are missing.
     */
    function trySpeechFallback(word, lang) {
        if (!window.speechSynthesis) return;

        var text = lang === "cs" ? word.czech : word.english;
        var utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = lang === "cs" ? "cs-CZ" : "en-US";
        utterance.rate = 0.85;
        window.speechSynthesis.speak(utterance);
    }

    /**
     * Stop any currently playing audio.
     */
    function stopAllAudio() {
        if (currentAudio) {
            currentAudio.pause();
            currentAudio.currentTime = 0;
            currentAudio = null;
        }
        if (window.speechSynthesis) {
            window.speechSynthesis.cancel();
        }
    }

    // =========================================================
    // Week Selector
    // =========================================================

    function populateWeekSelector(weeks, currentWeek) {
        var html = "";
        for (var i = 0; i < weeks.length; i++) {
            var w = weeks[i];
            var selected = w.week_id === currentWeek ? " selected" : "";
            html +=
                '<option value="' + escapeAttr(w.week_id) + '"' + selected + '>' +
                    escapeHtml(w.title) + ' (' + escapeHtml(w.week_id) + ')' +
                '</option>';
        }
        dom.weekSelect.innerHTML = html;
    }

    // =========================================================
    // Hash / URL management
    // =========================================================

    function getHashWeek() {
        // Hash format: #detail/2 or #week/2026-W13/3
        var hash = window.location.hash.replace("#", "");
        var parts = hash.split("/");
        if (parts[0] === "week" && parts[1]) {
            return parts[1];
        }
        return null;
    }

    function getHashCardIndex() {
        var hash = window.location.hash.replace("#", "");
        var parts = hash.split("/");
        if (parts[0] === "detail" && parts[1]) {
            return parseInt(parts[1], 10);
        }
        if (parts[0] === "week" && parts[2]) {
            return parseInt(parts[2], 10);
        }
        return null;
    }

    function updateHash() {
        var hash = "#detail/" + state.currentCardIndex;
        if (window.history && window.history.replaceState) {
            window.history.replaceState(null, "", hash);
        } else {
            window.location.hash = hash;
        }
    }

    // =========================================================
    // Touch / Swipe
    // =========================================================
    var touchStartX = 0;
    var touchStartY = 0;

    function handleTouchStart(e) {
        touchStartX = e.changedTouches[0].clientX;
        touchStartY = e.changedTouches[0].clientY;
    }

    function handleTouchEnd(e) {
        if (!state.isDetailOpen) return;

        var dx = e.changedTouches[0].clientX - touchStartX;
        var dy = e.changedTouches[0].clientY - touchStartY;

        // Only count horizontal swipes (more horizontal than vertical)
        if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy) * 1.5) {
            if (dx < 0) {
                nextCard(); // swipe left = next
            } else {
                prevCard(); // swipe right = prev
            }
        }
    }

    // =========================================================
    // Events
    // =========================================================

    function bindEvents() {
        // Grid card clicks (delegated)
        dom.grid.addEventListener("click", function (e) {
            var card = e.target.closest(".grid-card");
            if (card) {
                var index = parseInt(card.getAttribute("data-index"), 10);
                openDetail(index);
            }
        });

        // Grid card keyboard activation
        dom.grid.addEventListener("keydown", function (e) {
            if (e.key === "Enter" || e.key === " ") {
                var card = e.target.closest(".grid-card");
                if (card) {
                    e.preventDefault();
                    var index = parseInt(card.getAttribute("data-index"), 10);
                    openDetail(index);
                }
            }
        });

        // Close overlay
        dom.btnClose.addEventListener("click", closeDetail);
        dom.overlayBackdrop.addEventListener("click", closeDetail);

        // Navigation
        dom.btnPrev.addEventListener("click", function (e) {
            e.stopPropagation();
            prevCard();
        });
        dom.btnNext.addEventListener("click", function (e) {
            e.stopPropagation();
            nextCard();
        });

        // Flip card by clicking on it
        dom.cardScene.addEventListener("click", function (e) {
            // Don't flip if clicking audio button or nav
            if (e.target.closest(".btn-audio") || e.target.closest(".btn-nav")) return;
            flipCard();
        });

        // Audio buttons
        dom.btnAudioCs.addEventListener("click", function (e) {
            e.stopPropagation();
            playAudio("cs");
        });
        dom.btnAudioEn.addEventListener("click", function (e) {
            e.stopPropagation();
            playAudio("en");
        });

        // Week selector
        dom.weekSelect.addEventListener("change", function () {
            var weekId = dom.weekSelect.value;
            if (weekId && weekId !== state.currentWeek) {
                closeDetail();
                loadWeek(weekId);
            }
        });

        // Keyboard navigation
        document.addEventListener("keydown", function (e) {
            if (!state.isDetailOpen) return;

            switch (e.key) {
                case "Escape":
                    closeDetail();
                    break;
                case "ArrowLeft":
                    prevCard();
                    break;
                case "ArrowRight":
                    nextCard();
                    break;
                case " ":
                    e.preventDefault();
                    flipCard();
                    break;
            }
        });

        // Touch/swipe on overlay
        dom.overlay.addEventListener("touchstart", handleTouchStart, { passive: true });
        dom.overlay.addEventListener("touchend", handleTouchEnd, { passive: true });

        // Hash change (back button support)
        window.addEventListener("hashchange", function () {
            var hashIndex = getHashCardIndex();
            if (hashIndex !== null && state.isDetailOpen) {
                if (hashIndex !== state.currentCardIndex) {
                    openDetail(hashIndex);
                }
            } else if (hashIndex === null && state.isDetailOpen) {
                closeDetail();
            }
        });
    }

    // =========================================================
    // Utilities
    // =========================================================

    function escapeHtml(str) {
        var div = document.createElement("div");
        div.appendChild(document.createTextNode(str));
        return div.innerHTML;
    }

    function escapeAttr(str) {
        return str.replace(/&/g, "&amp;").replace(/"/g, "&quot;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
    }

    // =========================================================
    // Start
    // =========================================================

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();
