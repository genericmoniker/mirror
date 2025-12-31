// Auto-hide cursor after 5 seconds of inactivity
(function() {
    let timeout;
    const HIDE_DELAY = 5000; // 5 seconds

    function hideCursor() {
        document.body.classList.add('hide-cursor');
    }

    function showCursor() {
        document.body.classList.remove('hide-cursor');
    }

    function resetTimer() {
        showCursor();
        clearTimeout(timeout);
        timeout = setTimeout(hideCursor, HIDE_DELAY);
    }

    // Initialize on page load
    document.addEventListener('DOMContentLoaded', function() {
        // Start the timer
        timeout = setTimeout(hideCursor, HIDE_DELAY);

        // Reset timer on mouse movement
        document.addEventListener('mousemove', resetTimer);
    });
})();
