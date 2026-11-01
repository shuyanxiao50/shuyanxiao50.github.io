(() => {
  'use strict';
  const $ = (id) => document.getElementById(id);
  const menu = document.querySelector('.menu-toggle');
  const nav = $('navLinks');
  function setMenu(open) {
    nav.classList.toggle('is-open', open);
    menu.setAttribute('aria-expanded', String(open));
    menu.setAttribute('aria-label', open ? '收起导航' : '展开导航');
  }
  menu.addEventListener('click', () => setMenu(!nav.classList.contains('is-open')));
  nav.querySelectorAll('a').forEach((link) => link.addEventListener('click', () => setMenu(false)));
  document.addEventListener('keydown', (event) => { if (event.key === 'Escape') setMenu(false); });

  const scenes = {
    done: {
      type: 'REPLY READY → VOICE INPUT', title: '回答到达，下一句交给你。',
      context: '你暂时把视线从编辑器移开，模型完成了这一轮回复。',
      speaker: '电脑 / 模型', event: '本轮回答已生成，等待下一步需求。',
      creature: '模型答好了，接着做什么？', user: 'OK，接下来生成一份静态展示网页。',
      outcome: '把这一轮口述转成需求，送回当前编码会话，等待真实回执。',
      condition: '接入条件：真实模型事件、语音转写与会话回传接口。',
      steps: ['事件到达 · 编码工具产生可信的本轮完成事件', '小桶提醒 · 用声音与灯光告知回答已到达', '口述回应 · 唤醒后说出下一步需求', '回到会话 · 转写并送回指定会话，确认真实回执']
    },
    question: {
      type: 'QUESTION PENDING → SPOKEN ANSWER', title: '模型有问题，小桶帮你传话。',
      context: '模型需要补充信息才能继续。小桶把问题说清楚，留给你决定。',
      speaker: '电脑 / 模型', event: '展示网页主要给现场观众看，还是给技术评委看？',
      creature: '模型想确认：这份网页主要面向谁？', user: '给现场观众看，先讲清楚使用场景和产品外观。',
      outcome: '把你的补充与原问题关联，送回同一个任务，再等待模型继续。',
      condition: '接入条件：可读取的问题内容、有效会话标识及补充信息回传。',
      steps: ['问题到达 · 识别真实的待补充问题', '小桶转述 · 说清问题，保留必要上下文', '口述补充 · 用户给出具体信息', '继续任务 · 将回答关联到原问题与原会话']
    },
    approval: {
      type: 'SCOPED REQUEST → YOUR DECISION', title: '这一次，先听清，再决定。',
      context: '编码工具发来一条具体权限请求。确认对象与范围后，再做本次决定。',
      speaker: '电脑 / 工具', event: '请求：在当前项目目录创建静态网页文件，等待本次授权。',
      creature: '当前任务想在项目目录创建网页文件。这一次允许吗？', user: '允许这一次。',
      outcome: '仅在原工具支持、请求仍有效且范围匹配时传回本次决定；以原工具回执为准。',
      condition: '接入条件：原生授权路径、具体请求标识、明确范围和有效期；不自动放行全部请求。',
      steps: ['请求到达 · 取得本次操作、目录范围和有效请求', '解释请求 · 小桶说清楚要做什么', '明确决定 · 用户选择本次允许、拒绝或稍后', '原路回传 · 走工具支持的授权路径并读取回执']
    },
    error: {
      type: 'TASK INTERRUPTED → INFORMED RECOVERY', title: '任务没接上，也要说清楚。',
      context: '当工具报告网络异常或生成中断，小桶及时提示当前状态。',
      speaker: '电脑 / 工具', event: '网络连接中断，本轮任务未收到完成回执。',
      creature: '这轮任务中断了，还没有确认完成。要先检查网络吗？', user: '先检查网络，恢复后再重试这一步。',
      outcome: '说明失败或未知状态，保留原任务上下文；网络恢复不等于任务已经成功。',
      condition: '接入条件：工具真实异常事件、任务状态查询与受控重试；不把沉默误报成断网。',
      steps: ['异常到达 · 以工具真实错误和状态为依据', '告知状态 · 说明中断、失败或结果未知', '选择下一步 · 用户决定检查、重试或稍后', '核对结果 · 重试后再读取真实完成或失败回执']
    },
    posture: {
      type: 'STATIONARY OBSERVATION → GENTLE NUDGE', title: '专注的时候，也照顾一下坐姿。',
      context: '小桶停稳后观察姿态。设备移动、视线遮挡或结果未知时，暂停判断。',
      speaker: '设备 / 视觉', event: '静止状态下，姿态结果持续偏离设定范围。',
      creature: '坐了有一会儿了，调整一下姿势，放松肩膀吧。', user: '好，我调整一下。',
      outcome: '给出温和的姿态提醒；设备移动时暂停，恢复静止后再判断。',
      condition: '接入条件：真实 SPI 图像、静止状态与姿态结果；不从低头推断注意力或手机使用。',
      steps: ['确认静止 · 设备停稳且画面可用', '观察姿态 · 使用真实姿态结果与持续条件', '温和提醒 · 用一句话和声光提示', '继续观察 · 移动或遮挡时暂停，不强行判断']
    },
    emotion: {
      type: 'SAY IT OUT LOUD → A LITTLE COMPANY', title: '代码卡住了，先把情绪放下来。',
      context: '情绪垃圾桶是一种陪伴方式：你主动开口，小桶接住这一轮对话。',
      speaker: '你的桌面', event: '又一次报错，想找个地方吐槽两句。',
      creature: '可以，先说给我听。是报错太多，还是不知道下一步怎么改？', user: '调了很久都没好，有点烦。先陪我缓一会儿。',
      outcome: '先回应当下表达，再由你决定继续聊、整理问题或回到编码任务。',
      condition: '接入条件：明确唤醒或约定的一轮语音交互；不预设自动情绪识别。',
      steps: ['主动开口 · 用户唤醒后表达想法', '听清内容 · 把这一轮话准确转写', '接住情绪 · 回应用户已经表达的感受', '由你选择 · 陪聊、梳理问题或回到任务']
    },
    bin: {
      type: 'DESKTOP BIN → PHYSICAL RESPONSE', title: '小纸团，也有它的位置。',
      context: '一只真正有收纳用途的桌面伙伴。投放、开盖和回到待机组成一条物理交互支线。',
      speaker: '桌面 / 投放', event: '纸团靠近投放区域，等待识别与开盖。',
      creature: '这里交给我。', user: '把桌面小纸团放进去。',
      outcome: '目标是识别有效投放、驱动嘴盖并安全收回；动作完成需要真实机构回执。',
      condition: '接入条件：实际视觉触发、舵机控制与开合安全；此处为目标交互，需实物验证。',
      steps: ['投放靠近 · 实际检测投放区域', '开盖响应 · 机构在有效条件下打开', '完成投放 · 留出安全投放空间', '回到待机 · 安全收盖并读取动作结果']
    }
  };
  const tabs = Array.from(document.querySelectorAll('[data-scene]'));
  let currentScene = 'done';
  let currentStep = 0;
  ['事件', '小桶', '你', '结果'].forEach((name, index) => {
    const button = document.createElement('button');
    button.type = 'button';
    button.textContent = `${index + 1}. ${name}`;
    button.addEventListener('click', () => setStep(index));
    $('demoSteps').append(button);
  });
  function setStep(index) {
    currentStep = index;
    const scene = scenes[currentScene];
    $('stepDescription').textContent = scene.steps[index];
    $('demoSteps').querySelectorAll('button').forEach((button, i) => {
      button.classList.toggle('is-active', i === index);
      button.setAttribute('aria-label', `步骤 ${i + 1}：${scene.steps[i]}`);
      if (i === index) button.setAttribute('aria-current', 'step');
      else button.removeAttribute('aria-current');
    });
    $('dialogue').querySelectorAll('.dialogue-line').forEach((line, i) => line.classList.toggle('is-current', i === index));
    document.querySelector('.scene-outcome').classList.toggle('is-current', index === 3);
    $('nextStep').replaceChildren(document.createTextNode(index === 3 ? '重新演示 ' : '查看下一步 '));
    const arrow = document.createElement('span');
    arrow.setAttribute('aria-hidden', 'true');
    arrow.textContent = index === 3 ? '↺' : '→';
    $('nextStep').append(arrow);
  }
  function selectScene(key) {
    currentScene = key;
    const scene = scenes[key];
    tabs.forEach((tab) => {
      const active = tab.dataset.scene === key;
      tab.setAttribute('aria-selected', String(active));
      tab.tabIndex = active ? 0 : -1;
    });
    $('scenePanel').setAttribute('aria-labelledby', `scene-${key}`);
    $('sceneType').textContent = scene.type;
    $('sceneCount').textContent = `${String(Object.keys(scenes).indexOf(key) + 1).padStart(2, '0')} / 07`;
    $('sceneTitle').textContent = scene.title;
    $('sceneContext').textContent = scene.context;
    $('sceneOutcome').textContent = scene.outcome;
    $('sceneCondition').textContent = scene.condition;
    $('dialogue').replaceChildren();
    [[scene.speaker, scene.event, ''], ['小桶', scene.creature, 'creature'], ['你', scene.user, 'person']].forEach(([speaker, content, className]) => {
      const line = document.createElement('div');
      line.className = `dialogue-line ${className}`;
      const label = document.createElement('span');
      label.className = 'speaker';
      label.textContent = speaker;
      const paragraph = document.createElement('p');
      paragraph.textContent = content;
      line.append(label, paragraph);
      $('dialogue').append(line);
    });
    setStep(0);
  }
  tabs.forEach((tab, index) => {
    tab.addEventListener('click', () => selectScene(tab.dataset.scene));
    tab.addEventListener('keydown', (event) => {
      let next = index;
      if (event.key === 'ArrowDown' || event.key === 'ArrowRight') next = (index + 1) % tabs.length;
      else if (event.key === 'ArrowUp' || event.key === 'ArrowLeft') next = (index - 1 + tabs.length) % tabs.length;
      else if (event.key === 'Home') next = 0;
      else if (event.key === 'End') next = tabs.length - 1;
      else return;
      event.preventDefault();
      selectScene(tabs[next].dataset.scene);
      tabs[next].focus();
    });
  });
  $('nextStep').addEventListener('click', () => setStep((currentStep + 1) % 4));
  selectScene('done');

  let viewer;
  let loadingModel = false;
  const modelButton = $('loadModel');
  modelButton.addEventListener('click', async () => {
    if (viewer && viewer.loaded) {
      viewer.cameraOrbit = '0deg 75deg auto';
      viewer.jumpCameraToGoal();
      $('modelStatus').textContent = '已恢复初始视角。拖动旋转，滚轮或双指缩放。';
      return;
    }
    if (loadingModel) return;
    loadingModel = true;
    modelButton.disabled = true;
    modelButton.textContent = '正在载入…';
    $('modelStatus').textContent = '正在载入轻量外观参考（约 4.2 MB）…';
    try {
      await import('./assets/model-viewer.min.js');
      await customElements.whenDefined('model-viewer');
      viewer = document.createElement('model-viewer');
      const attributes = {src: 'assets/xiaotong-reference.glb', alt: '可旋转的小桶原始外观参考，非制造模型', 'camera-controls': '', 'touch-action': 'pan-y', 'shadow-intensity': '0.7', 'environment-image': 'neutral', exposure: '1.1', 'camera-orbit': '0deg 75deg auto', 'interaction-prompt': 'none', loading: 'eager', reveal: 'auto', poster: 'assets/original-reference.webp'};
      Object.entries(attributes).forEach(([key, value]) => viewer.setAttribute(key, value));
      await new Promise((resolve, reject) => {
        viewer.addEventListener('load', resolve, { once: true });
        viewer.addEventListener('error', () => reject(new Error('model-load-failed')), { once: true });
        $('modelPoster').hidden = true;
        $('modelStage').prepend(viewer);
      });
      modelButton.textContent = '恢复初始视角 ↺';
      $('modelStatus').textContent = '拖动旋转，滚轮或双指缩放。此模型仅用于观察外观。';
    } catch (error) {
      if (viewer) viewer.remove();
      viewer = undefined;
      $('modelPoster').hidden = false;
      modelButton.textContent = '重新载入 3D ↗';
      $('modelStatus').textContent = '当前浏览器未能显示 3D，可先查看外观图，或重新载入。';
    } finally {
      loadingModel = false;
      modelButton.disabled = false;
    }
  });

  const imageDialog = $('imageDialog');
  let imageTrigger;
  document.querySelectorAll('[data-image]').forEach((button) => button.addEventListener('click', () => {
    imageTrigger = button;
    $('largeImage').src = button.dataset.image;
    $('largeImage').alt = button.querySelector('img').alt;
    $('imageCaption').textContent = button.dataset.caption;
    imageDialog.showModal();
  }));
  $('closeImage').addEventListener('click', () => imageDialog.close());
  imageDialog.addEventListener('click', (event) => {
    if (event.target !== imageDialog) return;
    const rect = imageDialog.getBoundingClientRect();
    if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) imageDialog.close();
  });
  imageDialog.addEventListener('close', () => { if (imageTrigger) imageTrigger.focus(); });
})();
