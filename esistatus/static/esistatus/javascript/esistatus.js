/* global bootstrap, esistatusSettings, fetchGet */

$(document).ready(() => {
    'use strict';

    /**
     * Fetch and display the ESI Status Index
     *
     * @return {Promise<void>}
     * @throws {Error} If the fetch request fails
     */
    const fetchEsiStatus = async () => {
        const elementEsiStatusIndex = $('.esi-status-index');
        const elementLoading = $('.esistatus-loading');

        try {
            const data = await fetchGet({
                url: esistatusSettings.url.esistatus,
                responseIsJson: false
            });

            if (!data) {
                return;
            }

            elementLoading.addClass('d-none');
            elementEsiStatusIndex.html(data);

            // Initialize Bootstrap tooltips
            $('[data-bs-tooltip="aa-esi-status"]').each((_, el) => new bootstrap.Tooltip(el, {html: true}));
        } catch (error) {
            console.error(error);
        }
    };

    fetchEsiStatus();
});
