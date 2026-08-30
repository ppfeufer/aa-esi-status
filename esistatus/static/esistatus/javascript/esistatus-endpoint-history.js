/* global Chart, esistatusDashboardWidgetData */

/**
 * Convert a hex color code to an rgba(...) string with the specified alpha value.
 *
 * @param {string} hex - Hex color code (e.g., "#RRGGBB" or "#RGB")
 * @param {float|string} alpha - Alpha value (0 to 1 as factor or percentage string)
 * @returns {string} - RGBA color string (e.g., "rgb(r g b / alpha)")
 * @private
 */
const _hexToRgba = (hex, alpha) => {
    'use strict';

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
 * @param {float|string} alpha - Alpha value (0 to 1 as factor or percentage string)
 * @returns {string|null} - RGBA color string (e.g., "rgb(r g b / alpha)") or null if input is invalid
 * @private
 */
const _rgbAlpha = (cssColor, alpha) => {
    'use strict';

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
        return _hexToRgba(cssColor, alpha);
    }

    // Unknown format: return as-is (alpha ignored)
    return cssColor;
};

/**
 * Check if a given CSS color string represents a fully transparent color.
 *
 * Handles various formats including:
 *  - "transparent"
 *  - "rgba(0, 0, 0, 0)"
 *  - "rgba(0 0 0 / 0)"
 *  - "rgb(0 0 0 / 0%)"
 *  - "rgba(255,255,255,0)"
 *
 * @param {string} cssColor - CSS color string to check
 * @returns {boolean} - True if the color is fully transparent, false otherwise
 * @private
 */
const _isTransparentColor = (cssColor) => {
    'use strict';

    if (!cssColor) {
        return true;
    }

    cssColor = cssColor.trim().toLowerCase();

    if (cssColor === 'transparent') {
        return true;
    }

    // Match rgb/rgba forms
    const fnMatch = cssColor.match(/^(rgba?|hsla?)\((.*)\)$/);

    if (!fnMatch) {
        return false;
    }

    const inner = fnMatch[2].trim();

    // If the function uses the slash syntax: "r g b / a" or "h s l / a"
    if (inner.indexOf('/') !== -1) {
        const parts = inner.split('/');
        const alphaStr = parts[1].replace(/\)/g, '').trim();

        if (!alphaStr) {
            return false;
        }

        // Percent value
        if (alphaStr.endsWith('%')) {
            const p = parseFloat(alphaStr.slice(0, -1));

            return !Number.isNaN(p) && p === 0;
        }

        const a = parseFloat(alphaStr);

        return !Number.isNaN(a) && a === 0;
    }

    // Otherwise, comma or space separated. Try comma-separated rgba(r,g,b,a)
    const parts = inner.split(',').map(p => p.trim()).filter(p => p.length > 0);

    if (parts.length === 4) {
        const alphaStr = parts[3].replace(/\)/g, '').trim();

        if (alphaStr.endsWith('%')) {
            const p = parseFloat(alphaStr.slice(0, -1));

            return !Number.isNaN(p) && p === 0;
        }

        const a = parseFloat(alphaStr);

        return !Number.isNaN(a) && a === 0;
    }

    // No alpha channel present -> not transparent
    return false;
};

/**
 * Get computed background color for a list of possible classes, return first non-transparent.
 *
 * This function creates a temporary div element for each class in the provided list,
 * applies the class to the element, and retrieves the computed background color.
 * It returns the first non-transparent background color found, or null if none are found.
 *
 * @param {string[]} classList - Array of class names to check
 * @returns {string|null} - Computed background color or null if none found
 * @private
 */
const _getBgColorFromClasses = (classList) => {
    'use strict';

    for (let i = 0; i < classList.length; i++) {
        const cls = classList[i];
        const el = document.createElement('div');

        el.style.position = 'absolute';
        el.style.left = '-9999px';
        el.className = cls;

        document.body.appendChild(el);

        const comp = getComputedStyle(el).backgroundColor || getComputedStyle(el).color || '';

        document.body.removeChild(el);

        if (comp && !_isTransparentColor(comp)) {
            return comp;
        }
    }

    return null;
};

/**
 * Render the ESI Status History Chart using Chart.js
 *
 * This function initializes a line chart that displays the historical status of ESI services.
 * It uses the data provided in the `esistatusDashboardWidgetData` object, which should contain
 * labels and datasets for different status categories (OK, Degraded, Down, Recovering, Unknown).
 * The chart is rendered on a canvas element with the ID 'esi-status-chart-canvas'.
 *
 * @returns {void}
 */
