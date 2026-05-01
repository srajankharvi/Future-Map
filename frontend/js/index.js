// ==================== HOME PAGE MODULE ====================
// Handles demo score animation, smooth scroll, and scroll reveal

document.addEventListener('DOMContentLoaded', () => {
    // Smooth scroll for "See a Live Demo" anchor
    const secondaryCta = document.getElementById('heroSecondary');
    if (secondaryCta) {
        secondaryCta.addEventListener('click', (e) => {
            e.preventDefault();
            const target = document.getElementById('demo');
            if (target) {
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    }

    // Animate the demo score ring when it scrolls into view
    initDemoScoreAnimation();

    // Subtle scroll-triggered fade-in for sections
    initScrollReveal();
});

function initDemoScoreAnimation() {
    const scoreRing = document.getElementById('demoScoreRing');
    if (!scoreRing) return;

    const scoreFill = scoreRing.querySelector('.home-demo__score-fill');
    const scoreNum = document.getElementById('demoScoreNum');
    if (!scoreFill || !scoreNum) return;

    // Start with zero
    scoreFill.style.strokeDasharray = '0, 100';
    scoreNum.textContent = '0';

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                // Animate the ring fill to 70% (7/10)
                setTimeout(() => {
                    scoreFill.style.strokeDasharray = '70, 100';
                }, 300);

                // Animate the number counting up
                let current = 0;
                const target = 7;
                const interval = setInterval(() => {
                    current++;
                    scoreNum.textContent = current;
                    if (current >= target) clearInterval(interval);
                }, 120);

                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.3 });

    observer.observe(scoreRing);
}

function initScrollReveal() {
    const sections = document.querySelectorAll(
        '.home-problem, .home-demo, .home-value, .home-steps, .home-features, .home-cta, .home-trust'
    );

    if (!sections.length) return;

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
        threshold: 0.08,
        rootMargin: '0px 0px -40px 0px'
    });

    sections.forEach(section => observer.observe(section));
}
