/* global bootstrap, esistatusSettings, fetchGet, renderStatusHistoryChart */

$(document).ready(() => {
    'use strict';

    const esistatus = {
        esiStatusIndex: $('.esi-status-index'),
        loading: $('.esistatus-loading'),
        tooltip: '[data-bs-tooltip="aa-esi-status"]',
    };

    /**
     * Fetch and display the ESI Status Index
     *
     * @return {Promise<void>}
     * @throws {Error} If the fetch request fails
     */
    const fetchEsiStatus = async () => {
        await fetchGet({
            url: esistatusSettings.url.esistatus,
            responseIsJson: false
        }).then(response => {
            if (!response) {
                throw new Error('ESI Status Dashboard Widget: No response received from the server');
            }

            esistatus.loading.addClass('d-none');
            esistatus.esiStatusIndex.html(response);

            // Initialize Bootstrap tooltips
            $(esistatus.tooltip).each((_, el) => {
                // new bootstrap.Tooltip(el, {html: true});

                // Dispose existing tooltip instance if it exists
                const existing = bootstrap.Tooltip.getInstance(el);

                if (existing) {
                    existing.dispose();
                }

                // Remove any leftover tooltip elements
                $('.bs-tooltip-auto').remove();

                // Create new tooltip instance
                return new bootstrap.Tooltip(el, {html: true});
            });

            // Render the status history chart
            renderStatusHistoryChart();
        });
    };

    fetchEsiStatus()
        .then(() => console.log('ESI Status page loaded successfully'))
        .catch(error => console.error('Failed to load ESI Status page', error));
});
