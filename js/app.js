window.App = (function() {
  let currentData = null;
  let currentCurrency = 'SAR';
  let fxRate = 0.2666;

  function init() {
    currentData = window.INITIAL_DATA || null;
    if (currentData && currentData.kpis && currentData.kpis.usd_fx_rate) {
      fxRate = currentData.kpis.usd_fx_rate;
    }

    renderAll();
    window.ExcelParser.init();

    if (window.lucide) {
      window.lucide.createIcons();
    }
  }

  function getData() {
    return currentData;
  }

  function recalculateRollups() {
    if (!currentData || !currentData.transactions) return;

    const staffMap = {};
    const taskMap = {};
    const weeklyMap = {};

    let totalHours = 0;
    let totalCost = 0;
    let totalRev = 0;

    currentData.transactions.forEach((t, idx) => {
      t.id = idx + 1;
      const q = t.qty || 0;
      const c = t.burdened_cost || 0;
      const r = t.revenue || 0;

      totalHours += q;
      totalCost += c;
      totalRev += r;

      if (!staffMap[t.employee]) {
        staffMap[t.employee] = {
          name: t.employee,
          emp_id: t.emp_id || '',
          total_hours: 0,
          raw_cost: 0,
          burdened_cost: 0,
          revenue: 0,
          tasks: new Set(),
          tx_count: 0
        };
      }
      const s = staffMap[t.employee];
      s.total_hours += q;
      s.raw_cost += (t.raw_cost || 0);
      s.burdened_cost += c;
      s.revenue += r;
      s.tasks.add(t.task);
      s.tx_count++;

      if (!taskMap[t.task]) {
        taskMap[t.task] = {
          task_code: t.task,
          description: t.task_desc || '',
          category: 'Supervision',
          total_hours: 0,
          raw_cost: 0,
          burdened_cost: 0,
          revenue: 0,
          tx_count: 0,
          staff: new Set()
        };
      }
      const tk = taskMap[t.task];
      tk.total_hours += q;
      tk.raw_cost += (t.raw_cost || 0);
      tk.burdened_cost += c;
      tk.revenue += r;
      tk.tx_count++;
      tk.staff.add(t.employee);

      if (t.item_date) {
        try {
          const dt = new Date(t.item_date);
          const day = dt.getDay();
          const diff = dt.getDate() - day + (day === 0 ? -6 : 1);
          const mon = new Date(dt.setDate(diff)).toISOString().slice(0, 10);
          if (!weeklyMap[mon]) {
            weeklyMap[mon] = { week_start: mon, hours: 0, cost: 0, revenue: 0, tx_count: 0 };
          }
          weeklyMap[mon].hours += q;
          weeklyMap[mon].cost += c;
          weeklyMap[mon].revenue += r;
          weeklyMap[mon].tx_count++;
        } catch (e) {}
      }
    });

    currentData.staff_analytics = Object.values(staffMap).map(s => {
      const cost = Math.round(s.burdened_cost * 100) / 100;
      const rev = Math.round(s.revenue * 100) / 100;
      const margin = Math.round((rev - cost) * 100) / 100;
      const margin_pct = rev !== 0 ? Math.round((margin / rev * 100) * 10) / 10 : (cost === 0 ? 0 : -100);
      return {
        name: s.name,
        emp_id: s.emp_id,
        total_hours: Math.round(s.total_hours * 10) / 10,
        raw_cost: Math.round(s.raw_cost * 100) / 100,
        burdened_cost: cost,
        revenue: rev,
        margin: margin,
        margin_pct: margin_pct,
        avg_hourly_cost: s.total_hours > 0 ? Math.round((cost / s.total_hours) * 100) / 100 : 0,
        avg_hourly_rev: s.total_hours > 0 ? Math.round((rev / s.total_hours) * 100) / 100 : 0,
        tasks_count: s.tasks.size,
        tx_count: s.tx_count,
        is_negative_margin: margin < -100
      };
    }).sort((a, b) => b.burdened_cost - a.burdened_cost);

    currentData.task_analytics = Object.values(taskMap).map(tk => {
      const cost = Math.round(tk.burdened_cost * 100) / 100;
      const rev = Math.round(tk.revenue * 100) / 100;
      const margin = Math.round((rev - cost) * 100) / 100;
      const margin_pct = rev !== 0 ? Math.round((margin / rev * 100) * 10) / 10 : 0;
      return {
        task_code: tk.task_code,
        description: tk.description || 'Supervision / Support',
        category: tk.category,
        total_hours: Math.round(tk.total_hours * 10) / 10,
        burdened_cost: cost,
        revenue: rev,
        margin: margin,
        margin_pct: margin_pct,
        staff_count: tk.staff.size,
        tx_count: tk.tx_count
      };
    }).sort((a, b) => b.burdened_cost - a.burdened_cost);

    currentData.weekly_series = Object.values(weeklyMap).sort((a, b) => a.week_start.localeCompare(b.week_start));

    if (currentData.kpis && currentData.kpis.pjtd) {
      currentData.kpis.pjtd.hours = Math.round(totalHours * 100) / 100;
      currentData.kpis.pjtd.cost = Math.round(totalCost * 100) / 100;
      currentData.kpis.pjtd.revenue = Math.round(totalRev * 100) / 100;
      currentData.kpis.pjtd.gm = Math.round((totalRev - totalCost) * 100) / 100;
      currentData.kpis.pjtd.gm_pct = totalRev !== 0 ? (currentData.kpis.pjtd.gm / totalRev * 100) : 0;
    }
  }

  function formatMoney(amount, curr = currentCurrency) {
    if (amount === null || amount === undefined || isNaN(amount)) return '--';
    const val = curr === 'USD' ? (amount * fxRate) : amount;
    const prefix = curr === 'USD' ? '$' : 'SAR ';
    return prefix + Number(val).toLocaleString(undefined, {
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    });
  }

  function formatMoneyExact(amount, curr = currentCurrency) {
    if (amount === null || amount === undefined || isNaN(amount)) return '--';
    const val = curr === 'USD' ? (amount * fxRate) : amount;
    const prefix = curr === 'USD' ? '$' : 'SAR ';
    return prefix + Number(val).toLocaleString(undefined, {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    });
  }

  function setCurrency(curr) {
    currentCurrency = curr;
    const sarBtn = document.getElementById('btn-curr-sar');
    const usdBtn = document.getElementById('btn-curr-usd');

    if (sarBtn) {
      sarBtn.className = curr === 'SAR' 
        ? 'px-2.5 py-1 rounded bg-teal-500 text-slate-950 font-bold transition'
        : 'px-2.5 py-1 rounded text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition';
    }
    if (usdBtn) {
      usdBtn.className = curr === 'USD' 
        ? 'px-2.5 py-1 rounded bg-teal-500 text-slate-950 font-bold transition'
        : 'px-2.5 py-1 rounded text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition';
    }

    renderKPIs();
    renderScopeTable();
    renderStaffTable();
    renderTaskTable();
    window.TableExplorer.filter();
  }

  function toggleTheme() {
    const html = document.documentElement;
    const isDark = html.classList.toggle('dark');
    
    const themeIcon = document.getElementById('theme-icon');
    const themeText = document.getElementById('theme-text');

    if (themeIcon) {
      themeIcon.setAttribute('data-lucide', isDark ? 'sun' : 'moon');
      themeIcon.className = isDark ? 'w-3.5 h-3.5 text-amber-500' : 'w-3.5 h-3.5 text-indigo-500';
    }
    if (themeText) {
      themeText.textContent = isDark ? 'Light' : 'Dark';
    }

    if (window.ChartsManager) {
      window.ChartsManager.init(currentData);
    }
    if (window.lucide) {
      window.lucide.createIcons();
    }
  }

  function switchTab(tabId) {
    const tabs = ['tab-overview', 'tab-staff', 'tab-tasks', 'tab-finance', 'tab-transactions'];
    tabs.forEach(t => {
      const el = document.getElementById(t);
      const btn = document.getElementById('btn-' + t);
      if (t === tabId) {
        if (el) el.classList.remove('hidden');
        if (btn) btn.className = 'tab-btn pb-3 tab-active flex items-center gap-2';
      } else {
        if (el) el.classList.add('hidden');
        if (btn) btn.className = 'tab-btn pb-3 text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200 flex items-center gap-2 transition';
      }
    });

    if (window.lucide) {
      window.lucide.createIcons();
    }
  }

  function renderKPIs() {
    if (!currentData || !currentData.kpis) return;
    const k = currentData.kpis;

    const elPjtdRev = document.getElementById('kpi-pjtd-rev');
    const elBaseRev = document.getElementById('kpi-base-rev');
    const elPjtdCost = document.getElementById('kpi-pjtd-cost');
    const elBaseCost = document.getElementById('kpi-base-cost');
    const elBurnCost = document.getElementById('kpi-weekly-burn-cost');
    const elWip = document.getElementById('kpi-wip');
    const elReconWip = document.getElementById('recon-wip');

    if (elPjtdRev) elPjtdRev.textContent = formatMoney(k.pjtd.revenue);
    if (elBaseRev) elBaseRev.textContent = formatMoney(k.baseline.revenue);
    if (elPjtdCost) elPjtdCost.textContent = formatMoney(k.pjtd.cost);
    if (elBaseCost) elBaseCost.textContent = formatMoney(k.baseline.cost);
    if (elBurnCost) elBurnCost.textContent = formatMoney(k.weekly_burn_cost);
    if (elWip) elWip.textContent = formatMoney(k.working_capital.wip);
    if (elReconWip) elReconWip.textContent = formatMoney(k.working_capital.wip);
  }

  function renderScopeTable() {
    if (!currentData || !currentData.scope_items) return;
    const tbody = document.getElementById('table-scope-body');
    if (!tbody) return;
    tbody.innerHTML = '';

    const fragment = document.createDocumentFragment();

    currentData.scope_items.forEach(item => {
      const tr = document.createElement('tr');
      tr.className = 'hover:bg-slate-100/60 dark:hover:bg-slate-800/40 transition font-numeric';
      const gmClass = item.pjtd_gm < 0 ? 'text-red-500 dark:text-red-400 font-semibold' : 'text-slate-700 dark:text-slate-300';
      const statusBadge = item.pjtd_gm < 0 
        ? '<span class="px-2 py-0.5 rounded text-[10px] font-sans bg-red-500/10 text-red-500 dark:text-red-400 border border-red-500/20 font-medium">Over Budget</span>'
        : '<span class="px-2 py-0.5 rounded text-[10px] font-sans bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20 font-medium">On Track</span>';

      tr.innerHTML = `
        <td class="py-2 px-3 font-sans font-medium text-slate-900 dark:text-white">${item.name} <span class="text-slate-400 dark:text-slate-500 text-[10px]">(${item.code})</span></td>
        <td class="py-2 px-3 text-right text-slate-500 dark:text-slate-400">${formatMoney(item.baseline_revenue)}</td>
        <td class="py-2 px-3 text-right text-slate-500 dark:text-slate-400">${formatMoney(item.baseline_cost)}</td>
        <td class="py-2 px-3 text-right text-slate-500 dark:text-slate-400">${item.baseline_gm_pct.toFixed(1)}%</td>
        <td class="py-2 px-3 text-right text-teal-600 dark:text-teal-400 font-medium">${formatMoney(item.pjtd_revenue)}</td>
        <td class="py-2 px-3 text-right text-blue-600 dark:text-blue-400 font-medium">${formatMoney(item.pjtd_cost)}</td>
        <td class="py-2 px-3 text-right ${gmClass}">${formatMoney(item.pjtd_gm)}</td>
        <td class="py-2 px-3 text-right font-medium ${item.pjtd_gm_pct < 0 ? 'text-red-500 dark:text-red-400' : 'text-slate-700 dark:text-slate-300'}">${item.pjtd_gm_pct.toFixed(1)}%</td>
        <td class="py-2 px-3 text-center">${statusBadge}</td>
      `;
      fragment.appendChild(tr);
    });

    tbody.appendChild(fragment);
  }

  function renderStaffTable() {
    if (!currentData || !currentData.staff_analytics) return;
    const query = (document.getElementById('filter-staff-search')?.value || '').toLowerCase().trim();
    const marginFilter = document.getElementById('filter-staff-margin')?.value || 'all';
    const tbody = document.getElementById('table-staff-body');
    if (!tbody) return;
    tbody.innerHTML = '';

    let totalStaff = currentData.staff_analytics.length;
    let negStaff = 0;
    const fragment = document.createDocumentFragment();

    currentData.staff_analytics.forEach(s => {
      if (s.margin < -100) negStaff++;

      const matchesQuery = !query || s.name.toLowerCase().includes(query) || (s.emp_id && s.emp_id.includes(query));
      let matchesMargin = true;
      if (marginFilter === 'negative') matchesMargin = s.margin < 0;
      if (marginFilter === 'positive') matchesMargin = s.margin >= 0;

      if (!matchesQuery || !matchesMargin) return;

      const tr = document.createElement('tr');
      tr.className = 'hover:bg-slate-100/60 dark:hover:bg-slate-800/40 transition font-numeric';
      const isNeg = s.margin < 0;
      const statusBadge = isNeg 
        ? '<span class="px-2 py-0.5 rounded text-[10px] font-sans bg-red-500/10 text-red-500 dark:text-red-400 border border-red-500/20 font-semibold">Margin Loss</span>'
        : '<span class="px-2 py-0.5 rounded text-[10px] font-sans bg-teal-500/10 text-teal-600 dark:text-teal-400 border border-teal-500/20 font-medium">Positive</span>';

      tr.innerHTML = `
        <td class="py-2 px-3 font-sans font-medium text-slate-900 dark:text-white">
          ${s.name}
          <span class="text-slate-400 dark:text-slate-500 block text-[10px]">ID: ${s.emp_id || 'N/A'} &bull; ${s.tasks_count} Tasks</span>
        </td>
        <td class="py-2 px-3 text-right text-slate-800 dark:text-slate-200">${s.total_hours.toLocaleString()}</td>
        <td class="py-2 px-3 text-right text-blue-600 dark:text-blue-400 font-medium">${formatMoneyExact(s.burdened_cost)}</td>
        <td class="py-2 px-3 text-right text-teal-600 dark:text-teal-400 font-medium">${formatMoneyExact(s.revenue)}</td>
        <td class="py-2 px-3 text-right font-semibold ${isNeg ? 'text-red-500 dark:text-red-400' : 'text-emerald-600 dark:text-emerald-400'}">${formatMoneyExact(s.margin)}</td>
        <td class="py-2 px-3 text-right font-bold ${isNeg ? 'text-red-500 dark:text-red-400' : 'text-slate-800 dark:text-slate-200'}">${s.margin_pct.toFixed(1)}%</td>
        <td class="py-2 px-3 text-right text-slate-500 dark:text-slate-400">${formatMoneyExact(s.avg_hourly_cost)}</td>
        <td class="py-2 px-3 text-right text-slate-500 dark:text-slate-400">${formatMoneyExact(s.avg_hourly_rev)}</td>
        <td class="py-2 px-3 text-center">${statusBadge}</td>
      `;
      fragment.appendChild(tr);
    });

    tbody.appendChild(fragment);

    const statTotal = document.getElementById('stat-total-staff');
    const statNeg = document.getElementById('stat-neg-staff');
    const badgeNeg = document.getElementById('badge-neg-margin');

    if (statTotal) statTotal.textContent = totalStaff;
    if (statNeg) statNeg.textContent = negStaff;
    if (badgeNeg) badgeNeg.textContent = `${negStaff} At Risk`;
  }

  function renderTaskTable() {
    if (!currentData || !currentData.task_analytics) return;
    const query = (document.getElementById('filter-task-search')?.value || '').toLowerCase().trim();
    const tbody = document.getElementById('table-task-body');
    if (!tbody) return;
    tbody.innerHTML = '';

    const fragment = document.createDocumentFragment();

    currentData.task_analytics.forEach(t => {
      const matchesQuery = !query || t.task_code.toLowerCase().includes(query) || (t.description && t.description.toLowerCase().includes(query));
      if (!matchesQuery) return;

      const tr = document.createElement('tr');
      tr.className = 'hover:bg-slate-100/60 dark:hover:bg-slate-800/40 transition font-numeric';
      const isNeg = t.margin < 0;

      tr.innerHTML = `
        <td class="py-2 px-3 font-medium text-teal-600 dark:text-teal-400">${t.task_code}</td>
        <td class="py-2 px-3 font-sans text-slate-900 dark:text-white max-w-xs truncate" title="${t.description}">${t.description}</td>
        <td class="py-2 px-3 font-sans text-slate-500 dark:text-slate-400">${t.category}</td>
        <td class="py-2 px-3 text-right text-slate-800 dark:text-slate-200">${t.total_hours.toLocaleString()}</td>
        <td class="py-2 px-3 text-right text-blue-600 dark:text-blue-400 font-medium">${formatMoneyExact(t.burdened_cost)}</td>
        <td class="py-2 px-3 text-right text-teal-600 dark:text-teal-400 font-medium">${formatMoneyExact(t.revenue)}</td>
        <td class="py-2 px-3 text-right font-semibold ${isNeg ? 'text-red-500 dark:text-red-400' : 'text-emerald-600 dark:text-emerald-400'}">${formatMoneyExact(t.margin)}</td>
        <td class="py-2 px-3 text-right font-bold ${isNeg ? 'text-red-500 dark:text-red-400' : 'text-slate-800 dark:text-slate-200'}">${t.margin_pct.toFixed(1)}%</td>
        <td class="py-2 px-3 text-center text-slate-500 dark:text-slate-400">${t.staff_count}</td>
      `;
      fragment.appendChild(tr);
    });

    tbody.appendChild(fragment);
  }

  function renderAll() {
    renderKPIs();
    renderScopeTable();
    renderStaffTable();
    renderTaskTable();
    if (window.ChartsManager) {
      window.ChartsManager.init(currentData);
    }
    if (window.TableExplorer && currentData) {
      window.TableExplorer.init(currentData.transactions);
    }
    if (window.lucide) {
      window.lucide.createIcons();
    }
  }

  return {
    init,
    getData,
    recalculateRollups,
    formatMoney,
    formatMoneyExact,
    setCurrency,
    toggleTheme,
    switchTab,
    renderKPIs,
    renderScopeTable,
    renderStaffTable,
    renderTaskTable,
    renderAll
  };
})();

window.addEventListener('DOMContentLoaded', () => {
  window.App.init();
});
