/* global bootstrap, esistatusSettings */

$(document).ready(() => {
    'use strict';

    const elementEsiStatusIndex = $('.esi-status-index');
    const elementLoading = $('.esistatus-loading');

    fetch(esistatusSettings.url.esistatus)
        .then((response) => {
            return response.ok ? response.text() : Promise.reject(new Error('Something went wrong'));
        })
        .then((responseText) => {
            if (responseText === '') {
                return;
            }

            elementLoading.addClass('d-none');
            elementEsiStatusIndex.html(responseText);

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
});
