window.ExcelParser = (function() {
  function init() {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    if (!dropZone || !fileInput) return;

    dropZone.addEventListener('click', () => fileInput.click());

    ['dragenter', 'dragover'].forEach(name => {
      dropZone.addEventListener(name, (e) => {
        e.preventDefault();
        dropZone.classList.add('drag-over');
      });
    });

    ['dragleave', 'drop'].forEach(name => {
      dropZone.addEventListener(name, (e) => {
        e.preventDefault();
        dropZone.classList.remove('drag-over');
      });
    });

    dropZone.addEventListener('drop', (e) => {
      const files = e.dataTransfer.files;
      if (files && files.length > 0) {
        processFile(files[0]);
      }
    });

    fileInput.addEventListener('change', (e) => {
      const files = e.target.files;
      if (files && files.length > 0) {
        processFile(files[0]);
      }
    });
  }

  function excelDateToISO(serial) {
    if (!serial) return '';
    const num = parseFloat(serial);
    if (isNaN(num)) return String(serial);
    const base = new Date(Date.UTC(1899, 11, 30));
    const dt = new Date(base.getTime() + num * 86400000);
    return dt.toISOString().slice(0, 10);
  }

  function getTxKey(t) {
    if (t.trans_id && String(t.trans_id).trim() !== '') {
      return 'ID_' + String(t.trans_id).trim();
    }
    return `${t.project}|${t.task}|${t.employee}|${t.item_date}|${t.qty}|${t.trans_cost}|${t.burdened_cost}`;
  }

  function getZipEntry(zip, path) {
    if (!zip || !path) return null;
    return zip.file(path) || zip.file(path.replace(/\//g, '\\')) || (zip.file(new RegExp('^' + path.replace(/[.*+?^${}()|[\]\\]/g, '\\$&').replace(/\\\//g, '[\\\\/]') + '$', 'i')) || [])[0];
  }

  async function processFile(file) {
    if (!file.name.endsWith('.xlsx')) {
      alert('Please select an Excel (.xlsx) file.');
      return;
    }

    const uploadStatus = document.getElementById('upload-status');
    const uploadStatusText = document.getElementById('upload-status-text');
    if (uploadStatus) uploadStatus.classList.remove('hidden');
    if (uploadStatusText) uploadStatusText.textContent = `Reading ${file.name}...`;

    try {
      if (typeof JSZip === 'undefined') {
        throw new Error('JSZip library is not loaded. Please ensure network connection or local JSZip.');
      }

      const zip = await JSZip.loadAsync(file);

      const wbEntry = getZipEntry(zip, 'xl/workbook.xml');
      if (wbEntry) {
        let wbXml = await wbEntry.async('text');
        wbXml = wbXml.replace(/<definedNames>[\s\S]*?<\/definedNames>/g, '<definedNames/>');
        zip.file(wbEntry.name, wbXml);

        const cleanedBlob = await zip.generateAsync({ type: 'blob' });
        window.latestCleanedBlob = cleanedBlob;
        window.latestCleanedFilename = file.name.replace('.xlsx', '_Cleaned.xlsx');

        const dlBtn = document.getElementById('btn-download-cleaned');
        if (dlBtn) {
          dlBtn.onclick = (e) => {
            e.preventDefault();
            const url = URL.createObjectURL(cleanedBlob);
            const a = document.createElement('a');
            a.href = url;
            a.download = window.latestCleanedFilename;
            a.click();
          };
          dlBtn.classList.remove('opacity-50', 'pointer-events-none');
          dlBtn.innerHTML = '<i data-lucide="download" class="w-3.5 h-3.5"></i> Download';
          if (window.lucide) window.lucide.createIcons();
        }
      }

      if (uploadStatusText) uploadStatusText.textContent = 'Parsing workbook structure...';
      const parser = new DOMParser();

      let strings = [];
      const ssEntry = getZipEntry(zip, 'xl/sharedStrings.xml');
      if (ssEntry) {
        const sXml = await ssEntry.async('text');
        const sDoc = parser.parseFromString(sXml, 'application/xml');
        const sis = sDoc.getElementsByTagName('si');
        for (let i = 0; i < sis.length; i++) {
          strings.push(sis[i].textContent || '');
        }
      }

      const wbRels = {};
      const relsEntry = getZipEntry(zip, 'xl/_rels/workbook.xml.rels');
      if (relsEntry) {
        const rXml = await relsEntry.async('text');
        const rDoc = parser.parseFromString(rXml, 'application/xml');
        const rels = rDoc.getElementsByTagName('Relationship');
        for (let i = 0; i < rels.length; i++) {
          wbRels[rels[i].getAttribute('Id')] = rels[i].getAttribute('Target');
        }
      }

      const sheetMap = {};
      if (wbEntry) {
        const wbXml = await wbEntry.async('text');
        const wbDoc = parser.parseFromString(wbXml, 'application/xml');
        const sheets = wbDoc.getElementsByTagName('sheet');
        for (let i = 0; i < sheets.length; i++) {
          const sName = sheets[i].getAttribute('name');
          const rId = sheets[i].getAttribute('r:id') || sheets[i].getAttribute('id');
          const target = wbRels[rId] || '';
          const path = target.startsWith('worksheets/') ? 'xl/' + target : 'xl/worksheets/' + target;
          sheetMap[sName] = path;
        }
      }

      function parseSheetRows(xmlStr) {
        const doc = parser.parseFromString(xmlStr, 'application/xml');
        const rowsElem = doc.getElementsByTagName('row');
        const rows = {};
        for (let i = 0; i < rowsElem.length; i++) {
          const r = rowsElem[i];
          const rIdx = parseInt(r.getAttribute('r'), 10);
          const cells = {};
          const cs = r.getElementsByTagName('c');
          for (let j = 0; j < cs.length; j++) {
            const c = cs[j];
            const ref = c.getAttribute('r');
            const col = ref.replace(/[0-9]/g, '');
            const t = c.getAttribute('t');
            const vElem = c.getElementsByTagName('v')[0];
            let val = vElem ? vElem.textContent : '';
            if (t === 's' && val !== '') {
              val = strings[parseInt(val, 10)] || val;
            }
            cells[col] = val;
          }
          rows[rIdx] = cells;
        }
        return rows;
      }

      let txSheetPath = null;
      let isCombinedMaster = false;

      if (sheetMap['Oracle_Combined'] && getZipEntry(zip, sheetMap['Oracle_Combined'])) {
        txSheetPath = sheetMap['Oracle_Combined'];
        isCombinedMaster = true;
      } else if (sheetMap['SA859CMS'] && getZipEntry(zip, sheetMap['SA859CMS'])) {
        txSheetPath = sheetMap['SA859CMS'];
      } else if (sheetMap['SA859JUK'] && getZipEntry(zip, sheetMap['SA859JUK'])) {
        txSheetPath = sheetMap['SA859JUK'];
      } else if (getZipEntry(zip, 'xl/worksheets/sheet1.xml')) {
        txSheetPath = 'xl/worksheets/sheet1.xml';
      }

      const d = window.App.getData();
      if (!d.transactions) d.transactions = [];

      const existingKeys = new Set();
      d.transactions.forEach(t => existingKeys.add(getTxKey(t)));

      let addedCount = 0;
      let duplicateCount = 0;

      const txEntry = getZipEntry(zip, txSheetPath);
      if (txSheetPath && txEntry) {
        if (uploadStatusText) uploadStatusText.textContent = 'Deduplicating & importing transactions...';
        const txXml = await txEntry.async('text');
        const txRows = parseSheetRows(txXml);

        const rKeys = Object.keys(txRows).map(Number).sort((a, b) => a - b);
        let headerRowIndex = 1;
        for (const idx of rKeys.slice(0, 5)) {
          if (txRows[idx] && (txRows[idx]['A'] === 'Project' || txRows[idx]['B'] === 'Task')) {
            headerRowIndex = idx;
            break;
          }
        }

        for (const rIdx of rKeys) {
          if (rIdx <= headerRowIndex) continue;
          const r = txRows[rIdx];
          if (!r || !r['A'] || !r['B']) continue;

          const proj = r['A'] || '';
          const task = r['B'] || '';
          const emp = r['C'] || '';
          const empId = r['D'] || '';
          const expType = r['E'] || '';
          const itemDateRaw = r['F'] || '';
          const itemDate = excelDateToISO(itemDateRaw);
          const qty = parseFloat(r['G']) || 0;
          const transCurr = r['H'] || '';
          const transCost = parseFloat(r['I']) || 0;
          const rawCost = parseFloat(r['K']) || 0;
          const burdCost = parseFloat(r['L']) || 0;
          const accrRev = parseFloat(r['M']) || 0;
          const billRate = parseFloat(r['N']) || 0;
          const billAmt = parseFloat(r['O']) || 0;
          const billable = r['R'] || '';
          const transId = r['AT'] || '';
          const effRev = accrRev !== 0 ? accrRev : billAmt;

          const candidate = {
            id: d.transactions.length + 1,
            project: proj,
            task: task,
            task_desc: '',
            employee: emp,
            emp_id: empId,
            exp_type: expType,
            item_date: itemDate,
            qty: Math.round(qty * 100) / 100,
            trans_curr: transCurr,
            trans_cost: Math.round(transCost * 100) / 100,
            raw_cost: Math.round(rawCost * 100) / 100,
            burdened_cost: Math.round(burdCost * 100) / 100,
            revenue: Math.round(effRev * 100) / 100,
            margin: Math.round((effRev - burdCost) * 100) / 100,
            bill_rate: Math.round(billRate * 100) / 100,
            billable: billable,
            trans_id: transId
          };

          const key = getTxKey(candidate);
          if (existingKeys.has(key)) {
            duplicateCount++;
          } else {
            existingKeys.add(key);
            d.transactions.push(candidate);
            addedCount++;
          }
        }
      }

      const sumEntry = sheetMap['Summary'] ? getZipEntry(zip, sheetMap['Summary']) : null;
      if (isCombinedMaster && sumEntry) {
        const sumXml = await sumEntry.async('text');
        const sumRows = parseSheetRows(sumXml);

        if (sumRows[9]) {
          d.kpis.baseline.revenue = parseFloat(sumRows[9]['F']) || d.kpis.baseline.revenue;
        }
        if (sumRows[10]) {
          d.kpis.baseline.cost = parseFloat(sumRows[10]['F']) || d.kpis.baseline.cost;
        }
        if (sumRows[9] && sumRows[9]['S']) {
          d.kpis.weekly_burn_hours = parseFloat(sumRows[9]['S']) || d.kpis.weekly_burn_hours;
        }
        if (sumRows[10] && sumRows[10]['S']) {
          d.kpis.weekly_burn_cost = parseFloat(sumRows[10]['S']) || d.kpis.weekly_burn_cost;
        }
        if (sumRows[35] && sumRows[35]['G']) {
          d.kpis.working_capital.wip = parseFloat(sumRows[35]['G']) || d.kpis.working_capital.wip;
        }
      }

      if (addedCount > 0 || isCombinedMaster) {
        window.App.recalculateRollups();
      }

      window.App.renderAll();

      if (uploadStatusText) {
        if (addedCount === 0 && duplicateCount > 0) {
          uploadStatusText.textContent = `All ${duplicateCount.toLocaleString()} entries already in database (0 duplicates added).`;
        } else {
          uploadStatusText.textContent = `Imported: +${addedCount.toLocaleString()} new, ${duplicateCount.toLocaleString()} duplicates skipped (Total: ${d.transactions.length.toLocaleString()})`;
        }
      }

      setTimeout(() => {
        if (uploadStatus) uploadStatus.classList.add('hidden');
      }, 5000);

    } catch (err) {
      console.error(err);
      alert('Error parsing Excel report: ' + err.message);
      if (uploadStatus) uploadStatus.classList.add('hidden');
    }
  }

  return {
    init,
    processFile
  };
})();
