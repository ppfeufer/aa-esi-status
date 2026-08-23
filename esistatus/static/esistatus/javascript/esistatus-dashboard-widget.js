/* global bootstrap, esistatusSettings, fetchGet, renderStatusHistoryChart */

$(document).ready(() => {
    'use strict';

    /**
     * ESI Status Dashboard Widget
     *
     * @type {{dashboardWidget: HTMLElement, tooltipElements: string, refreshInterval: null}}
     */
    const esistatus = {
        dashboardWidget: $('#esi-status-dashboard-panel'),
        tooltipElements: '[data-bs-tooltip="aa-esi-status"]',
        refreshInterval: null
    };

    /**
     * Update the ESI Status Dashboard Widget content
     *
     * @returns {Promise<void>}
     * @throws {Error} If the fetch request fails
     */
    const updateWidget = async () => {
        await fetchGet({
            url: esistatusSettings.dashboardWidget.ajaxUrl,
            responseIsJson: false
        }).then(response => {
            if (!response) {
                throw new Error('ESI Status Dashboard Widget: No response received from the server');
            }

            // console.log('ESI Status Dashboard Widget: Update successful', response);

            esistatus.dashboardWidget.html(response);

            if (!esistatus.dashboardWidget[0].classList.contains('show')) {
                new bootstrap.Collapse(esistatus.dashboardWidget[0], { // jshint ignore:line
                    show: true
                });
            }

            // Initialize Bootstrap tooltips
            $(esistatus.tooltipElements).each((_, el) => {
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
        }).catch(error => {
            console.error('ESI Status Dashboard Widget: Failed to update', error);
        });
    };

    /**
     * Start automatic refresh
     *
     * @returns {void}
     */
    const startRefresh = () => {
        console.log('ESI Status Dashboard Widget: Starting automatic refresh');

        updateWidget()
            .then(() => console.log('ESI Status Dashboard Widget: Initial update complete'))
            .catch(error => console.error('ESI Status Dashboard Widget: Initial update failed', error));

        esistatus.refreshInterval = setInterval(updateWidget, 30000);
    };

    /**
     * Stop automatic refresh
     *
     * @returns {void}
     */
    // const stopRefresh = () => {
    //     if (esistatus.refreshInterval) {
    //         console.log('ESI Status Dashboard Widget: Stopping automatic refresh');
    //
    //         clearInterval(esistatus.refreshInterval);
    //
    //         esistatus.refreshInterval = null;
    //     }
    // };

    // Event listeners for tab focus/blur
    // window.addEventListener('focus', startRefresh);
    // window.addEventListener('blur', stopRefresh);

    // Initialize
    startRefresh();
});
