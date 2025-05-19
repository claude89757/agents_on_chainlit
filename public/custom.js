document.addEventListener('DOMContentLoaded', () => {
    // 创建水印元素
    const watermark = document.createElement('div');
    watermark.id = 'custom-watermark';
    watermark.textContent = 'AI 也可能会犯错。请核查重要信息。';
    document.body.appendChild(watermark);

    // 确保水印始终显示
    watermark.classList.remove('hidden');
});


window.addEventListener("chainlit-call-fn", (e) => {
    const { name, args, callback } = e.detail;
    if (name === "url_query_parameter") {
      callback((new URLSearchParams(window.location.search)).get(args.msg));
    }
    else if (name === "update_url_param") {
      // 更新URL参数的函数
      const urlParams = new URLSearchParams(window.location.search);
      urlParams.set(args.param, args.value);
      const newUrl = window.location.pathname + '?' + urlParams.toString();
      window.history.pushState({}, '', newUrl);
      callback(true); // 返回成功
    }
  });