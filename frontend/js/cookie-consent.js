(function() {
    const CONSENT_KEY = 'futuremap_cookie_consent';

    const defaultConsent = {
        essential: true,
        analytics: false,
        preferences: false,
        learningProgress: true
    };

    function getConsent() {
        const stored = localStorage.getItem(CONSENT_KEY);
        if (!stored) return null;

        try {
            return JSON.parse(stored);
        } catch (error) {
            return null;
        }
    }

    function saveConsent(consent) {
        const normalized = {
            essential: true,
            analytics: !!consent.analytics,
            preferences: !!consent.preferences,
            learningProgress: true
        };

        localStorage.setItem(CONSENT_KEY, JSON.stringify(normalized));
        document.dispatchEvent(new CustomEvent('cookie-consent:updated', { detail: normalized }));
    }

    function injectHTML() {
        if (document.getElementById('cookie-consent-banner')) return;

        const banner = document.createElement('div');
        banner.id = 'cookie-consent-banner';
        banner.innerHTML = `
            <div class="cookie-banner-inner" role="dialog" aria-live="polite" aria-label="Cookie consent">
                <div class="cookie-banner-icon" aria-hidden="true">
                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                        <circle cx="12" cy="12" r="9"></circle>
                        <path d="M8 9h.01M12 7h.01M15 11h.01M10 15h.01M16 16h.01"></path>
                    </svg>
                </div>
                <div class="cookie-banner-text">
                    <h3>Cookie Preferences</h3>
                    <p>Future Map uses essential cookies for login sessions, authentication, learning progress, analytics, and saved preferences. Optional cookies stay off until you allow them.</p>
                </div>
                <div class="cookie-banner-actions">
                    <button class="cookie-btn-reject" id="cookie-essential-only" type="button">Essential Only</button>
                    <button class="cookie-btn-manage" id="cookie-manage-pref" type="button">Manage Preferences</button>
                    <button class="cookie-btn-accept" id="cookie-accept-all" type="button">Accept All</button>
                </div>
            </div>
        `;

        const modal = document.createElement('div');
        modal.id = 'cookie-preferences-modal';
        modal.innerHTML = `
            <div class="cookie-modal-overlay" id="cookie-modal-overlay"></div>
            <div class="cookie-modal-card" role="dialog" aria-modal="true" aria-labelledby="cookie-modal-title">
                <div class="cookie-modal-header">
                    <div>
                        <h2 id="cookie-modal-title">Manage Cookies</h2>
                        <p>Choose how Future Map may remember and improve your learning and career planning experience.</p>
                    </div>
                    <button class="cookie-modal-close" id="cookie-modal-close" type="button" aria-label="Close cookie preferences">x</button>
                </div>
                <div class="cookie-modal-body">
                    <div class="cookie-toggle-row">
                        <div class="cookie-toggle-info">
                            <h4>Login Sessions</h4>
                            <p>Required for secure authentication, protected routes, and session handling.</p>
                        </div>
                        <span class="cookie-toggle-required">Required</span>
                    </div>
                    <div class="cookie-toggle-row">
                        <div class="cookie-toggle-info">
                            <h4>Learning Progress</h4>
                            <p>Required to remember completed lessons, visualization states, and practice history.</p>
                        </div>
                        <span class="cookie-toggle-required">Required</span>
                    </div>
                    <div class="cookie-toggle-row">
                        <div class="cookie-toggle-info">
                            <h4>Analytics</h4>
                            <p>Optional usage signals that help improve algorithm lessons and page performance.</p>
                        </div>
                        <label class="cookie-toggle" aria-label="Allow analytics cookies">
                            <input type="checkbox" id="cookie-toggle-analytics">
                            <span class="cookie-toggle-track"></span>
                        </label>
                    </div>
                    <div class="cookie-toggle-row">
                        <div class="cookie-toggle-info">
                            <h4>Preferences</h4>
                            <p>Optional settings such as theme choices, preferred difficulty, and animation speed.</p>
                        </div>
                        <label class="cookie-toggle" aria-label="Allow preference cookies">
                            <input type="checkbox" id="cookie-toggle-preferences">
                            <span class="cookie-toggle-track"></span>
                        </label>
                    </div>
                </div>
                <div class="cookie-modal-footer">
                    <button class="cookie-accept-all-btn" id="cookie-modal-accept-all" type="button">Accept All</button>
                    <button class="cookie-save-btn" id="cookie-modal-save" type="button">Save Preferences</button>
                </div>
            </div>
        `;

        document.body.appendChild(banner);
        document.body.appendChild(modal);
        setupEventListeners();
    }

    function openModal() {
        const modal = document.getElementById('cookie-preferences-modal');
        if (!modal) return;

        const consent = getConsent() || defaultConsent;
        document.getElementById('cookie-toggle-analytics').checked = !!consent.analytics;
        document.getElementById('cookie-toggle-preferences').checked = !!consent.preferences;
        modal.classList.add('visible');
    }

    function closeModal() {
        const modal = document.getElementById('cookie-preferences-modal');
        if (modal) modal.classList.remove('visible');
    }

    function hideBanner() {
        const banner = document.getElementById('cookie-consent-banner');
        if (banner) banner.classList.remove('visible');
    }

    function setupEventListeners() {
        document.getElementById('cookie-accept-all').addEventListener('click', () => {
            saveConsent({ analytics: true, preferences: true });
            hideBanner();
        });

        document.getElementById('cookie-essential-only').addEventListener('click', () => {
            saveConsent({ analytics: false, preferences: false });
            hideBanner();
        });

        document.getElementById('cookie-manage-pref').addEventListener('click', openModal);
        document.getElementById('cookie-modal-close').addEventListener('click', closeModal);
        document.getElementById('cookie-modal-overlay').addEventListener('click', closeModal);

        document.getElementById('cookie-modal-accept-all').addEventListener('click', () => {
            saveConsent({ analytics: true, preferences: true });
            closeModal();
            hideBanner();
        });

        document.getElementById('cookie-modal-save').addEventListener('click', () => {
            saveConsent({
                analytics: document.getElementById('cookie-toggle-analytics').checked,
                preferences: document.getElementById('cookie-toggle-preferences').checked
            });
            closeModal();
            hideBanner();
        });
    }

    function init() {
        injectHTML();

        if (!getConsent()) {
            window.setTimeout(() => {
                const banner = document.getElementById('cookie-consent-banner');
                if (banner) banner.classList.add('visible');
            }, 800);
        }
    }

    window.CookieConsent = {
        openPreferences: openModal,
        getConsentSettings: getConsent,
        hasConsented: () => getConsent() !== null
    };

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
