document.addEventListener('DOMContentLoaded', () => {
    // 1. Intersection Observer for scroll-reveal animations
    const revealOptions = {
        threshold: 0.15,
        rootMargin: '0px 0px -50px 0px'
    };

    const revealObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('revealed');
                
                // If it's a stats item, trigger the count animation
                if (entry.target.classList.contains('about-stat-item')) {
                    animateStatCounter(entry.target);
                }
                
                observer.unobserve(entry.target); // Reveal only once
            }
        });
    }, revealOptions);

    // Observe feature cards, stats, and timeline items
    const elementsToReveal = document.querySelectorAll('.about-feature-card, .about-stat-item, .timeline-item');
    elementsToReveal.forEach(el => {
        revealObserver.observe(el);
    });

    // 2. Animate stat counter (0 -> target)
    function animateStatCounter(statItem) {
        const numberEl = statItem.querySelector('.stat-number-value');
        if (!numberEl) return;

        const target = parseInt(numberEl.getAttribute('data-target'), 10);
        if (isNaN(target)) return;

        const duration = 1500; // 1.5s animation duration
        const startTime = performance.now();

        function updateCounter(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // Easing function: easeOutQuad
            const easeProgress = progress * (2 - progress);
            const currentValue = Math.floor(easeProgress * target);

            // Format numbers nicely (e.g. 10,000 -> 10k or with commas)
            if (target >= 10000) {
                numberEl.textContent = (currentValue / 1000).toFixed(0);
            } else {
                numberEl.textContent = currentValue.toLocaleString();
            }

            if (progress < 1) {
                requestAnimationFrame(updateCounter);
            } else {
                if (target >= 10000) {
                    numberEl.textContent = (target / 1000).toFixed(0);
                } else {
                    numberEl.textContent = target.toLocaleString();
                }
            }
        }

        requestAnimationFrame(updateCounter);
    }

    // 3. Parallax scroll effect on Hero illustration/background circles
    const heroSection = document.querySelector('.about-hero');
    const illustration = document.querySelector('.about-illustration');
    const floatCards = document.querySelectorAll('.about-illustration-card');

    if (heroSection && (illustration || floatCards.length)) {
        window.addEventListener('scroll', () => {
            const scrollY = window.scrollY;
            const heroHeight = heroSection.offsetHeight;

            // Only run parallax when hero is in view
            if (scrollY <= heroHeight) {
                const speed = 0.05;
                if (illustration) {
                    illustration.style.transform = `translateY(${scrollY * speed}px)`;
                }
                
                floatCards.forEach((card, index) => {
                    const cardSpeed = 0.08 * (index + 1);
                    card.style.transform = `translateY(${scrollY * cardSpeed}px)`;
                });
            }
        });
    }
});
