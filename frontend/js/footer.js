document.addEventListener('DOMContentLoaded', () => {
    const footerElement = document.querySelector('.footer');
    if (!footerElement) return;

    footerElement.innerHTML = `
        <div class="simple-footer-inner">
            <div class="simple-footer-links">
                <a href="about.html">About Us</a>
                <a href="privacy.html">Privacy Policy</a>
                <a href="terms.html">Terms & Conditions</a>
            </div>
            <p class="simple-footer-copy">&copy; 2026 Future Map. Your pathway to success</p>
            <p class="simple-footer-credit">Designed by Srajan And Team</p>
        </div>
    `;
});
