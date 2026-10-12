let ready;
async function prepare(id) {
  self.postMessage({id, progress: '首次使用需加载分析引擎，请稍候…'});
  importScripts('./runtime/pyodide.js');
  const py = await loadPyodide({indexURL: './runtime/', stdout: () => {}, stderr: () => {}});
  self.postMessage({id, progress: '正在准备图像分析组件…'});
  await py.loadPackage(['numpy', 'opencv-python']);
  const response = await fetch('./engine.py');
  if (!response.ok) throw new Error('分析引擎加载失败，请刷新页面后重试。');
  await py.runPythonAsync(await response.text());
  return py;
}
self.onmessage = async ({data}) => {
  const {id, bytes} = data;
  try {
    if (!ready) ready = prepare(id).catch(error => {ready = undefined; throw error;});
    const py = await ready;
    self.postMessage({id, progress: '正在分析构图、透视和曝光…'});
    py.FS.writeFile('/frame.png', new Uint8Array(bytes));
    try {
      const result = JSON.parse(await py.runPythonAsync('analyze_upload("/frame.png")'));
      self.postMessage({id, result});
    } finally {py.FS.unlink('/frame.png');}
  } catch (error) {
    self.postMessage({id, error: '分析未完成：' + error.message});
  }
};
