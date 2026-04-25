// ==================== HOME PAGE MODULE ====================

document.addEventListener('DOMContentLoaded', () => {
    // Setup hero buttons
    const gotoYourpathBtn = document.querySelector('[data-action="goto-yourpath"]');
    const gotoCareersBtn = document.querySelector('[data-action="goto-careers"]');

    if (gotoYourpathBtn) {
        gotoYourpathBtn.addEventListener('click', () => {
            window.location.href = 'yourpath.html';
        });
    }

    if (gotoCareersBtn) {
        gotoCareersBtn.addEventListener('click', () => {
            window.location.href = 'careers.html';
        });
    }

    // "Follow the Mouse" effect for hero feature cards
    initFollowMouseEffect();
});

function initFollowMouseEffect() {
    const cards = document.querySelectorAll('.hero-feature-card');
    if (!cards.length) return;

    // Check if device supports hover (desktop)
    const isDesktop = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
    if (!isDesktop) return;

    document.addEventListener('mousemove', (e) => {
        cards.forEach(card => {
            const rect = card.getBoundingClientRect();
            // Calculate center of the card
            const cardCenterX = rect.left + rect.width / 2;
            const cardCenterY = rect.top + rect.height / 2;
            
            // Calculate distance from cursor to center
            const distX = e.clientX - cardCenterX;
            const distY = e.clientY - cardCenterY;
            
            // Translate the card slowly toward the mouse (divisor controls the amount)
            const moveX = distX / 25;
            const moveY = distY / 25;
            
            card.style.setProperty('--x', moveX);
            card.style.setProperty('--y', moveY);
        });
    });
}

