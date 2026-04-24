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
});
