/* global Chart, esistatusData */

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
    const normalized = h.length === 3 ? h.split('').map((c) => c + c).join('') : h;
    const bigint = parseInt(normalized, 16);
    const r = (bigint >> 16) & 255; // jshint ignore:line
    const g = (bigint >> 8) & 255; // jshint ignore:line
    const b = bigint & 255; // jshint ignore:line

    return `rgb(${r} ${g} ${b} / ${alpha})`;
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
            return `rgb(${nums[0]} ${nums[1]} ${nums[2]} / ${alpha})`;
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
    const parts = inner.split(',').map((p) => p.trim()).filter((p) => p.length > 0);

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

// Persistence helpers for per-dataset visibility (legend filters)
const _esiVisibilityStoragePrefix = 'esiStatusChartVisibility:';

// In-memory pending writes and timers to debounce localStorage writes and
// perform a read-merge-write at commit time to avoid overwriting concurrent
// writers.
const _esiPersistPending = Object.create(null);
const _esiPersistTimers = Object.create(null);
const _esiPersistDebounceMs = 120;

/**
 * Apply persisted visibility settings from localStorage to the given chart configuration.
 *
 * This function reads the persisted visibility settings for the specified chart ID from localStorage,
 * parses the JSON data, and applies the visibility settings to the datasets in the provided chart configuration.
 * It handles errors gracefully and logs any issues encountered during the process.
 *
 * @param {string} chartId - The unique identifier for the chart (used as a key in localStorage)
 * @param {object} chartConfig - The Chart.js configuration object containing datasets to which visibility settings will be applied
 * @private
 */
const _applyPersistedVisibility = (chartId, chartConfig) => {
    'use strict';

    try {
        const key = _esiVisibilityStoragePrefix + chartId;
        let json = null;

        try {
            json = window.localStorage.getItem(key);
        } catch (error) {
            json = null;

            console.error('ESI persist visibility read failed', chartId, error);
        }

        if (!json) {
            return;
        }

        let map = null;

        try {
            map = JSON.parse(json);
        } catch (error) {
            map = null;

            console.error('ESI persist visibility read: invalid json', chartId, json, error);
        }

        if (!map) {
            return;
        }

        ((chartConfig.data && chartConfig.data.datasets) || []).forEach((ds) => {
            if (!ds) {
                return;
            }

            // Determine the dataset key: prefer explicit id (added below), fall back to label
            let keyForDs = ds._esiId || ds.id || ds.label;

            if (typeof keyForDs === 'string' && Object.prototype.hasOwnProperty.call(map, keyForDs)) {
                ds.hidden = !!map[keyForDs];
            } else if (typeof ds.label === 'string' && Object.prototype.hasOwnProperty.call(map, ds.label)) {
                // backward compatibility: old keys may be stored by label
                ds.hidden = !!map[ds.label];
            }
        });
    } catch (error) {
        console.error('ESI persist visibility apply failed', chartId, error);
    }
};

/**
 * Commit any pending visibility changes for the specified chart ID to localStorage.
 *
 * This function reads the current persisted visibility settings from localStorage,
 * merges any pending changes for the specified chart ID, and writes the updated settings back to localStorage.
 * It handles errors gracefully and logs any issues encountered during the process.
 *
 * @param {string} chartId - The ID of the chart for which to commit pending visibility changes
 * @private
 */
const _commitPersistedWrites = (chartId) => {
    'use strict';

    try {
        const key = _esiVisibilityStoragePrefix + chartId;
        const pending = _esiPersistPending[chartId] || {};

        // Read current stored map, merge pending into it, write back
        let stored = {};

        try {
            const json = window.localStorage.getItem(key);

            if (json) {
                stored = JSON.parse(json) || {};
            }
        } catch (error) {
            console.error('ESI persist visibility read failed', chartId, error);

            stored = {};
        }

        // Merge pending entries into stored (overwrite per-key)
        Object.keys(pending).forEach((k) => {
            stored[k] = !!pending[k];
        });

        try {
            window.localStorage.setItem(key, JSON.stringify(stored));
        } catch (error) {
            console.error('ESI persist visibility write failed', chartId, error);
        }
    } catch (error) {
        console.error('ESI persist visibility commit failed', chartId, error);
    } finally {
        // clear pending and timer
        try {
            delete _esiPersistPending[chartId];
        } catch (error) {
            console.error('ESI persist visibility clear pending failed', chartId, error);
        }

        try {
            clearTimeout(_esiPersistTimers[chartId]);
        } catch (error) {
            console.error('ESI persist visibility clear timer failed', chartId, error);
        }

        try {
            delete _esiPersistTimers[chartId];
        } catch (error) {
            console.error('ESI persist visibility delete timer failed', chartId, error);
        }
    }
};

