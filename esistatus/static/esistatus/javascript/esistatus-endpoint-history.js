/* global Chart, esistatusDashboardWidgetData */

(() => {
    'use strict';

    const ctx = document.getElementById('esiStatusChart');

    if (!ctx) {
        return;
    }

    console.log('esiStatusChart: ctx', ctx);

    // Flip data so the latest timestamp is on the right side of the chart.
    // The template emits entries in the same order as `esi_endpoint_history`.
    // Calling reverse() here ensures the most recent entry appears at the end (right).
    const labels = esistatusDashboardWidgetData.chartData.labels.reverse();
    const okData = esistatusDashboardWidgetData.chartData.okData.reverse();
    const degradedData = esistatusDashboardWidgetData.chartData.degradedData.reverse();
    const downData = esistatusDashboardWidgetData.chartData.downData.reverse();
    const recoveringData = esistatusDashboardWidgetData.chartData.recoveringData.reverse();
    const unknownData = esistatusDashboardWidgetData.chartData.unknownData.reverse();

    console.log('Labels:', labels);
    console.log('OK Data:', okData);
    console.log('Degraded Data:', degradedData);
    console.log('Down Data:', downData);
    console.log('Recovering Data:', recoveringData);
    console.log('Unknown Data:', unknownData);

    const elementBody = document.querySelector('body');
    const elementBodyCss = getComputedStyle(elementBody);

    Chart.defaults.color = elementBodyCss.color;

    /**
     * Convert a hex color code to an rgba(...) string with the specified alpha value.
     *
     * @param {string} hex - Hex color code (e.g., "#RRGGBB" or "#RGB")
     * @param {number} alpha - Alpha value (0 to 1)
     * @returns {string} - RGBA color string (e.g., "rgb(r g b / alpha)")
     */
    const hexToRgba = (hex, alpha) => {
        const h = hex.replace('#', '');
        const normalized = h.length === 3 ? h.split('').map(c => c + c).join('') : h;
        const bigint = parseInt(normalized, 16);
        const r = (bigint >> 16) & 255; // jshint ignore:line
        const g = (bigint >> 8) & 255; // jshint ignore:line
        const b = bigint & 255; // jshint ignore:line

        return 'rgb(' + r + ' ' + g + ' ' + b + ' / ' + alpha + ')';
    };

    /**
     * Convert a hex, rgb(...) or rgba(...) CSS value to an rgba(...) string with the specified alpha value.
     *
     * @param {string} cssColor - CSS color value (hex, rgb(...), or rgba(...))
     * @param {number} alpha - Alpha value (0 to 1)
     * @returns {string|null} - RGBA color string (e.g., "rgb(r g b / alpha)") or null if input is invalid
     */
    const rgbAlpha = (cssColor, alpha) => {
        if (!cssColor) {
            return null;
        }

        cssColor = cssColor.trim();

        if (cssColor.startsWith('rgb')) {
            const nums = cssColor.match(/\d+/g);

            if (nums && nums.length >= 3) {
                return 'rgb(' + nums[0] + ' ' + nums[1] + ' ' + nums[2] + ' / ' + alpha + ')';
            }
        }

        if (cssColor.startsWith('#')) {
            return hexToRgba(cssColor, alpha);
        }

        // unknown format: return as-is (alpha ignored)
        return cssColor;
    };

    /**
     * Get computed background color for a list of possible classes, return first non-transparent
     *
     * @param {string[]} classList - Array of class names to check
     * @returns {string|null} - Computed background color or null if none found
     */
    const getBgColorFromClasses = (classList) => {
        for (let i = 0; i < classList.length; i++) {
            const cls = classList[i];
            const el = document.createElement('div');

            el.style.position = 'absolute';
            el.style.left = '-9999px';
            el.className = cls;

            document.body.appendChild(el);

            const comp = getComputedStyle(el).backgroundColor || getComputedStyle(el).color || '';

            document.body.removeChild(el);

            if (comp && comp !== 'rgba(0, 0, 0, 0)' && comp !== 'transparent') {
                return comp;
            }
        }

        return null;
    };

    // Resolve colors using the Bootstrap utility classes.
    const colorBsSuccess = getBgColorFromClasses(['text-bg-success','bg-success']);
    const colorBsWarning = getBgColorFromClasses(['text-bg-warning','bg-warning']);
    const colorBsDanger = getBgColorFromClasses(['text-bg-danger','bg-danger']);
    const colorBsInfo = getBgColorFromClasses(['text-bg-info','bg-info']);
    const colorBsDefault = getBgColorFromClasses(['text-bg-default','bg-secondary']);

    // Responsive chart with multiple datasets (line chart with filled areas)
    new Chart(ctx.getContext('2d'), { // jshint ignore:line
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: esistatusDashboardWidgetData.translations.ok,
                    data: okData,
                    borderColor: colorBsSuccess,
                    backgroundColor: rgbAlpha(colorBsSuccess, 0.25),
                    tension: 0.25,
                    fill: true,
                    pointRadius: 2,
                },
                {
                    label: esistatusDashboardWidgetData.translations.degraded,
                    data: degradedData,
                    borderColor: colorBsWarning,
                    backgroundColor: rgbAlpha(colorBsWarning, 0.25),
                    tension: 0.25,
                    fill: true,
                    pointRadius: 2,
                },
                {
                    label: esistatusDashboardWidgetData.translations.down,
                    data: downData,
                    borderColor: colorBsDanger,
                    backgroundColor: rgbAlpha(colorBsDanger, 0.25),
                    tension: 0.25,
                    fill: true,
                    pointRadius: 2,
                },
                {
                    label: esistatusDashboardWidgetData.translations.recovering,
                    data: recoveringData,
                    borderColor: colorBsInfo,
                    backgroundColor: rgbAlpha(colorBsInfo, 0.25),
                    tension: 0.25,
                    fill: true,
                    pointRadius: 2,
                },
                {
                    label: esistatusDashboardWidgetData.translations.unknown,
                    data: unknownData,
                    borderColor: colorBsDefault,
                    backgroundColor: rgbAlpha(colorBsDefault, 0.25),
                    tension: 0.25,
                    fill: true,
                    pointRadius: 2,
                }
            ]
        },
        options: {
            // disable animations/transitions so chart appears instantly
            animation: false,
            transitions: {
                // disable show/hide/resize animations
                show: { animation: false },
                hide: { animation: false },
                resize: { animation: false }
            },
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    // hide the x-axis tick labels (dates) to reduce clutter
                    display: true,
                    ticks: {
                        display: false,
                        maxRotation: 45,
                        minRotation: 0
                    }
                },
                y: {
                    beginAtZero: true,
                    precision: 0
                }
            },
            plugins: {
                legend: { position: 'top' },
                tooltip: { mode: 'index', intersect: false }
            },
            interaction: { mode: 'index', intersect: false }
        }
    });
})();
