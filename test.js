
        let selectedLat = 13.2619;
        let selectedLng = 80.0277;

        // GLOBAL VANILLA JS ERROR BOUNDARY
        window.onerror = function (message, source, lineno, colno, error) {
            console.error("Global Error Caught:", message, error);
            const panel = document.getElementById('panel');
            if (panel) {
                panel.classList.add('open');
                document.getElementById('p-region-name').textContent = "Application Error";
                document.getElementById('p-error').innerHTML = `Something went wrong loading this view.<br><button onclick="window.location.reload()" style="margin-top:12px; padding:6px 12px; background:var(--stress-500); color:white; font-family:var(--mono); border:none; border-radius:4px; cursor:pointer;">RETRY</button>`;
                const badge = document.getElementById('p-badge');
                if (badge) badge.style.display = 'none';
            }
            return true; // Suppress raw stack traces from reaching user console
        };
        window.addEventListener('unhandledrejection', function (event) {
            console.error("Unhandled Promise Rejection:", event.reason);
            const errDiv = document.getElementById('p-error');
            if (errDiv) errDiv.innerHTML = `Data request failed — please check connection.<br><button onclick="window.location.reload()" style="margin-top:12px; padding:6px 12px; background:var(--stress-500); color:white; font-family:var(--mono); border:none; border-radius:4px; cursor:pointer;">RETRY</button>`;
        });
    