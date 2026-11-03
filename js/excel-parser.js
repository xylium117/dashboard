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

  async function processFile(file) {
    if (!file.name.endsWith('.xlsx')) {
      alert('Please select an Excel (.xlsx) file.');
      return;
    }

    const uploadStatus = document.getElementById('upload-status');
    const uploadStatusText = document.getElementById('upload-status-text');
    if (uploadStatus) uploadStatus.classList.remove('hidden');
    if (uploadStatusText) uploadStatusText.textContent = 'Reading Excel package...';

    try {
      if (typeof JSZip === 'undefined') {
        throw new Error('JSZip library is not loaded. Please ensure internet access or local script inclusion.');
      }

      const zip = await JSZip.loadAsync(file);

      if (uploadStatusText) uploadStatusText.textContent = 'Cleaning defined names bloat...';
      if (zip.file('xl/workbook.xml')) {
        let wbXml = await zip.file('xl/workbook.xml').async('text');
        wbXml = wbXml.replace(/<definedNames>[\s\S]*?<\/definedNames>/g, '<definedNames/>');
        zip.file('xl/workbook.xml', wbXml);

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

      if (uploadStatusText) uploadStatusText.textContent = 'Parsing sheet data...';
      const parser = new DOMParser();
      let strings = [];
      if (zip.file('xl/sharedStrings.xml')) {
        const sXml = await zip.file('xl/sharedStrings.xml').async('text');
        const sDoc = parser.parseFromString(sXml, 'application/xml');
        const sis = sDoc.getElementsByTagName('si');
        for (let i = 0; i < sis.length; i++) {
          strings.push(sis[i].textContent || '');
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

      if (zip.file('xl/worksheets/sheet5.xml')) {
        const sumXml = await zip.file('xl/worksheets/sheet5.xml').async('text');
        const sumRows = parseSheetRows(sumXml);

        const d = window.App.getData();
        if (sumRows[9]) {
          d.kpis.baseline.revenue = parseFloat(sumRows[9]['F']) || d.kpis.baseline.revenue;
          d.kpis.pjtd.revenue = parseFloat(sumRows[9]['G']) || d.kpis.pjtd.revenue;
        }
        if (sumRows[10]) {
          d.kpis.baseline.cost = parseFloat(sumRows[10]['F']) || d.kpis.baseline.cost;
          d.kpis.pjtd.cost = parseFloat(sumRows[10]['G']) || d.kpis.pjtd.cost;
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

      window.App.renderAll();

      if (uploadStatusText) {
        uploadStatusText.textContent = `Active: ${file.name}`;
      }
      setTimeout(() => {
        if (uploadStatus) uploadStatus.classList.add('hidden');
      }, 3500);

    } catch (err) {
      console.error('Error parsing Excel:', err);
      alert('Error parsing Excel file: ' + err.message);
      if (uploadStatus) uploadStatus.classList.add('hidden');
    }
  }

  return {
    init,
    processFile
  };
})();