/**
 * Update the persisted visibility entry for a specific dataset in a chart.
 *
 * This function updates the in-memory pending visibility map for the specified chart ID and dataset key.
 * It debounces the commit to localStorage to avoid rapid conflicting writes when toggling dataset visibility.
 *
 * @param {string} chartId - The ID of the chart for which to update the visibility entry
 * @param {string} datasetKey - The unique key identifying the dataset (e.g., label or custom ID)
 * @param {boolean} hidden - The visibility state to persist (true for hidden, false for visible)
 * @private
 */
const _updatePersistedVisibilityEntry = (chartId, datasetKey, hidden) => {
    'use strict';

    try {
        if (!chartId || !datasetKey) {
            return;
        }

        // Ensure we have a pending map for this chart
        if (!_esiPersistPending[chartId]) {
            _esiPersistPending[chartId] = {};
        }

        _esiPersistPending[chartId][datasetKey] = !!hidden;

        // Debounce the commit so rapid toggles don't cause conflicting writes
        try {
            if (_esiPersistTimers[chartId]) {
                clearTimeout(_esiPersistTimers[chartId]);
            }

            _esiPersistTimers[chartId] = setTimeout(() => {
                _commitPersistedWrites(chartId);
            }, _esiPersistDebounceMs);
        } catch (error) {
            console.error('ESI persist visibility debounce failed', chartId, error);

            // Last-resort immediate commit
            _commitPersistedWrites(chartId);
        }
    } catch (error) {
        console.error('ESI persist visibility update failed', chartId, datasetKey, hidden, error);
    }
};

/**
 * Render the ESI Status History Chart using Chart.js
 *
 * This function initializes a line chart that displays the historical status of ESI services.
 * It uses the data provided in the `esistatusData` object, which should contain
 * labels and datasets for different status categories (OK, Degraded, Down, Recovering, Unknown).
 * The chart is rendered on a canvas element with the ID 'esi-status-chart-canvas'.
 *
 * @returns {void}
 */
