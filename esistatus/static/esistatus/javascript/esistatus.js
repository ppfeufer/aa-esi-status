/* global bootstrap, esistatusSettings, fetchGet */

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
        try {
            const data = await fetchGet({
                url: esistatusSettings.url.esistatus,
                responseIsJson: false
            });

            if (!data) {
                return;
            }

            esistatus.loading.addClass('d-none');
            esistatus.esiStatusIndex.html(data);

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
        } catch (error) {
            console.error(error);
        }
    };

    fetchEsiStatus();
});
