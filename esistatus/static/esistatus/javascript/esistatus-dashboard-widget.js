/* global bootstrap, esistatusSettings */

/**
 * This script refreshed the ESI status dashboard widget
 * regularly so to keep the user apprized about the current status of
 * ESI without having to reload the page.
 */

const elementEsiStatusDashboardWidget = document.getElementById('esi-status-dashboard-panel');

/**
 * Update the ESI status dashboard widget
 */
const esiStatusDashboardWidget = () => {
    'use strict';

    fetch(esistatusSettings.dashboardWidget.ajaxUrl)
        .then((response) => {
            return response.ok ? response.text() : Promise.reject(new Error('Something went wrong'));
        })
        .then((responseText) => {
            if (responseText === '') {
                return;
            }

            console.log('ESI Status Dashboard Widget: Updating widget content');

            elementEsiStatusDashboardWidget.innerHTML = responseText;

            if (!elementEsiStatusDashboardWidget.classList.contains('show')) {
                new bootstrap.Collapse(elementEsiStatusDashboardWidget, { // jshint ignore:line
                    show: true
                });
            }

            // Initialize Bootstrap tooltips
            [].slice.call(document.querySelectorAll(
                '[data-bs-tooltip="aa-esi-status"]'
            )).map((tooltipTriggerEl) => {
                return new bootstrap.Tooltip(tooltipTriggerEl, {html: true});
            });
        })
        .catch((error) => {
            console.error(error);
        });
};

let esiStatusDashboardWidgetInterval;

/**
 * Activate automatic refresh every x seconds
 */
const activateEsiStatusDashboardWidget = () => {
    'use strict';

    esiStatusDashboardWidget();

    console.log('ESI Status Dashboard Widget: Activating automatic refresh');

    esiStatusDashboardWidgetInterval = setInterval(
        esiStatusDashboardWidget, 60 * 1000
    );
};

/**
 * Deactivate automatic refresh
 */
const deactivateEsiStatusDashboardWidget = () => {
    'use strict';

    if (typeof esiStatusDashboardWidgetInterval !== 'undefined') {
        console.log('ESI Status Dashboard Widget: Deactivating automatic refresh');

        clearInterval(esiStatusDashboardWidgetInterval);
    }
};

/**
 * Refresh only on active browser tabs
 */
window.addEventListener('focus', () => {
    'use strict';

    activateEsiStatusDashboardWidget();
});

/**
 * Deactivate automatic refresh on inactive browser tabs
 */
window.addEventListener('blur', () => {
    'use strict';

    deactivateEsiStatusDashboardWidget();
});

/**
 * Initial start of refreshing on script loading
 */
activateEsiStatusDashboardWidget();
