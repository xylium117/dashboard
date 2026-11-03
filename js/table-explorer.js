window.TableExplorer = (function() {
  let allTransactions = [];
  let filteredTransactions = [];
  let currentPage = 1;
  let pageSize = 50;

  function init(transactions) {
    allTransactions = transactions || [];
    filter();
  }

  function filter() {
    const query = (document.getElementById('tx-search')?.value || '').toLowerCase().trim();
    const proj = document.getElementById('tx-project')?.value || 'all';
    const exp = document.getElementById('tx-exp-type')?.value || 'all';
    const bill = document.getElementById('tx-billable')?.value || 'all';

    let sumHrs = 0;
    let sumCost = 0;
    let sumRev = 0;

    filteredTransactions = allTransactions.filter(t => {
      if (proj !== 'all' && t.project !== proj) return false;
      if (exp !== 'all' && t.exp_type !== exp) return false;
      if (bill !== 'all' && t.billable !== bill) return false;
      if (query) {
        const fullStr = `${t.employee} ${t.task} ${t.exp_type} ${t.item_date} ${t.task_desc || ''}`.toLowerCase();
        if (!fullStr.includes(query)) return false;
      }
      sumHrs += t.qty;
      sumCost += t.burdened_cost;
      sumRev += t.revenue;
      return true;
    });

    const statCount = document.getElementById('tx-stat-count');
    const statHours = document.getElementById('tx-stat-hours');
    const statCost = document.getElementById('tx-stat-cost');
    const statRev = document.getElementById('tx-stat-rev');

    if (statCount) statCount.textContent = filteredTransactions.length.toLocaleString();
    if (statHours) statHours.textContent = sumHrs.toLocaleString(undefined, { minimumFractionDigits: 1, maximumFractionDigits: 1 });
    if (statCost) statCost.textContent = window.App ? window.App.formatMoney(sumCost) : sumCost.toFixed(2);
    if (statRev) statRev.textContent = window.App ? window.App.formatMoney(sumRev) : sumRev.toFixed(2);

    currentPage = 1;
    renderPage();
  }

  function setPageSize(size) {
    pageSize = parseInt(size, 10) || 50;
    currentPage = 1;
    renderPage();
  }

  function changePage(delta) {
    const maxPages = Math.ceil(filteredTransactions.length / pageSize) || 1;
    currentPage = Math.max(1, Math.min(maxPages, currentPage + delta));
    renderPage();
  }

  function renderPage() {
    const tbody = document.getElementById('table-tx-body');
    if (!tbody) return;
    tbody.innerHTML = '';

    const total = filteredTransactions.length;
    const start = (currentPage - 1) * pageSize;
    const end = Math.min(start + pageSize, total);
    const pageRows = filteredTransactions.slice(start, end);

    const fragment = document.createDocumentFragment();

    pageRows.forEach(t => {
      const tr = document.createElement('tr');
      tr.className = 'hover:bg-slate-100/60 dark:hover:bg-slate-800/40 transition font-numeric text-[11px]';
      const isNeg = t.margin < 0;

      tr.innerHTML = `
        <td class="py-1.5 px-2.5 text-slate-400 dark:text-slate-500">${t.id}</td>
        <td class="py-1.5 px-2.5 text-slate-700 dark:text-slate-300 font-sans">${t.item_date || 'N/A'}</td>
        <td class="py-1.5 px-2.5"><span class="px-1.5 py-0.5 rounded bg-slate-200 dark:bg-slate-800 text-teal-600 dark:text-teal-400 text-[10px] font-sans font-medium">${t.project}</span></td>
        <td class="py-1.5 px-2.5 text-slate-700 dark:text-slate-300" title="${t.task_desc || ''}">${t.task}</td>
        <td class="py-1.5 px-2.5 text-slate-900 dark:text-white font-sans font-medium max-w-[180px] truncate" title="${t.employee}">${t.employee}</td>
        <td class="py-1.5 px-2.5 text-slate-500 dark:text-slate-400 font-sans text-[10px]">${t.exp_type}</td>
        <td class="py-1.5 px-2.5 text-right font-bold text-slate-900 dark:text-white">${t.qty.toFixed(1)}</td>
        <td class="py-1.5 px-2.5 text-right text-blue-600 dark:text-blue-400">${window.App ? window.App.formatMoneyExact(t.burdened_cost) : t.burdened_cost}</td>
        <td class="py-1.5 px-2.5 text-right text-teal-600 dark:text-teal-400">${window.App ? window.App.formatMoneyExact(t.revenue) : t.revenue}</td>
        <td class="py-1.5 px-2.5 text-right font-medium ${isNeg ? 'text-red-500 dark:text-red-400' : 'text-emerald-600 dark:text-emerald-400'}">${window.App ? window.App.formatMoneyExact(t.margin) : t.margin}</td>
        <td class="py-1.5 px-2.5 text-center"><span class="px-1 py-0.5 rounded text-[10px] font-sans ${t.billable === 'Y' ? 'bg-teal-500/10 text-teal-600 dark:text-teal-400 font-medium' : 'bg-slate-200 dark:bg-slate-800 text-slate-500 dark:text-slate-400'}">${t.billable}</span></td>
      `;
      fragment.appendChild(tr);
    });

    tbody.appendChild(fragment);

    const pageInfo = document.getElementById('tx-page-info');
    if (pageInfo) {
      pageInfo.textContent = total === 0 ? 'No matching records' : `Showing ${(start + 1).toLocaleString()} to ${end.toLocaleString()} of ${total.toLocaleString()}`;
    }

    const prevBtn = document.getElementById('btn-tx-prev');
    const nextBtn = document.getElementById('btn-tx-next');
    if (prevBtn) prevBtn.disabled = currentPage <= 1;
    if (nextBtn) nextBtn.disabled = end >= total;
  }

  function exportFilteredCSV() {
    if (filteredTransactions.length === 0) {
      alert('No matching records to export.');
      return;
    }
    const keys = Object.keys(filteredTransactions[0]);
    let csvContent = 'data:text/csv;charset=utf-8,' + keys.join(',') + '\n';
    filteredTransactions.forEach(row => {
      const vals = keys.map(k => `"${String(row[k] || '').replace(/"/g, '""')}"`);
      csvContent += vals.join(',') + '\n';
    });
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `Oracle_Transactions_Filtered_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }

  return {
    init,
    filter,
    setPageSize,
    changePage,
    exportFilteredCSV
  };
})();
