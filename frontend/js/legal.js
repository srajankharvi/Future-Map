/**
 * FUTURE MAP — Legal Pages Navigation & Selection Animation (Terms & Privacy)
 */

document.addEventListener('DOMContentLoaded', () => {
    const navList = document.querySelector('.legal-nav-list');
    const navLinks = document.querySelectorAll('.legal-nav-link');
    const sections = document.querySelectorAll('.legal-section');
    
    if (!navList || navLinks.length === 0) return;

    // 1. Create and Append the Dynamic Indicator
    const indicator = document.createElement('div');
    indicator.className = 'legal-nav-indicator';
    navList.appendChild(indicator);

    // Enable JS-specific styles (removes the default backgrounds/borders from active link)
    navList.classList.add('js-active');

    let isScrollingFromClick = false;
    let clickTimeout = null;

    // 2. Position the Indicator Dynamically
    const updateIndicator = () => {
        const activeLink = document.querySelector('.legal-nav-link.active');
        if (!activeLink || !indicator) return;

        const isMobile = window.innerWidth <= 1024;
        
        if (isMobile) {
            // Horizontal sliding pill on mobile layout
            indicator.classList.add('mobile-mode');
            indicator.style.left = `${activeLink.offsetLeft}px`;
            indicator.style.top = `${activeLink.offsetTop}px`;
            indicator.style.width = `${activeLink.offsetWidth}px`;
            indicator.style.height = `${activeLink.offsetHeight}px`;
        } else {
            // Vertical sliding pill on desktop layout
            indicator.classList.remove('mobile-mode');
            indicator.style.left = '0';
            indicator.style.top = `${activeLink.offsetTop}px`;
            indicator.style.width = '100%';
            indicator.style.height = `${activeLink.offsetHeight}px`;
        }
        indicator.style.opacity = '1';
    };

    // 3. Scroll Spy (Active class updates on scroll)
    const handleScrollSpy = () => {
        if (isScrollingFromClick) return; // Prevent jitter during click scroll transitions

        let currentId = '';
        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            // Trigger 180px before the section hits the top of viewport (navbar height offset)
            if (window.scrollY >= (sectionTop - 180)) {
                currentId = section.getAttribute('id');
            }
        });

        // Fallback to first item if at the very top of page
        if (window.scrollY < 100 && sections.length > 0) {
            currentId = sections[0].getAttribute('id');
        }

        let stateChanged = false;
        navLinks.forEach(link => {
            const hasActive = link.classList.contains('active');
            const shouldBeActive = link.getAttribute('href') === `#${currentId}`;

            if (shouldBeActive && !hasActive) {
                link.classList.add('active');
                stateChanged = true;
            } else if (!shouldBeActive && hasActive) {
                link.classList.remove('active');
                stateChanged = true;
            }
        });

        if (stateChanged) {
            updateIndicator();
        }
    };

    // 4. Smooth Anchor Link Clicks with Offset
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = link.getAttribute('href');
            const targetSection = document.querySelector(targetId);

            if (targetSection) {
                // Clear any existing scroll timeout
                if (clickTimeout) clearTimeout(clickTimeout);
                isScrollingFromClick = true;

                // Instantly update active class and indicator (gives visual snappiness)
                navLinks.forEach(l => l.classList.remove('active'));
                link.classList.add('active');
                updateIndicator();

                // Smooth scroll to the section with proper header offset
                const offset = 120; // Accounts for sticky header + spacing
                const targetPosition = targetSection.offsetTop - offset;

                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });

                // Re-enable scroll spy after the smooth scrolling finishes
                clickTimeout = setTimeout(() => {
                    isScrollingFromClick = false;
                }, 800);
            }
        });
    });

    // 5. Window Resize Event (re-align indicator bounds)
    let resizeTimeout;
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(() => {
            updateIndicator();
        }, 100);
    });

    // 6. Cookie Preferences Handler (privacy.html specific fallback)
    const cookiePrefLink = document.getElementById('openCookiePrefs');
    if (cookiePrefLink) {
        cookiePrefLink.addEventListener('click', (e) => {
            e.preventDefault();
            if (window.CookieConsent && typeof window.CookieConsent.openPreferences === 'function') {
                window.CookieConsent.openPreferences();
            }
        });
    }

    // Initialize state
    setTimeout(() => {
        handleScrollSpy();
        updateIndicator();
    }, 50);

    window.addEventListener('scroll', handleScrollSpy, { passive: true });
});
