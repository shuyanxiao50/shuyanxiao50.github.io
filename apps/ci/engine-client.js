(() => {
  let worker, pending, serial = 0, canceled = false;
  function stop(reason) {
    if (worker) worker.terminate();
    worker = undefined;
    if (pending) {clearTimeout(pending.timer); pending.reject(new Error(reason)); pending = undefined;}
  }
  window.CIEngine = {
    cancel() {canceled = true; stop('已取消分析，可以重新选择照片。');},
    async analyze(file, progress) {
      canceled = false;
      if (file.size > 16 * 1024 * 1024) throw new Error('请选择不超过 16 MB 的图片。');
      if (!file.type.startsWith('image/')) throw new Error('请选择图片文件。');
      progress('正在读取照片…');
      let image;
      try {image = await createImageBitmap(file);} catch {
        if (file.type !== 'image/svg+xml') throw new Error('无法读取图片，请选择 JPG、PNG、WebP 或 BMP 图片。');
        const url = URL.createObjectURL(file);
        image = await new Promise((resolve, reject) => {
          const element = new Image();
          element.onload = () => {element.close = () => URL.revokeObjectURL(url); resolve(element);};
          element.onerror = () => {URL.revokeObjectURL(url); reject(new Error('示例图加载失败。'));};
          element.src = url;
        });
      }
      if (canceled) {image.close(); throw new Error('已取消分析。');}
      if (image.width * image.height > 40000000) {image.close(); throw new Error('图片像素过大，请缩小至 4000 万像素以内。');}
      const scale = Math.min(1800 / image.width, 1400 / image.height, 1);
      const canvas = document.createElement('canvas');
      canvas.width = Math.max(1, Math.floor(image.width * scale));
      canvas.height = Math.max(1, Math.floor(image.height * scale));
      const context = canvas.getContext('2d', {alpha: false});
      context.fillStyle = '#fff'; context.fillRect(0, 0, canvas.width, canvas.height);
      context.drawImage(image, 0, 0, canvas.width, canvas.height); image.close();
      const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/png'));
      canvas.width = canvas.height = 1;
      if (!blob) throw new Error('图片转换失败，请尝试其他图片。');
      const bytes = await blob.arrayBuffer();
      if (canceled) throw new Error('已取消分析。');
      if (!worker) {
        worker = new Worker('./engine-worker.js');
        worker.onerror = () => stop('分析引擎未能启动，请检查网络并刷新页面重试。');
        worker.onmessage = ({data}) => {
          if (!pending || data.id !== pending.id) return;
          if (data.progress) {pending.progress(data.progress); return;}
          clearTimeout(pending.timer);
          const current = pending; pending = undefined;
          if (data.error) current.reject(new Error(data.error)); else current.resolve(data.result);
        };
      }
      return new Promise((resolve, reject) => {
        const id = ++serial;
        pending = {id, resolve, reject, progress, timer: setTimeout(() => stop('加载或分析耗时较长，请检查网络后重试。'), 240000)};
        worker.postMessage({id, bytes}, [bytes]);
      });
    }
  };
})();
