// ==================== HOME PAGE MODULE ====================
// Handles homepage-specific interactions and smooth scroll behavior

document.addEventListener('DOMContentLoaded', () => {
    // Smooth scroll for "See How It Works" anchor link
    const secondaryCta = document.getElementById('heroSecondary');
    if (secondaryCta) {
        secondaryCta.addEventListener('click', (e) => {
            e.preventDefault();
            const target = document.getElementById('how-it-works');
            if (target) {
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    }

    // Subtle scroll-triggered fade-in for sections
    initScrollReveal();
});

function initScrollReveal() {
    const sections = document.querySelectorAll(
        '.home-value, .home-steps, .home-features, .home-cta, .home-trust'
    );

    if (!sections.length) return;

    // Set initial state
    sections.forEach(section => {
        section.style.opacity = '0';
        section.style.transform = 'translateY(24px)';
        section.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    });

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -40px 0px'
    });

    sections.forEach(section => observer.observe(section));
}
