self.importScripts("https://cdn.jsdelivr.net/pyodide/v0.25.0/full/pyodide.js");

let pyodideReadyPromise = (async () => {
    self.postMessage({ type: "status", message: "Loading..." });
    self.pyodide = await loadPyodide();
    await pyodide.loadPackage("micropip");
    await pyodide.loadPackage("pyodide-http");
    const micropip = pyodide.pyimport("micropip");
    await micropip.install(['pandas', 'altair', 'vega_datasets']);
    const pythonCode = await fetch('main.py').then(res => res.text());
    await pyodide.runPythonAsync(pythonCode);
    self.postMessage({ type: "ready" });
})();

self.onmessage = async (event) => {

    try {
        console.log(pyodide.globals.has("generate_chart"));  // should log: true
        await pyodideReadyPromise;
        const generate_map = pyodide.globals.get("generate_chart");
        const result = generate_map();
        self.postMessage({ type: "result", data: result });
    } catch (err) {
        self.postMessage({ type: "error", message: err.message });
    }
};