const _renderStatusHistoryChartImpl = () => {
    'use strict';

    // Prevent concurrent re-entrancy: if a render is already in progress,
    // postpone this call slightly so we don't race destroying/creating the chart.
    if (window._esiStatusHistoryChartUpdating) {
        window._esiStatusHistoryChartNeedsUpdate = true;

        if (window._esiStatusHistoryChartUpdateTimer) {
            clearTimeout(window._esiStatusHistoryChartUpdateTimer);
        }

        window._esiStatusHistoryChartUpdateTimer = setTimeout(() => {
            window._esiStatusHistoryChartUpdating = false;
            window._esiStatusHistoryChartUpdateTimer = null;

            if (window._esiStatusHistoryChartNeedsUpdate) {
                window._esiStatusHistoryChartNeedsUpdate = false;

                try {
                    renderStatusHistoryChart();
                } catch (error) {
                    console.error('ESI chart: renderStatusHistoryChart failed', error);
                }
            }
        }, 120);

        return;
    }

    window._esiStatusHistoryChartUpdating = true;

    // Get the canvas element for the chart
    const ctx = document.getElementById('esi-status-chart-canvas');

    if (!ctx) {
        return;
    }

    // If an existing chart instance is present, persist its visibility and destroy it
    // immediately to avoid races where multiple renders create competing chart instances.
    try {
        const existingChart = window._esiStatusHistoryChart;

        if (existingChart) {
            try {
                if (typeof existingChart.destroy === 'function') {
                    existingChart.destroy();
                }
            } catch (error) {
                console.error('ESI chart: failed to destroy existing chart', error);
            }

            window._esiStatusHistoryChart = null;
        }
    } catch (error) {
        console.error('ESI chart: failed to destroy existing chart', error);
    }

    // Reverse the data arrays to display the most recent data on the right side of the chart
    // Use slice() to avoid mutating the source arrays when reversing
    const labels = (esistatusData.chartData.labels || []).slice().reverse();
    const okData = (esistatusData.chartData.okData || []).slice().reverse();
    const degradedData = (esistatusData.chartData.degradedData || []).slice().reverse();
    const downData = (esistatusData.chartData.downData || []).slice().reverse();
    const recoveringData = (esistatusData.chartData.recoveringData || []).slice().reverse();
    const unknownData = (esistatusData.chartData.unknownData || []).slice().reverse();

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

    // Chart identifier (use canvas id so multiple charts won't collide)
    const _chartId = (ctx && ctx.id) ? ctx.id : 'esi-status-chart-canvas';

    // Configuration object for Chart.js
    const chartConfig = {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    ...datasetDefaults,
                    _esiId: 'ok',
                    backgroundColor: _rgbAlpha(color.success, color.backgroundAlpha),
                    borderColor: color.success,
                    data: okData,
                    label: esistatusData.translations.ok
                },
                {
                    ...datasetDefaults,
                    _esiId: 'degraded',
                    backgroundColor: _rgbAlpha(color.warning, color.backgroundAlpha),
                    borderColor: color.warning,
                    data: degradedData,
                    label: esistatusData.translations.degraded
                },
                {
                    ...datasetDefaults,
                    _esiId: 'down',
                    backgroundColor: _rgbAlpha(color.danger, color.backgroundAlpha),
                    borderColor: color.danger,
                    data: downData,
                    label: esistatusData.translations.down
                },
                {
                    ...datasetDefaults,
                    _esiId: 'recovering',
                    backgroundColor: _rgbAlpha(color.info, color.backgroundAlpha),
                    borderColor: color.info,
                    data: recoveringData,
                    label: esistatusData.translations.recovering
                },
                {
                    ...datasetDefaults,
                    _esiId: 'unknown',
                    backgroundColor: _rgbAlpha(color.default, color.backgroundAlpha),
                    borderColor: color.default,
                    data: unknownData,
                    label: esistatusData.translations.unknown
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
                        display: false
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
                // custom legend handler will persist visibility changes
                legend: {
                    position: 'top'
                },
                decimation: {
                    enabled: true,
                    algorithm: 'lttb',
                    samples: decimationSamples
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

    // Attach a legend onClick wrapper that persists visibility changes
    try {
        const defaultLegendOnClick = (Chart && Chart.defaults && Chart.defaults.plugins && Chart.defaults.plugins.legend && Chart.defaults.plugins.legend.onClick) ? Chart.defaults.plugins.legend.onClick : null;

        chartConfig.options.plugins.legend.onClick = (evt, legendItem, legend) => {
            // Determine the element that was clicked (legend item)
            const element = evt.target;

            // Determine chart instance
            const chart = (legend && legend.chart) ? legend.chart : (element && element.chart) ? element.chart : window._esiStatusHistoryChart;

            try {
                if (defaultLegendOnClick) {
                    defaultLegendOnClick.call(chart, evt, legendItem, legend);
                } else {
                    const index = legendItem.datasetIndex;

                    if (typeof chart.isDatasetVisible === 'function' && typeof chart.setDatasetVisibility === 'function') {
                        chart.setDatasetVisibility(index, !chart.isDatasetVisible(index));
                    } else {
                        const meta = chart.getDatasetMeta(index);

                        meta.hidden = !meta.hidden;
                    }

                    chart.update();
                }
            } catch (error) {
                console.error('ESI chart: legend onClick default handler failed', error);
            }

            // Persist only the toggled dataset entry to avoid overwriting other entries
            try {
                let datasetKey = null;

                if (legendItem && typeof legendItem.datasetIndex !== 'undefined') {
                    let dsIndex = legendItem.datasetIndex;

                    try {
                        let ds = (chart && chart.data && chart.data.datasets && chart.data.datasets[dsIndex]) || null;

                        if (ds) {
                            datasetKey = ds._esiId || ds.id || ds.label || null;
                        }
                    } catch (error) {
                        console.error('ESI chart: failed to determine datasetKey', error);

                        datasetKey = null;
                    }
                }

                if (!datasetKey && legendItem && legendItem.text) {
                    datasetKey = legendItem.text;
                }

                if (datasetKey) {
                    try {
                        let meta = null;

                        try {
                            meta = chart.getDatasetMeta(legendItem.datasetIndex);
                        } catch (error) {
                            console.error('ESI chart: failed to get dataset meta', error);

                            meta = null;
                        }

                        let hiddenVal = null;

                        if (meta) {
                            hiddenVal = !!meta.hidden;
                        } else {
                            // fallback: check chart.isDatasetVisible if available
                            try {
                                hiddenVal = !(chart.isDatasetVisible && chart.isDatasetVisible(legendItem.datasetIndex));
                            } catch (error) {
                                console.error('ESI chart: failed to determine hidden state', error);

                                hiddenVal = false;
                            }
                        }

                        _updatePersistedVisibilityEntry(_chartId, datasetKey, hiddenVal);
                    } catch (error) {
                        console.error('ESI chart: failed to update persisted visibility entry', error);
                    }
                }
            } catch (error) {
                console.error('ESI chart: failed to process legend item', error);
            }
        };
    } catch (error) {
        console.error('ESI chart: failed to set up legend onClick handler', error);
    }

    // Apply any persisted visibility from previous sessions before creating/updating
    try {
        _applyPersistedVisibility(_chartId, chartConfig);
    } catch (error) {
        console.error('ESI chart: failed to apply persisted visibility', error);
    }

    // Create or update the Chart.js line chart
    // Preserve dataset visibility (legend toggles) across data reloads by
    // reusing an existing Chart instance when present and copying the
    // hidden state by dataset key.
    try {
        if (window._esiStatusHistoryChart && typeof window._esiStatusHistoryChart.update === 'function') {
            const oldChart = window._esiStatusHistoryChart;

            // Build a map of datasetKey -> hidden state from the existing chart
            const hiddenByKey = {};

            ((oldChart.data && oldChart.data.datasets) || []).forEach((ds, i) => {
                try {
                    const meta = oldChart.getDatasetMeta(i);
                    let keyForDs = (ds && (ds._esiId || ds.id || ds.label)) || null;

                    if (keyForDs) {
                        hiddenByKey[keyForDs] = !!meta.hidden;
                    }
                } catch (error) {
                    console.error('ESI chart: unable to get meta for dataset index', i, error);
                }
            });

            // Determine which canvas the existing chart is drawing to
            const oldCanvas = oldChart.canvas || (oldChart.ctx && oldChart.ctx.canvas) || null;

            if (oldCanvas === ctx) {
                // Canvas is the same element: update in-place
                ((chartConfig.data && chartConfig.data.datasets) || []).forEach((ds) => {
                    let keyForDs = ds && (ds._esiId || ds.id || ds.label);

                    if (keyForDs && Object.prototype.hasOwnProperty.call(hiddenByKey, keyForDs)) {
                        ds.hidden = hiddenByKey[keyForDs];
                    }
                });

                // Replace data and options on the existing chart and update
                oldChart.data = chartConfig.data;
                oldChart.options = chartConfig.options;
                oldChart.update();
            } else {
                // Canvas element was replaced in the DOM: destroy old chart and create a new one
                ((chartConfig.data && chartConfig.data.datasets) || []).forEach((ds) => {
                    let keyForDs = ds && (ds._esiId || ds.id || ds.label);

                    if (keyForDs && Object.prototype.hasOwnProperty.call(hiddenByKey, keyForDs)) {
                        ds.hidden = hiddenByKey[keyForDs];
                    }
                });

                try {
                    if (typeof oldChart.destroy === 'function') {
                        oldChart.destroy();
                    }
                } catch (error) {
                    console.error('ESI chart: failed to destroy old chart', error);
                }

                window._esiStatusHistoryChart = new Chart(ctx, chartConfig); // jshint ignore:line
            }
        } else {
            // Create a new chart and keep a reference so we can update it later
            window._esiStatusHistoryChart = new Chart(ctx, chartConfig); // jshint ignore:line
        }
    } catch (error) {
        console.error('ESI chart: create/update failed, attempting create-only fallback', error);
        // Fallback: try to create a new chart if something went wrong
        try {
            window._esiStatusHistoryChart = new Chart(ctx, chartConfig); // jshint ignore:line
        } catch (error) {
            console.error('Failed to create/update ESI status chart', error);
        }
    }

    // Mark update complete and process any pending update requests
    try {
        window._esiStatusHistoryChartUpdating = false;

        if (window._esiStatusHistoryChartNeedsUpdate) {
            window._esiStatusHistoryChartNeedsUpdate = false;
            console.debug('ESI chart: scheduling pending update');

            setTimeout(() => {
                try {
                    renderStatusHistoryChart();
                } catch (error) {
                    console.error('ESI chart: renderStatusHistoryChart failed', error);
                }
            }, 30);
        }
    } catch (error) {
        console.error('ESI chart: failed to finalize update state', error);
    }
};

// Debounced public wrapper so multiple callers can call quickly without
// creating destroy/create churn. Calls are coalesced into a single render.
const renderStatusHistoryChart = (() => {
    'use strict';

    let timer = null;
    const debounceMs = 80;

    return () => {
        try {
            if (timer) {
                clearTimeout(timer);
            }

            timer = setTimeout(() => {
                timer = null;

                try {
                    _renderStatusHistoryChartImpl();
                } catch (error) {
                    console.error('ESI chart: renderStatusHistoryChart failed', error);
                }
            }, debounceMs);
        } catch (error) {
            // fallback: immediate call
            console.debug('ESI chart: renderStatusHistoryChart failed to debounce, calling immediately', error);

            try {
                _renderStatusHistoryChartImpl();
            } catch (error) {
                console.error('ESI chart: renderStatusHistoryChart failed', error);
            }
        }
    };
})();
