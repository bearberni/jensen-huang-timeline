(function () {
  'use strict';

  function initialiseMarket() {
    var root = document.getElementById('market');
    if (!root || root.dataset.marketReady === 'true') return;

    var rows = Array.prototype.slice.call(root.querySelectorAll('tr[data-market-date]'));
    var records = rows.map(function (row) {
      return {
        date: row.dataset.marketDate,
        close: Number(row.dataset.marketClose),
        plot: row.dataset.marketPlot === 'true',
        event: row.dataset.marketEvent,
        previousClose: row.dataset.marketPreviousClose ? Number(row.dataset.marketPreviousClose) : null,
        row: row
      };
    });
    var points = records.filter(function (record) { return record.plot; });
    if (points.length !== 5 || records.some(function (record) { return !Number.isFinite(record.close) || record.close <= 0; })) return;

    var explorer = root.querySelector('.market-explorer');
    var baseControl = root.querySelector('#market-base');
    var columns = root.querySelector('.market-columns');
    var axis = root.querySelector('.market-axis');
    var grid = root.querySelector('.market-grid');
    var baseLine = root.querySelector('.market-baseline');
    var selectedIndex = points.length - 1;
    var mode = 'price';
    var base = points[0];
    var buttons = [];

    function shortDate(date) { return date.slice(5); }
    function pct(value, basePrice) { return (value / basePrice - 1) * 100; }
    function signed(value, digits) {
      if (Math.abs(value) < .5 / Math.pow(10, digits)) return (0).toFixed(digits) + '%';
      return (value > 0 ? '+' : '−') + Math.abs(value).toFixed(digits) + '%';
    }
    function markSign(element, value) {
      element.classList.toggle('market-positive', value > .000001);
      element.classList.toggle('market-negative', value < -.000001);
    }
    function node(name, className, text) {
      var element = document.createElement(name);
      if (className) element.className = className;
      if (text !== undefined) element.textContent = text;
      return element;
    }

    points.forEach(function (point, index) {
      var button = node('button', 'market-point-button');
      button.type = 'button';
      button.dataset.marketPoint = point.date;
      var track = node('span', 'market-track');
      track.setAttribute('aria-hidden', 'true');
      track.appendChild(node('span', 'market-stem'));
      track.appendChild(node('span', 'market-dot'));
      track.appendChild(node('span', 'market-point-value'));
      button.appendChild(track);
      button.appendChild(node('span', 'market-point-date', shortDate(point.date)));
      button.addEventListener('click', function () { select(index); });
      button.addEventListener('keydown', function (event) {
        var next = null;
        if (event.key === 'ArrowRight') next = (index + 1) % points.length;
        if (event.key === 'ArrowLeft') next = (index - 1 + points.length) % points.length;
        if (event.key === 'Home') next = 0;
        if (event.key === 'End') next = points.length - 1;
        if (next === null) return;
        event.preventDefault();
        select(next);
        buttons[next].focus();
      });
      columns.appendChild(button);
      buttons.push(button);
    });

    function select(index) {
      selectedIndex = index;
      buttons.forEach(function (button, i) {
        button.setAttribute('aria-pressed', String(i === selectedIndex));
        button.tabIndex = i === selectedIndex ? 0 : -1;
      });
      var point = points[selectedIndex];
      var change = pct(point.close, base.close);
      root.querySelector('#market-selected-date').textContent = point.date + ' · ' + point.event;
      root.querySelector('#market-selected-close').textContent = '$' + point.close.toFixed(2);
      root.querySelector('#market-selected-comparison-label').textContent = '较 ' + shortDate(base.date) + ' 收盘';
      var output = root.querySelector('#market-selected-return');
      output.textContent = signed(change, 2);
      markSign(output, change);
      var daily = root.querySelector('#market-selected-day-change');
      daily.textContent = point.previousClose ? '较上一交易日 ' + signed(pct(point.close, point.previousClose), 2) : '该日用作区间比较时点';
      records.forEach(function (record) { record.row.classList.toggle('market-table-selected', record.date === point.date); });
    }

    function render() {
      var values = points.map(function (point) { return mode === 'price' ? point.close : pct(point.close, base.close); });
      var minimum = 0;
      var maximum = 260;
      var step = 50;
      if (mode === 'return') {
        var low = Math.min.apply(Math, values.concat([0])) - 10;
        var high = Math.max.apply(Math, values.concat([0])) + 10;
        step = high - low > 100 ? 25 : (high - low > 60 ? 20 : 10);
        minimum = Math.floor(low / step) * step;
        maximum = Math.ceil(high / step) * step;
      }
      function position(value) { return (value - minimum) / (maximum - minimum) * 100; }
      axis.replaceChildren();
      grid.replaceChildren();
      for (var tick = minimum; tick <= maximum; tick += step) {
        var axisText = mode === 'price' ? String(tick) : (tick < 0 ? '−' + Math.abs(tick) : String(tick)) + '%';
        var label = node('span', 'market-tick', axisText);
        label.style.bottom = position(tick) + '%';
        axis.appendChild(label);
        var gridLine = node('span', 'market-grid-line');
        gridLine.style.bottom = position(tick) + '%';
        grid.appendChild(gridLine);
      }
      var reference = mode === 'price' ? base.close : 0;
      baseLine.style.bottom = 'calc(var(--market-date-height) + var(--market-chart-height) * ' + position(reference) / 100 + ')';
      root.querySelector('#market-axis-unit').textContent = mode === 'price' ? '美元 · Close' : '相对基准 · %';
      root.querySelector('#market-baseline-label').textContent = '基准 ' + shortDate(base.date) + ' · $' + base.close.toFixed(2);

      points.forEach(function (point, index) {
        var button = buttons[index];
        var change = pct(point.close, base.close);
        var value = values[index];
        var y = position(value);
        var origin = position(0);
        var pointColor = Math.abs(change) < .000001 ? 'var(--muted, #6f6758)' : (change < 0 ? 'var(--market-negative)' : 'var(--market-positive)');
        button.style.setProperty('--point-color', pointColor);
        var stem = button.querySelector('.market-stem');
        stem.style.bottom = Math.min(y, origin) + '%';
        stem.style.height = Math.abs(y - origin) + '%';
        button.querySelector('.market-dot').style.bottom = y + '%';
        var valueLabel = button.querySelector('.market-point-value');
        valueLabel.style.bottom = 'calc(' + y + '% + 16px)';
        valueLabel.textContent = mode === 'price' ? String(Math.round(point.close)) : signed(change, 0);
        button.setAttribute('aria-label', point.date + '，' + point.event + '，收盘 ' + point.close.toFixed(2) + ' 美元；较 ' + base.date + ' 收盘 ' + signed(change, 2));
      });
      root.querySelector('#market-table-comparison').textContent = '较 ' + shortDate(base.date) + ' 收盘';
      records.forEach(function (record) {
        var cell = record.row.querySelector('.market-table-return');
        var change = pct(record.close, base.close);
        cell.textContent = signed(change, 2);
        markSign(cell, change);
      });
      select(selectedIndex);
    }

    root.querySelectorAll('input[name="market-view"]').forEach(function (radio) {
      radio.addEventListener('change', function () {
        if (!radio.checked) return;
        mode = radio.value;
        render();
      });
    });
    baseControl.addEventListener('change', function () {
      var next = points.find(function (point) { return point.date === baseControl.value; });
      if (!next) return;
      base = next;
      render();
    });

    render();
    root.dataset.marketReady = 'true';
    explorer.hidden = false;
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initialiseMarket, { once: true });
  else initialiseMarket();
})();
