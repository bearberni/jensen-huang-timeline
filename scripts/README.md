# 页面生成

在仓库根目录运行 `python3 scripts/build.py`，从 data/content.json、data/summary.json 和 templates/market.html 同时生成 index.html 与 tldr.html。只使用 Python 3 标准库。

`visuals.py`生成逐对象的直接关系浏览器；`social.py`从`data/social.json`生成两版可见的社交档案。原始回应和旧表仍保存在`data/content.json`以便追溯；修改新社交展示时应同步核对对应原始记录与分级，不把旧互动值当作实时数据。
