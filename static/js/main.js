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
