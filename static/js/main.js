document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchInput');
    const searchForm = document.getElementById('searchForm');
    
    // ফর্মটি পেজে থাকলে তবেই কোড কাজ করবে
    if (searchInput && searchForm) {
        let typingTimer;

        // পেজ রিলোড হওয়ার পর ইনপুট বক্সে কার্সার ফিরিয়ে আনা ও লেখার শেষে রাখা
        if (searchInput.value) {
            searchInput.focus();
            searchInput.setSelectionRange(searchInput.value.length, searchInput.value.length);
        }

        // টাইপ করার সময় ফর্ম সাবমিট করার লজিক
        searchInput.addEventListener('input', function() {
            clearTimeout(typingTimer);
            typingTimer = setTimeout(function() {
                searchForm.submit();
            }, 500); 
        });
    }
});





document.addEventListener("DOMContentLoaded", function () {
const sliders = document.querySelectorAll(".emox-auto-slider");

sliders.forEach((slider) => {
    const slides = slider.querySelectorAll(".emox-slide");
    const dotsContainer = slider.querySelector(".emox-dots");

    if (slides.length <= 1) return;

    let currentIndex = 0;
    const intervalTime = parseInt(slider.getAttribute("data-interval")) || 4000;
    let slideTimer;

    // স্লাইড সংখ্যা অনুযায়ী ডট তৈরি করা
    slides.forEach((_, index) => {
    const dot = document.createElement("button");
    dot.type = "button";
    dot.classList.add("emox-dot");
    dot.setAttribute("aria-label", `Slide ${index + 1}`);
    if (index === 0) dot.classList.add("active");

    dot.addEventListener("click", (e) => {
        e.preventDefault();
        e.stopPropagation();
        goToSlide(index);
        resetTimer();
    });

    dotsContainer.appendChild(dot);
    });

    const dots = dotsContainer.querySelectorAll(".emox-dot");

    function goToSlide(index) {
    slides[currentIndex].classList.remove("active");
    dots[currentIndex].classList.remove("active");

    currentIndex = index;

    slides[currentIndex].classList.add("active");
    dots[currentIndex].classList.add("active");
    }

    function nextSlide() {
    const nextIndex = (currentIndex + 1) % slides.length;
    goToSlide(nextIndex);
    }

    function resetTimer() {
    clearInterval(slideTimer);
    slideTimer = setInterval(nextSlide, intervalTime);
    }

    slideTimer = setInterval(nextSlide, intervalTime);
});
});