const renderStatusHistoryChart = () => { // eslint-disable-line no-unused-vars
    'use strict';

    // Get the canvas element for the chart
    const ctx = document.getElementById('esi-status-chart-canvas');

    if (!ctx) {
        return;
    }

    // Reverse the data arrays to display the most recent data on the right side of the chart
    const labels = esistatusDashboardWidgetData.chartData.labels.reverse();
    const okData = esistatusDashboardWidgetData.chartData.okData.reverse();
    const degradedData = esistatusDashboardWidgetData.chartData.degradedData.reverse();
    const downData = esistatusDashboardWidgetData.chartData.downData.reverse();
    const recoveringData = esistatusDashboardWidgetData.chartData.recoveringData.reverse();
    const unknownData = esistatusDashboardWidgetData.chartData.unknownData.reverse();

    // Set the default font color for Chart.js to match the computed color of the body element
    Chart.defaults.color = getComputedStyle(document.querySelector('body')).color;

    // Resolve colors using the Bootstrap utility classes.
    const color = {
        backgroundAlpha: '25%',
        danger: _getBgColorFromClasses(['text-bg-danger', 'bg-danger']),
        default: _getBgColorFromClasses(['text-bg-default', 'bg-secondary']),
        info: _getBgColorFromClasses(['text-bg-info', 'bg-info']),
        success: _getBgColorFromClasses(['text-bg-success', 'bg-success']),
        warning: _getBgColorFromClasses(['text-bg-warning', 'bg-warning'])
    };

    // Common dataset options for all datasets
    const datasetDefaults = {
        borderWidth: 0.6,
        cubicInterpolationMode: 'monotone',
        fill: {
            target: 'origin'
        },
        normalized: true,
        pointRadius: 0,
        spanGaps: false,
        tension: 0.2
    };

    // Determine the number of samples for decimation based on the canvas width and device pixel ratio
    const minSamples = 200;
    const decimationSamples = Math.max(minSamples, Math.round((ctx.clientWidth || 800) * (window.devicePixelRatio || 1)));

    // Configuration object for Chart.js
    const chartConfig = {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    ...datasetDefaults,
                    backgroundColor: _rgbAlpha(color.success, color.backgroundAlpha),
                    borderColor: color.success,
                    data: okData,
                    label: esistatusDashboardWidgetData.translations.ok
                },
                {
                    ...datasetDefaults,
                    backgroundColor: _rgbAlpha(color.warning, color.backgroundAlpha),
                    borderColor: color.warning,
                    data: degradedData,
                    label: esistatusDashboardWidgetData.translations.degraded
                },
                {
                    ...datasetDefaults,
                    backgroundColor: _rgbAlpha(color.danger, color.backgroundAlpha),
                    borderColor: color.danger,
                    data: downData,
                    label: esistatusDashboardWidgetData.translations.down
                },
                {
                    ...datasetDefaults,
                    backgroundColor: _rgbAlpha(color.info, color.backgroundAlpha),
                    borderColor: color.info,
                    data: recoveringData,
                    label: esistatusDashboardWidgetData.translations.recovering
                },
                {
                    ...datasetDefaults,
                    backgroundColor: _rgbAlpha(color.default, color.backgroundAlpha),
                    borderColor: color.default,
                    data: unknownData,
                    label: esistatusDashboardWidgetData.translations.unknown
                }
            ]
        },
        options: {
            // disable animations/transitions so chart appears instantly
            animation: false,
            // transitions: {
            //     // disable show/hide/resize animations
            //     show: {
            //         animation: false
            //     },
            //     hide: {
            //         animation: false
            //     },
            //     resize: {
            //         animation: false
            //     }
            // },
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    // hide the x-axis tick labels (dates) to reduce clutter
                    display: true,
                    ticks: {
                        display: false,
                        // maxRotation: 45,
                        // minRotation: 0
                    }
                },
                y: {
                    beginAtZero: true,
                    precision: 0
                }
            },
            plugins: {
                decimation: {
                    enabled: true,
                    algorithm: 'lttb',
                    samples: decimationSamples
                },
                legend: {
                    position: 'top'
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    position: 'nearest'
                }
            },
            interaction: {
                mode: 'index',
                intersect: false
            }
        }
    };

    // Create the Chart.js line chart
    new Chart(ctx, chartConfig); // jshint ignore:line
};
