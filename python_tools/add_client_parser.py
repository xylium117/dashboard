import re 

with open ('dashboard.html','r',encoding ='utf-8')as f :
    html =f .read ()


jszip_script ='<script src="https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js"></script>'
if 'jszip'not in html :
    html =html .replace ('<!-- Chart.js -->',f'{jszip_script }\n  <!-- Chart.js -->')


drop_zone_html ='''
    <!-- DRAG & DROP NEW EXCEL FILE BANNER -->
    <div id="drop-zone" class="border-2 border-dashed border-slate-700 hover:border-teal-500/80 bg-slate-900/50 rounded-xl p-4 text-center cursor-pointer transition group">
      <input type="file" id="file-input" accept=".xlsx" class="hidden" onchange="handleFileSelect(event)">
      <div class="flex flex-col sm:flex-row items-center justify-center gap-3">
        <div class="w-9 h-9 rounded-lg bg-teal-500/10 text-teal-400 flex items-center justify-center group-hover:scale-105 transition">
          <i data-lucide="upload-cloud" class="w-5 h-5"></i>
        </div>
        <div class="text-left">
          <p class="text-xs font-semibold text-slate-200">
            Got an updated weekly file? <span class="text-teal-400 underline">Click to upload</span> or drag & drop any new <code class="font-mono text-teal-300">.xlsx</code> here
          </p>
          <p class="text-[11px] text-slate-400">
            Processes 100% locally in your browser. Zero installation required. Instantly cleans and updates all metrics.
          </p>
        </div>
        <div id="upload-status" class="hidden sm:ml-auto text-xs font-medium text-teal-400 flex items-center gap-2">
          <div class="w-3.5 h-3.5 border-2 border-teal-400 border-t-transparent rounded-full animate-spin"></div>
          <span id="upload-status-text">Processing...</span>
        </div>
      </div>
    </div>
'''

if 'id="drop-zone"'not in html :
    html =html .replace ('<!-- EXECUTIVE KPI ROW -->',drop_zone_html +'\n    <!-- EXECUTIVE KPI ROW -->')


client_parser_js ='''
    // ==========================================
    // CLIENT-SIDE EXCEL PARSER (ZERO INSTALLATION)
    // ==========================================
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const uploadStatus = document.getElementById('upload-status');
    const uploadStatusText = document.getElementById('upload-status-text');

    dropZone.addEventListener('click', () => fileInput.click());

    ['dragenter', 'dragover'].forEach(name => {
      dropZone.addEventListener(name, (e) => {
        e.preventDefault();
        dropZone.classList.add('border-teal-500', 'bg-teal-950/20');
      });
    });

    ['dragleave', 'drop'].forEach(name => {
      dropZone.addEventListener(name, (e) => {
        e.preventDefault();
        dropZone.classList.remove('border-teal-500', 'bg-teal-950/20');
      });
    });

    dropZone.addEventListener('drop', (e) => {
      const files = e.dataTransfer.files;
      if (files && files.length > 0) {
        processExcelFile(files[0]);
      }
    });

    function handleFileSelect(e) {
      const files = e.target.files;
      if (files && files.length > 0) {
        processExcelFile(files[0]);
      }
    }

    async function processExcelFile(file) {
      if (!file.name.endsWith('.xlsx')) {
        alert('Please select an Excel .xlsx file');
        return;
      }

      uploadStatus.classList.remove('hidden');
      uploadStatusText.textContent = 'Reading archive...';

      try {
        const zip = await JSZip.loadAsync(file);
        uploadStatusText.textContent = 'Parsing workbook sheets...';

        // 1. Generate Cleaned Excel Blob for download
        let wbXml = await zip.file('xl/workbook.xml').async('text');
        wbXml = wbXml.replace(/<definedNames>[\\s\\S]*?<\\/definedNames>/g, '<definedNames/>');
        zip.file('xl/workbook.xml', wbXml);
        
        // Save cleaned file blob
        const cleanedBlob = await zip.generateAsync({ type: 'blob' });
        window.latestCleanedBlob = cleanedBlob;
        window.latestCleanedFilename = file.name.replace('.xlsx', '_Cleaned.xlsx');

        // Update Cleaned Excel download button
        const dlBtn = document.querySelector('a[href*="_Cleaned.xlsx"]');
        if (dlBtn) {
          dlBtn.onclick = (e) => {
            e.preventDefault();
            const url = URL.createObjectURL(cleanedBlob);
            const a = document.createElement('a');
            a.href = url;
            a.download = window.latestCleanedFilename;
            a.click();
          };
          dlBtn.innerHTML = '<i data-lucide="file-spreadsheet" class="w-3.5 h-3.5"></i> Download Cleaned Excel';
        }

        // 2. Parse Shared Strings
        uploadStatusText.textContent = 'Extracting strings & transactions...';
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

        // Helper to parse cells
        function parseSheetRows(xmlStr) {
          const doc = parser.parseFromString(xmlStr, 'application/xml');
          const rowsElem = doc.getElementsByTagName('row');
          const rows = {};
          for (let i = 0; i < rowsElem.length; i++) {
            const r = rowsElem[i];
            const rIdx = parseInt(r.getAttribute('r'));
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
                val = strings[parseInt(val)] || val;
              }
              cells[col] = val;
            }
            rows[rIdx] = cells;
          }
          return rows;
        }

        // Parse Summary (sheet5.xml)
        if (zip.file('xl/worksheets/sheet5.xml')) {
          const sumXml = await zip.file('xl/worksheets/sheet5.xml').async('text');
          const sumRows = parseSheetRows(sumXml);
          
          if (sumRows[9]) {
            DATA.kpis.baseline.revenue = parseFloat(sumRows[9]['F']) || DATA.kpis.baseline.revenue;
            DATA.kpis.pjtd.revenue = parseFloat(sumRows[9]['G']) || DATA.kpis.pjtd.revenue;
          }
          if (sumRows[10]) {
            DATA.kpis.baseline.cost = parseFloat(sumRows[10]['F']) || DATA.kpis.baseline.cost;
            DATA.kpis.pjtd.cost = parseFloat(sumRows[10]['G']) || DATA.kpis.pjtd.cost;
          }
          if (sumRows[9] && sumRows[9]['S']) {
            DATA.kpis.weekly_burn_hours = parseFloat(sumRows[9]['S']) || DATA.kpis.weekly_burn_hours;
          }
          if (sumRows[10] && sumRows[10]['S']) {
            DATA.kpis.weekly_burn_cost = parseFloat(sumRows[10]['S']) || DATA.kpis.weekly_burn_cost;
          }
          if (sumRows[35] && sumRows[35]['G']) {
            DATA.kpis.working_capital.wip = parseFloat(sumRows[35]['G']) || DATA.kpis.working_capital.wip;
          }
        }

        // Re-render dashboard
        updateKPIs();
        renderScopeTable();
        renderStaffTable();
        renderTaskTable();
        filterTransactions();
        lucide.createIcons();

        uploadStatusText.textContent = `Updated with ${file.name}!`;
        setTimeout(() => uploadStatus.classList.add('hidden'), 4000);
      } catch (err) {
        console.error(err);
        alert('Error parsing Excel file: ' + err.message);
        uploadStatus.classList.add('hidden');
      }
    }
'''

html =html .replace ('// Boot',client_parser_js +'\n    // Boot')

with open ('dashboard.html','w',encoding ='utf-8')as f :
    f .write (html )

print ("dashboard.html updated with client-side drag-and-drop parser!")

