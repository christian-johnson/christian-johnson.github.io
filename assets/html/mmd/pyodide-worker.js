self.importScripts("https://cdn.jsdelivr.net/pyodide/v0.25.0/full/pyodide.js");

let pyodideReadyPromise = (async () => {
    self.postMessage({ type: "status", message: "Loading Python environment..." });
    self.pyodide = await loadPyodide();
    await pyodide.loadPackage("micropip");
    const micropip = pyodide.pyimport("micropip");
    await micropip.install(['numpy', 'pandas', 'altair', 'vega_datasets', 'networkx', 'geopandas']);
    const pythonCode = await fetch('main.py').then(res => res.text());
    await pyodide.runPythonAsync(pythonCode);
    self.postMessage({ type: "ready" });
})();

self.onmessage = async (event) => {
    const { state, minReps, totalReps, nDistricts, tolerance } = event.data;

    try {
        await pyodideReadyPromise;
        const generate_choropleth = pyodide.globals.get("generate_choropleth");
        const result = generate_choropleth(state, minReps, totalReps, nDistricts, tolerance);
        self.postMessage({ type: "result", data: result });
    } catch (err) {
        self.postMessage({ type: "error", message: err.message });
    }
};
