import json 

with open ('data/dashboard_data.json','r',encoding ='utf-8')as f :
    data =json .load (f )

json_str =json .dumps (data )

html_template =f'''<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Cost Report Analytics & Visualization Dashboard | SA859CMS</title>
  <!-- Tailwind CSS -->
  <script src="https://cdn.tailwindcss.com"></script>
  <!-- Chart.js -->
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <!-- Lucide Icons -->
  <script src="https://unpkg.com/lucide@latest"></script>
  <script>
    tailwind.config = {{
      darkMode: 'class',
      theme: {{
        extend: {{
          colors: {{
            brand: {{
              50: '#f0fdfa',
              100: '#ccfbf1',
              500: '#14b8a6',
              600: '#0d9488',
              700: '#0f766e',
              900: '#134e4a',
            }},
            darkbg: '#0f172a',
            darkcard: '#1e293b',
            darkborder: '#334155'
          }}
        }}
      }}
    }}
  </script>
  <style>
    /* Custom scrollbar */
    ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
    ::-webkit-scrollbar-track {{ background: #0f172a; }}
    ::-webkit-scrollbar-thumb {{ background: #334155; border-radius: 3px; }}
    ::-webkit-scrollbar-thumb:hover {{ background: #475569; }}
    .tab-active {{
      border-bottom: 2px solid #14b8a6;
      color: #14b8a6;
      font-weight: 600;
    }}
  </style>
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen font-sans transition-colors duration-200">

  <!-- TOP APP BAR -->
  <header class="border-b border-slate-800 bg-slate-900/80 backdrop-blur sticky top-0 z-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3.5 flex flex-wrap items-center justify-between gap-4">
      <div class="flex items-center space-x-3">
        <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-teal-500 to-cyan-400 flex items-center justify-center text-slate-950 shadow-lg shadow-teal-500/20">
          <i data-lucide="bar-chart-3" class="w-6 h-6"></i>
        </div>
        <div>
          <div class="flex items-center space-x-2">
            <h1 class="text-lg font-bold tracking-tight text-white">SA859CMS Cost & Commercial Analytics</h1>
            <span class="text-xs font-semibold px-2 py-0.5 rounded-full bg-teal-500/10 text-teal-400 border border-teal-500/20">Week 13</span>
          </div>
          <p class="text-xs text-slate-400 flex items-center gap-1.5 mt-0.5">
            <i data-lucide="building-2" class="w-3.5 h-3.5"></i>
            50MW Humain Campus Data Center CS &bull; Client: Alistidafa Aldhakiah &bull; WE 30-Oct-2026
          </p>
        </div>
      </div>

      <!-- Quick Actions & Controls -->
      <div class="flex items-center space-x-3 text-sm">
        <!-- Currency Toggle -->
        <div class="flex items-center bg-slate-800 border border-slate-700 rounded-lg p-0.5 text-xs font-medium">
          <button id="btn-curr-sar" onclick="setCurrency('SAR')" class="px-2.5 py-1 rounded bg-teal-500 text-slate-950 font-bold transition">SAR</button>
          <button id="btn-curr-usd" onclick="setCurrency('USD')" class="px-2.5 py-1 rounded text-slate-400 hover:text-white transition">USD</button>
        </div>

        <!-- Export Buttons -->
        <a href="data/transactions.csv" download class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 text-xs font-medium transition">
          <i data-lucide="download" class="w-3.5 h-3.5 text-teal-400"></i>
          Export CSV
        </a>

        <a href="SA859CMS_Cost_Report_Cleaned.xlsx" download class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-teal-600 hover:bg-teal-500 text-slate-950 text-xs font-bold transition shadow-sm">
          <i data-lucide="file-spreadsheet" class="w-3.5 h-3.5"></i>
          Cleaned Excel (4.9MB)
        </a>

        <!-- Dark/Light Toggle -->
        <button onclick="toggleTheme()" class="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white transition">
          <i data-lucide="sun-moon" class="w-4 h-4"></i>
        </button>
      </div>
    </div>
  </header>

  <!-- MAIN CONTAINER -->
  <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">

    <!-- EXECUTIVE KPI ROW -->
    <section class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3.5">
      <!-- PJTD Revenue -->
      <div class="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-sm hover:border-slate-700 transition">
        <div class="flex items-center justify-between text-slate-400 text-xs mb-1">
          <span>PJTD Revenue</span>
          <i data-lucide="wallet" class="w-4 h-4 text-emerald-400"></i>
        </div>
        <div class="text-xl font-bold text-white tracking-tight" id="kpi-pjtd-rev">--</div>
        <div class="text-[11px] text-slate-400 mt-1 flex items-center justify-between">
          <span>Budget: <span id="kpi-base-rev">--</span></span>
          <span class="text-emerald-400 font-semibold" id="kpi-rev-pct">4.7%</span>
        </div>
      </div>

      <!-- PJTD Cost -->
      <div class="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-sm hover:border-slate-700 transition">
        <div class="flex items-center justify-between text-slate-400 text-xs mb-1">
          <span>PJTD Cost</span>
          <i data-lucide="receipt" class="w-4 h-4 text-blue-400"></i>
        </div>
        <div class="text-xl font-bold text-white tracking-tight" id="kpi-pjtd-cost">--</div>
        <div class="text-[11px] text-slate-400 mt-1 flex items-center justify-between">
          <span>Budget: <span id="kpi-base-cost">--</span></span>
          <span class="text-blue-400 font-semibold" id="kpi-cost-pct">4.9%</span>
        </div>
      </div>

      <!-- Gross Margin -->
      <div class="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-sm hover:border-slate-700 transition">
        <div class="flex items-center justify-between text-slate-400 text-xs mb-1">
          <span>PJTD Margin %</span>
          <i data-lucide="trending-up" class="w-4 h-4 text-amber-400"></i>
        </div>
        <div class="flex items-baseline gap-2">
          <span class="text-xl font-bold text-amber-400 tracking-tight" id="kpi-pjtd-gm-pct">28.18%</span>
          <span class="text-xs text-slate-400 line-through" id="kpi-base-gm-pct">30.88%</span>
        </div>
        <div class="text-[11px] text-amber-400/90 mt-1 flex items-center gap-1">
          <i data-lucide="alert-triangle" class="w-3 h-3"></i>
          <span>-2.7% margin erosion</span>
        </div>
      </div>

      <!-- Total Hours -->
      <div class="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-sm hover:border-slate-700 transition">
        <div class="flex items-center justify-between text-slate-400 text-xs mb-1">
          <span>Hours Spent</span>
          <i data-lucide="clock" class="w-4 h-4 text-cyan-400"></i>
        </div>
        <div class="text-xl font-bold text-white tracking-tight" id="kpi-pjtd-hours">3,128 hrs</div>
        <div class="text-[11px] text-slate-400 mt-1 flex items-center justify-between">
          <span>Budget: 70,793</span>
          <span class="text-cyan-400 font-semibold">4.4%</span>
        </div>
      </div>

      <!-- Weekly Burn Rate -->
      <div class="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-sm hover:border-slate-700 transition">
        <div class="flex items-center justify-between text-slate-400 text-xs mb-1">
          <span>Weekly Burn</span>
          <i data-lucide="flame" class="w-4 h-4 text-orange-400"></i>
        </div>
        <div class="text-xl font-bold text-white tracking-tight" id="kpi-weekly-burn-cost">--</div>
        <div class="text-[11px] text-slate-400 mt-1 flex items-center justify-between">
          <span>240.6 hrs/wk</span>
          <span class="text-emerald-400 font-medium">11 On-Site</span>
        </div>
      </div>

      <!-- Working Capital / WIP -->
      <div class="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-sm hover:border-slate-700 transition">
        <div class="flex items-center justify-between text-slate-400 text-xs mb-1">
          <span>Unbilled WIP</span>
          <i data-lucide="landmark" class="w-4 h-4 text-purple-400"></i>
        </div>
        <div class="text-xl font-bold text-purple-300 tracking-tight" id="kpi-wip">--</div>
        <div class="text-[11px] text-slate-400 mt-1 flex items-center justify-between">
          <span>WWOA: 73.8%</span>
          <span class="text-purple-400 font-medium">AR: 0</span>
        </div>
      </div>
    </section>

    <!-- NAVIGATION TABS -->
    <nav class="flex border-b border-slate-800 text-sm font-medium space-x-6 overflow-x-auto">
      <button onclick="switchTab('tab-overview')" id="btn-tab-overview" class="pb-3 tab-active flex items-center gap-2">
        <i data-lucide="layout-dashboard" class="w-4 h-4"></i>
        Executive Overview
      </button>
      <button onclick="switchTab('tab-staff')" id="btn-tab-staff" class="pb-3 text-slate-400 hover:text-slate-200 flex items-center gap-2 transition">
        <i data-lucide="users" class="w-4 h-4"></i>
        Staff & Margin Performance
        <span class="bg-red-500/10 text-red-400 text-[10px] font-bold px-1.5 py-0.5 rounded-full border border-red-500/20" id="badge-neg-margin">6 At Risk</span>
      </button>
      <button onclick="switchTab('tab-tasks')" id="btn-tab-tasks" class="pb-3 text-slate-400 hover:text-slate-200 flex items-center gap-2 transition">
        <i data-lucide="check-square" class="w-4 h-4"></i>
        WBS & Task Code Breakdown
      </button>
      <button onclick="switchTab('tab-finance')" id="btn-tab-finance" class="pb-3 text-slate-400 hover:text-slate-200 flex items-center gap-2 transition">
        <i data-lucide="file-check-2" class="w-4 h-4"></i>
        Contract & WIP Recon
      </button>
      <button onclick="switchTab('tab-transactions')" id="btn-tab-transactions" class="pb-3 text-slate-400 hover:text-slate-200 flex items-center gap-2 transition">
        <i data-lucide="table" class="w-4 h-4"></i>
        Oracle Transactions Explorer
        <span class="bg-teal-500/10 text-teal-400 text-[10px] font-bold px-1.5 py-0.5 rounded-full border border-teal-500/20">4,095 Rows</span>
      </button>
    </nav>

    <!-- TAB 1: EXECUTIVE OVERVIEW -->
    <div id="tab-overview" class="space-y-6">
      <!-- ROW 1 CHARTS: GM Trend + Expenditure Distribution -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- GM Trend (2 cols) -->
        <div class="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm">
          <div class="flex items-center justify-between mb-4">
            <div>
              <h2 class="text-sm font-bold text-white flex items-center gap-2">
                <i data-lucide="trending-down" class="w-4 h-4 text-teal-400"></i>
                Gross Margin Trend (Weekly Actual vs Budget 30.88%)
              </h2>
              <p class="text-xs text-slate-400 mt-0.5">Erosion from 33.28% peak down to 27.22% on WE 30-Oct-2026</p>
            </div>
            <div class="text-xs flex items-center gap-3">
              <span class="flex items-center gap-1.5 text-slate-400"><span class="w-3 h-0.5 bg-dashed bg-slate-400 inline-block"></span> Budget 30.88%</span>
              <span class="flex items-center gap-1.5 text-teal-400"><span class="w-3 h-1 bg-teal-400 rounded-full inline-block"></span> Actual GM %</span>
            </div>
          </div>
          <div class="h-64">
            <canvas id="chart-gm-trend"></canvas>
          </div>
        </div>

        <!-- Regional & Resource Mix (1 col) -->
        <div class="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-sm font-bold text-white flex items-center gap-2">
              <i data-lucide="pie-chart" class="w-4 h-4 text-cyan-400"></i>
              Staff Regional Distribution
            </h2>
          </div>
          <div class="h-52">
            <canvas id="chart-regional"></canvas>
          </div>
          <div class="mt-4 pt-3 border-t border-slate-800 text-xs grid grid-cols-3 text-center">
            <div>
              <span class="text-slate-400 block">Saudi Arabia</span>
              <span class="font-bold text-white" id="reg-sa-hrs">2,805 hrs</span>
            </div>
            <div>
              <span class="text-slate-400 block">UAE (AE)</span>
              <span class="font-bold text-white" id="reg-ae-hrs">127 hrs</span>
            </div>
            <div>
              <span class="text-slate-400 block">UK (UF)</span>
              <span class="font-bold text-white" id="reg-uf-hrs">47 hrs</span>
            </div>
          </div>
        </div>
      </div>

      <!-- ROW 2: Scope Breakdown + Weekly Burn -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Scope Cost vs Revenue -->
        <div class="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm">
          <h2 class="text-sm font-bold text-white flex items-center gap-2 mb-1">
            <i data-lucide="layers" class="w-4 h-4 text-emerald-400"></i>
            PJTD Cost vs Revenue by Scope Category
          </h2>
          <p class="text-xs text-slate-400 mb-4">On-Site Supervision represents 89.6% of project spend</p>
          <div class="h-64">
            <canvas id="chart-scope"></canvas>
          </div>
        </div>

        <!-- Weekly Spend & Hours -->
        <div class="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm">
          <h2 class="text-sm font-bold text-white flex items-center gap-2 mb-1">
            <i data-lucide="calendar" class="w-4 h-4 text-blue-400"></i>
            Weekly Spend Velocity & Hours Logged
          </h2>
          <p class="text-xs text-slate-400 mb-4">Historical weekly billing transactions</p>
          <div class="h-64">
            <canvas id="chart-weekly"></canvas>
          </div>
        </div>
      </div>

      <!-- ROW 3: Scope Breakdown Table -->
      <div class="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm">
        <h2 class="text-sm font-bold text-white flex items-center gap-2 mb-3">
          <i data-lucide="list-checks" class="w-4 h-4 text-teal-400"></i>
          Detailed Scope Budget vs PJTD Actuals
        </h2>
        <div class="overflow-x-auto">
          <table class="w-full text-left text-xs border-collapse">
            <thead>
              <tr class="border-b border-slate-800 text-slate-400 bg-slate-950/50">
                <th class="py-2.5 px-3 font-semibold">Scope Item</th>
                <th class="py-2.5 px-3 font-semibold text-right">Baseline Rev</th>
                <th class="py-2.5 px-3 font-semibold text-right">Baseline Cost</th>
                <th class="py-2.5 px-3 font-semibold text-right">Base GM%</th>
                <th class="py-2.5 px-3 font-semibold text-right text-teal-400">PJTD Rev</th>
                <th class="py-2.5 px-3 font-semibold text-right text-blue-400">PJTD Cost</th>
                <th class="py-2.5 px-3 font-semibold text-right">PJTD GM</th>
                <th class="py-2.5 px-3 font-semibold text-right">PJTD GM%</th>
                <th class="py-2.5 px-3 font-semibold text-center">Status</th>
              </tr>
            </thead>
            <tbody id="table-scope-body" class="divide-y divide-slate-800/60">
              <!-- Dynamically populated -->
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- TAB 2: STAFF & MARGIN PERFORMANCE -->
    <div id="tab-staff" class="hidden space-y-6">
      <!-- ALERT CALLOUT -->
      <div class="bg-amber-950/30 border border-amber-800/40 rounded-xl p-4 flex items-start gap-3.5">
        <div class="p-2 bg-amber-500/10 text-amber-400 rounded-lg shrink-0">
          <i data-lucide="alert-octagon" class="w-5 h-5"></i>
        </div>
        <div>
          <h3 class="text-sm font-bold text-amber-200">Critical Commercial Alert: Staff Margin Erosion</h3>
          <p class="text-xs text-amber-300/80 mt-1 leading-relaxed">
            Several staff and subcontractor resources are generating <strong>negative gross margin</strong> (cost exceeds accrued revenue), pulling overall project margin below the 30.88% baseline target. In particular, Job Shopper personnel (e.g. Radha Rayudu -21.7% GM, Amjad Saeed -21.3% GM) and Jacobs UK subcontracts (-28.9% GM) have hourly burdened costs that exceed the billable rate.
          </p>
        </div>
      </div>

      <!-- Top Staff Chart & Filter Controls -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div class="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm">
          <h2 class="text-sm font-bold text-white flex items-center gap-2 mb-3">
            <i data-lucide="award" class="w-4 h-4 text-teal-400"></i>
            Top 10 Personnel by Burdened Cost & Revenue
          </h2>
          <div class="h-64">
            <canvas id="chart-top-staff"></canvas>
          </div>
        </div>

        <div class="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm flex flex-col justify-between">
          <div>
            <h2 class="text-sm font-bold text-white flex items-center gap-2 mb-3">
              <i data-lucide="filter" class="w-4 h-4 text-cyan-400"></i>
              Resource Filters
            </h2>
            <div class="space-y-3">
              <div>
                <label class="text-xs text-slate-400 block mb-1">Search Staff Name / ID</label>
                <input type="text" id="filter-staff-search" oninput="renderStaffTable()" placeholder="e.g. Nelson, Rayudu, Jacobs..." class="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:border-teal-500 transition">
              </div>
              <div>
                <label class="text-xs text-slate-400 block mb-1">Margin Status</label>
                <select id="filter-staff-margin" onchange="renderStaffTable()" class="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:border-teal-500">
                  <option value="all">All Personnel</option>
                  <option value="negative">Negative Margin Only (&lt; 0%)</option>
                  <option value="positive">Healthy Margin (&gt;= 0%)</option>
                </select>
              </div>
            </div>
          </div>
          <div class="pt-4 border-t border-slate-800 text-xs text-slate-400 space-y-1">
            <div class="flex justify-between">
              <span>Total Deployed Resources:</span>
              <span class="font-bold text-white" id="stat-total-staff">--</span>
            </div>
            <div class="flex justify-between text-red-400">
              <span>Negative Margin Resources:</span>
              <span class="font-bold" id="stat-neg-staff">--</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Staff Table -->
      <div class="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm">
        <h2 class="text-sm font-bold text-white mb-3">Personnel Performance & Profitability Ledger</h2>
        <div class="overflow-x-auto">
          <table class="w-full text-left text-xs border-collapse">
            <thead>
              <tr class="border-b border-slate-800 text-slate-400 bg-slate-950/50">
                <th class="py-2.5 px-3 font-semibold">Employee / Supplier</th>
                <th class="py-2.5 px-3 font-semibold text-right">Hours</th>
                <th class="py-2.5 px-3 font-semibold text-right">Burdened Cost</th>
                <th class="py-2.5 px-3 font-semibold text-right">Accrued Rev</th>
                <th class="py-2.5 px-3 font-semibold text-right">Gross Margin</th>
                <th class="py-2.5 px-3 font-semibold text-right">GM %</th>
                <th class="py-2.5 px-3 font-semibold text-right">Cost/Hr</th>
                <th class="py-2.5 px-3 font-semibold text-right">Rev/Hr</th>
                <th class="py-2.5 px-3 font-semibold text-center">Status</th>
              </tr>
            </thead>
            <tbody id="table-staff-body" class="divide-y divide-slate-800/60">
              <!-- Dynamically populated -->
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- TAB 3: WBS & TASK CODES -->
    <div id="tab-tasks" class="hidden space-y-6">
      <div class="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm">
        <div class="flex flex-wrap items-center justify-between gap-4 mb-4">
          <div>
            <h2 class="text-sm font-bold text-white flex items-center gap-2">
              <i data-lucide="check-square" class="w-4 h-4 text-teal-400"></i>
              WBS Tasks & Position Codes
            </h2>
            <p class="text-xs text-slate-400 mt-0.5">Task code rate realization and spend breakdown</p>
          </div>
          <div>
            <input type="text" id="filter-task-search" oninput="renderTaskTable()" placeholder="Search task code / description..." class="bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:border-teal-500 w-64">
          </div>
        </div>

        <div class="overflow-x-auto">
          <table class="w-full text-left text-xs border-collapse">
            <thead>
              <tr class="border-b border-slate-800 text-slate-400 bg-slate-950/50">
                <th class="py-2.5 px-3 font-semibold">WBS Task Code</th>
                <th class="py-2.5 px-3 font-semibold">Position / Task Description</th>
                <th class="py-2.5 px-3 font-semibold">Category</th>
                <th class="py-2.5 px-3 font-semibold text-right">Hours</th>
                <th class="py-2.5 px-3 font-semibold text-right">Burdened Cost</th>
                <th class="py-2.5 px-3 font-semibold text-right">Revenue</th>
                <th class="py-2.5 px-3 font-semibold text-right">Margin</th>
                <th class="py-2.5 px-3 font-semibold text-right">GM %</th>
                <th class="py-2.5 px-3 font-semibold text-center">Staff Count</th>
              </tr>
            </thead>
            <tbody id="table-task-body" class="divide-y divide-slate-800/60">
              <!-- Dynamically populated -->
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- TAB 4: CONTRACT & WIP RECON -->
    <div id="tab-finance" class="hidden space-y-6">
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Contractual Parameters -->
        <div class="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm space-y-4">
          <h2 class="text-sm font-bold text-white flex items-center gap-2 border-b border-slate-800 pb-3">
            <i data-lucide="file-text" class="w-4 h-4 text-teal-400"></i>
            Contractual Parameters & Terms
          </h2>
          <dl class="space-y-2.5 text-xs">
            <div class="flex justify-between py-1 border-b border-slate-800/60">
              <dt class="text-slate-400">Project Name</dt>
              <dd class="font-semibold text-white">50MW Humain Campus Data Center CS</dd>
            </div>
            <div class="flex justify-between py-1 border-b border-slate-800/60">
              <dt class="text-slate-400">Client</dt>
              <dd class="font-semibold text-white">Alistidafa Aldhakiah Company</dd>
            </div>
            <div class="flex justify-between py-1 border-b border-slate-800/60">
              <dt class="text-slate-400">Project Location</dt>
              <dd class="font-semibold text-white">Riyadh, Saudi Arabia</dd>
            </div>
            <div class="flex justify-between py-1 border-b border-slate-800/60">
              <dt class="text-slate-400">Contract Type</dt>
              <dd class="font-semibold text-white">Time and Material (T&M)</dd>
            </div>
            <div class="flex justify-between py-1 border-b border-slate-800/60">
              <dt class="text-slate-400">Project Duration</dt>
              <dd class="font-semibold text-white">16 Months</dd>
            </div>
            <div class="flex justify-between py-1 border-b border-slate-800/60">
              <dt class="text-slate-400">Payment Terms</dt>
              <dd class="font-semibold text-white">45 days from receipt of invoice</dd>
            </div>
            <div class="flex justify-between py-1 border-b border-slate-800/60">
              <dt class="text-slate-400">Currency & FX Rate</dt>
              <dd class="font-semibold text-white">SAR (1 SAR = 0.2666 USD)</dd>
            </div>
            <div class="flex justify-between py-1">
              <dt class="text-slate-400">Labor Contingency</dt>
              <dd class="font-semibold text-white">1.35% of labor cost as Non-Billable</dd>
            </div>
          </dl>
        </div>

        <!-- WIP & Billing Reconciliation -->
        <div class="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm space-y-4">
          <h2 class="text-sm font-bold text-white flex items-center gap-2 border-b border-slate-800 pb-3">
            <i data-lucide="scale" class="w-4 h-4 text-purple-400"></i>
            WIP & Cash Flow Reconciliation
          </h2>
          <div class="space-y-3">
            <div class="p-3 bg-purple-950/20 border border-purple-800/30 rounded-lg flex items-center justify-between">
              <div>
                <span class="text-xs text-purple-300 block font-medium">Unbilled Revenue (WIP)</span>
                <span class="text-xs text-slate-400">Revenue earned but not yet invoiced</span>
              </div>
              <span class="text-lg font-bold text-purple-200" id="recon-wip">SAR 697,713</span>
            </div>

            <div class="p-3 bg-slate-950 border border-slate-800 rounded-lg flex items-center justify-between">
              <div>
                <span class="text-xs text-slate-300 block font-medium">Billed Revenue & Invoiced</span>
                <span class="text-xs text-slate-400">Invoices issued to client</span>
              </div>
              <span class="text-sm font-bold text-white">SAR 0.00</span>
            </div>

            <div class="p-3 bg-slate-950 border border-slate-800 rounded-lg flex items-center justify-between">
              <div>
                <span class="text-xs text-slate-300 block font-medium">Cash Collected</span>
                <span class="text-xs text-slate-400">Payments received</span>
              </div>
              <span class="text-sm font-bold text-white">SAR 0.00</span>
            </div>

            <div class="p-3 bg-teal-950/20 border border-teal-800/30 rounded-lg">
              <div class="flex items-center justify-between mb-1.5">
                <span class="text-xs font-semibold text-teal-300">WWOA Facility Utilization</span>
                <span class="text-xs font-bold text-teal-300">73.8%</span>
              </div>
              <div class="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                <div class="bg-teal-500 h-full rounded-full" style="width: 73.8%"></div>
              </div>
              <div class="flex justify-between text-[11px] text-slate-400 mt-1.5">
                <span>Spent: SAR 692,231</span>
                <span>Approved Limit: SAR 937,500</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Contingency Reserve Card -->
      <div class="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm">
        <h2 class="text-sm font-bold text-white flex items-center gap-2 mb-3">
          <i data-lucide="shield" class="w-4 h-4 text-blue-400"></i>
          Contingency Reserve Allocation (Baseline Budget: SAR 192,371 / $51,286)
        </h2>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div class="bg-slate-950 p-4 rounded-xl border border-slate-800">
            <span class="text-xs text-slate-400 block">PM Contingency (30%)</span>
            <span class="text-lg font-bold text-white mt-1 block">SAR 57,711.16</span>
            <span class="text-[11px] text-slate-500">$15,385.80 USD &bull; Task: S.PN.S.S.S</span>
          </div>
          <div class="bg-slate-950 p-4 rounded-xl border border-slate-800">
            <span class="text-xs text-slate-400 block">Controlled Contingency 1 (50%)</span>
            <span class="text-lg font-bold text-white mt-1 block">SAR 96,185.27</span>
            <span class="text-[11px] text-slate-500">$25,642.99 USD &bull; Task: S.PN.S.S.CC1</span>
          </div>
          <div class="bg-slate-950 p-4 rounded-xl border border-slate-800">
            <span class="text-xs text-slate-400 block">Controlled Contingency 2 (20%)</span>
            <span class="text-lg font-bold text-white mt-1 block">SAR 38,474.11</span>
            <span class="text-[11px] text-slate-500">$10,257.20 USD &bull; Task: S.PN.S.S.CC2</span>
          </div>
        </div>
      </div>
    </div>

    <!-- TAB 5: ORACLE TRANSACTIONS EXPLORER -->
    <div id="tab-transactions" class="hidden space-y-4">
      <div class="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm">
        <!-- Explorer Header & Filters -->
        <div class="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-slate-800">
          <div>
            <h2 class="text-sm font-bold text-white flex items-center gap-2">
              <i data-lucide="database" class="w-4 h-4 text-teal-400"></i>
              Oracle ERP Raw Transactions Ledger
            </h2>
            <p class="text-xs text-slate-400 mt-0.5">Explore, search, filter and export all 4,095 transaction records</p>
          </div>

          <button onclick="exportFilteredCSV()" class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-teal-600 hover:bg-teal-500 text-slate-950 text-xs font-bold transition">
            <i data-lucide="download" class="w-3.5 h-3.5"></i>
            Export Filtered CSV
          </button>
        </div>

        <!-- Filter Controls Bar -->
        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3 py-4">
          <div>
            <label class="text-[11px] text-slate-400 block mb-1">Global Keyword Search</label>
            <input type="text" id="tx-search" oninput="filterTransactions()" placeholder="Search staff, task, exp type..." class="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:border-teal-500">
          </div>
          <div>
            <label class="text-[11px] text-slate-400 block mb-1">Project Filter</label>
            <select id="tx-project" onchange="filterTransactions()" class="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:border-teal-500">
              <option value="all">All Projects</option>
              <option value="SA859CMS">SA859CMS</option>
              <option value="SA859JUK">SA859JUK</option>
            </select>
          </div>
          <div>
            <label class="text-[11px] text-slate-400 block mb-1">Expenditure Type</label>
            <select id="tx-exp-type" onchange="filterTransactions()" class="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:border-teal-500">
              <option value="all">All Expenditure Types</option>
              <option value="Pro-Service ST">Pro-Service ST</option>
              <option value="Job Shopper P/S ST">Job Shopper P/S ST</option>
              <option value="Subcontract Cost">Subcontract Cost</option>
              <option value="Pro-Service SPOT">Pro-Service SPOT</option>
              <option value="Job Shopper P/S SPOT">Job Shopper P/S SPOT</option>
              <option value="Vehicle-Fuel">Vehicle-Fuel</option>
            </select>
          </div>
          <div>
            <label class="text-[11px] text-slate-400 block mb-1">Billable Status</label>
            <select id="tx-billable" onchange="filterTransactions()" class="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:border-teal-500">
              <option value="all">All</option>
              <option value="Y">Billable (Y)</option>
              <option value="N">Non-Billable (N)</option>
            </select>
          </div>
        </div>

        <!-- Filtered Dynamic Stats Bar -->
        <div class="flex flex-wrap items-center justify-between gap-4 py-2.5 px-4 bg-slate-950 rounded-lg text-xs border border-slate-800/80">
          <div class="flex items-center gap-4 text-slate-400">
            <span>Matching Records: <strong class="text-white" id="tx-stat-count">0</strong></span>
            <span>Total Hours: <strong class="text-cyan-400" id="tx-stat-hours">0</strong></span>
            <span>Total Burdened Cost: <strong class="text-blue-400" id="tx-stat-cost">SAR 0</strong></span>
            <span>Total Revenue: <strong class="text-teal-400" id="tx-stat-rev">SAR 0</strong></span>
          </div>

          <div class="flex items-center gap-2">
            <span class="text-slate-400">Rows per page:</span>
            <select id="tx-page-size" onchange="changePageSize()" class="bg-slate-900 border border-slate-800 rounded px-2 py-0.5 text-xs text-white">
              <option value="25">25</option>
              <option value="50" selected>50</option>
              <option value="100">100</option>
              <option value="250">250</option>
            </select>
          </div>
        </div>

        <!-- Transactions Table -->
        <div class="overflow-x-auto mt-4">
          <table class="w-full text-left text-xs border-collapse">
            <thead>
              <tr class="border-b border-slate-800 text-slate-400 bg-slate-950/60">
                <th class="py-2 px-2.5">ID</th>
                <th class="py-2 px-2.5">Date</th>
                <th class="py-2 px-2.5">Project</th>
                <th class="py-2 px-2.5">Task Code</th>
                <th class="py-2 px-2.5">Employee / Supplier</th>
                <th class="py-2 px-2.5">Expenditure Type</th>
                <th class="py-2 px-2.5 text-right">Qty (Hrs)</th>
                <th class="py-2 px-2.5 text-right">Burdened Cost</th>
                <th class="py-2 px-2.5 text-right">Revenue</th>
                <th class="py-2 px-2.5 text-right">Margin</th>
                <th class="py-2 px-2.5 text-center">Billable</th>
              </tr>
            </thead>
            <tbody id="table-tx-body" class="divide-y divide-slate-800/50">
              <!-- Dynamically populated -->
            </tbody>
          </table>
        </div>

        <!-- Pagination Controls -->
        <div class="flex items-center justify-between pt-4 border-t border-slate-800 text-xs">
          <span class="text-slate-400" id="tx-page-info">Showing 1 to 50 of 4,095</span>
          <div class="flex items-center gap-2">
            <button id="btn-tx-prev" onclick="changePage(-1)" class="px-3 py-1.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 font-medium disabled:opacity-40 disabled:cursor-not-allowed">Previous</button>
            <button id="btn-tx-next" onclick="changePage(1)" class="px-3 py-1.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 font-medium disabled:opacity-40 disabled:cursor-not-allowed">Next</button>
          </div>
        </div>
      </div>
    </div>
  </main>

  <!-- DATA & APP LOGIC -->
  <script>
    // Embedded Data Payload
    const DATA = {json_str };

    let currentCurrency = 'SAR';
    const fxRate = DATA.kpis.usd_fx_rate || 0.2666;

    function formatMoney(amount, curr = currentCurrency) {{
      if (amount === null || amount === undefined || isNaN(amount)) return '--';
      const val = curr === 'USD' ? (amount * fxRate) : amount;
      const prefix = curr === 'USD' ? '$' : 'SAR ';
      return prefix + Number(val).toLocaleString(undefined, {{
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
      }});
    }}

    function formatMoneyExact(amount, curr = currentCurrency) {{
      if (amount === null || amount === undefined || isNaN(amount)) return '--';
      const val = curr === 'USD' ? (amount * fxRate) : amount;
      const prefix = curr === 'USD' ? '$' : 'SAR ';
      return prefix + Number(val).toLocaleString(undefined, {{
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      }});
    }}

    function setCurrency(curr) {{
      currentCurrency = curr;
      document.getElementById('btn-curr-sar').className = curr === 'SAR' 
        ? 'px-2.5 py-1 rounded bg-teal-500 text-slate-950 font-bold transition'
        : 'px-2.5 py-1 rounded text-slate-400 hover:text-white transition';
      document.getElementById('btn-curr-usd').className = curr === 'USD' 
        ? 'px-2.5 py-1 rounded bg-teal-500 text-slate-950 font-bold transition'
        : 'px-2.5 py-1 rounded text-slate-400 hover:text-white transition';

      updateKPIs();
      renderScopeTable();
      renderStaffTable();
      renderTaskTable();
      filterTransactions();
    }}

    function toggleTheme() {{
      const html = document.documentElement;
      html.classList.toggle('dark');
    }}

    function switchTab(tabId) {{
      const tabs = ['tab-overview', 'tab-staff', 'tab-tasks', 'tab-finance', 'tab-transactions'];
      tabs.forEach(t => {{
        const el = document.getElementById(t);
        const btn = document.getElementById('btn-' + t);
        if (t === tabId) {{
          el.classList.remove('hidden');
          btn.className = 'pb-3 tab-active flex items-center gap-2';
        }} else {{
          el.classList.add('hidden');
          btn.className = 'pb-3 text-slate-400 hover:text-slate-200 flex items-center gap-2 transition';
        }}
      }});
      lucide.createIcons();
    }}

    function updateKPIs() {{
      const k = DATA.kpis;
      document.getElementById('kpi-pjtd-rev').textContent = formatMoney(k.pjtd.revenue);
      document.getElementById('kpi-base-rev').textContent = formatMoney(k.baseline.revenue);
      document.getElementById('kpi-pjtd-cost').textContent = formatMoney(k.pjtd.cost);
      document.getElementById('kpi-base-cost').textContent = formatMoney(k.baseline.cost);
      document.getElementById('kpi-weekly-burn-cost').textContent = formatMoney(k.weekly_burn_cost);
      document.getElementById('kpi-wip').textContent = formatMoney(k.working_capital.wip);
      document.getElementById('recon-wip').textContent = formatMoney(k.working_capital.wip);
    }}

    // Render Scope Breakdown Table
    function renderScopeTable() {{
      const tbody = document.getElementById('table-scope-body');
      tbody.innerHTML = '';
      DATA.scope_items.forEach(item => {{
        const tr = document.createElement('tr');
        tr.className = 'hover:bg-slate-800/40 transition';
        const gmClass = item.pjtd_gm < 0 ? 'text-red-400 font-semibold' : 'text-slate-300';
        const statusBadge = item.pjtd_gm < 0 
          ? '<span class="px-2 py-0.5 rounded text-[10px] bg-red-500/10 text-red-400 border border-red-500/20">Over Budget</span>'
          : '<span class="px-2 py-0.5 rounded text-[10px] bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">On Track</span>';

        tr.innerHTML = `
          <td class="py-2 px-3 font-medium text-white">${{item.name}} <span class="text-slate-500 text-[10px]">(${{item.code}})</span></td>
          <td class="py-2 px-3 text-right text-slate-400">${{formatMoney(item.baseline_revenue)}}</td>
          <td class="py-2 px-3 text-right text-slate-400">${{formatMoney(item.baseline_cost)}}</td>
          <td class="py-2 px-3 text-right text-slate-400">${{item.baseline_gm_pct.toFixed(1)}}%</td>
          <td class="py-2 px-3 text-right text-teal-400 font-medium">${{formatMoney(item.pjtd_revenue)}}</td>
          <td class="py-2 px-3 text-right text-blue-400 font-medium">${{formatMoney(item.pjtd_cost)}}</td>
          <td class="py-2 px-3 text-right ${{gmClass}}">${{formatMoney(item.pjtd_gm)}}</td>
          <td class="py-2 px-3 text-right font-medium ${{item.pjtd_gm_pct < 0 ? 'text-red-400' : 'text-slate-300'}}">${{item.pjtd_gm_pct.toFixed(1)}}%</td>
          <td class="py-2 px-3 text-center">${{statusBadge}}</td>
        `;
        tbody.appendChild(tr);
      }});
    }}

    // Render Staff Table
    function renderStaffTable() {{
      const query = (document.getElementById('filter-staff-search')?.value || '').toLowerCase();
      const marginFilter = document.getElementById('filter-staff-margin')?.value || 'all';
      const tbody = document.getElementById('table-staff-body');
      tbody.innerHTML = '';

      let totalStaff = DATA.staff_analytics.length;
      let negStaff = 0;

      DATA.staff_analytics.forEach(s => {{
        if (s.margin < -100) negStaff++;

        const matchesQuery = !query || s.name.toLowerCase().includes(query) || (s.emp_id && s.emp_id.includes(query));
        let matchesMargin = true;
        if (marginFilter === 'negative') matchesMargin = s.margin < 0;
        if (marginFilter === 'positive') matchesMargin = s.margin >= 0;

        if (!matchesQuery || !matchesMargin) return;

        const tr = document.createElement('tr');
        tr.className = 'hover:bg-slate-800/40 transition';
        const isNeg = s.margin < 0;
        const statusBadge = isNeg 
          ? '<span class="px-2 py-0.5 rounded text-[10px] bg-red-500/10 text-red-400 border border-red-500/20 font-semibold">Margin Loss</span>'
          : '<span class="px-2 py-0.5 rounded text-[10px] bg-teal-500/10 text-teal-400 border border-teal-500/20">Positive</span>';

        tr.innerHTML = `
          <td class="py-2 px-3 font-medium text-white">
            ${{s.name}}
            <span class="text-slate-500 block text-[10px]">ID: ${{s.emp_id || 'N/A'}} &bull; ${{s.tasks_count}} Tasks</span>
          </td>
          <td class="py-2 px-3 text-right font-mono">${{s.total_hours.toLocaleString()}}</td>
          <td class="py-2 px-3 text-right text-blue-400 font-medium">${{formatMoneyExact(s.burdened_cost)}}</td>
          <td class="py-2 px-3 text-right text-teal-400 font-medium">${{formatMoneyExact(s.revenue)}}</td>
          <td class="py-2 px-3 text-right font-semibold ${{isNeg ? 'text-red-400' : 'text-emerald-400'}}">${{formatMoneyExact(s.margin)}}</td>
          <td class="py-2 px-3 text-right font-bold ${{isNeg ? 'text-red-400' : 'text-slate-200'}}">${{s.margin_pct.toFixed(1)}}%</td>
          <td class="py-2 px-3 text-right text-slate-400 font-mono">${{formatMoneyExact(s.avg_hourly_cost)}}</td>
          <td class="py-2 px-3 text-right text-slate-400 font-mono">${{formatMoneyExact(s.avg_hourly_rev)}}</td>
          <td class="py-2 px-3 text-center">${{statusBadge}}</td>
        `;
        tbody.appendChild(tr);
      }});

      document.getElementById('stat-total-staff').textContent = totalStaff;
      document.getElementById('stat-neg-staff').textContent = negStaff;
      document.getElementById('badge-neg-margin').textContent = `${{negStaff}} At Risk`;
    }}

    // Render Task Table
    function renderTaskTable() {{
      const query = (document.getElementById('filter-task-search')?.value || '').toLowerCase();
      const tbody = document.getElementById('table-task-body');
      tbody.innerHTML = '';

      DATA.task_analytics.forEach(t => {{
        const matchesQuery = !query || t.task_code.toLowerCase().includes(query) || (t.description && t.description.toLowerCase().includes(query));
        if (!matchesQuery) return;

        const tr = document.createElement('tr');
        tr.className = 'hover:bg-slate-800/40 transition';
        const isNeg = t.margin < 0;

        tr.innerHTML = `
          <td class="py-2 px-3 font-mono font-medium text-teal-400">${{t.task_code}}</td>
          <td class="py-2 px-3 text-white max-w-xs truncate" title="${{t.description}}">${{t.description}}</td>
          <td class="py-2 px-3 text-slate-400">${{t.category}}</td>
          <td class="py-2 px-3 text-right font-mono">${{t.total_hours.toLocaleString()}}</td>
          <td class="py-2 px-3 text-right text-blue-400 font-medium">${{formatMoneyExact(t.burdened_cost)}}</td>
          <td class="py-2 px-3 text-right text-teal-400 font-medium">${{formatMoneyExact(t.revenue)}}</td>
          <td class="py-2 px-3 text-right font-semibold ${{isNeg ? 'text-red-400' : 'text-emerald-400'}}">${{formatMoneyExact(t.margin)}}</td>
          <td class="py-2 px-3 text-right font-bold ${{isNeg ? 'text-red-400' : 'text-slate-200'}}">${{t.margin_pct.toFixed(1)}}%</td>
          <td class="py-2 px-3 text-center text-slate-400">${{t.staff_count}}</td>
        `;
        tbody.appendChild(tr);
      }});
    }}

    // Transactions Explorer Logic
    let filteredTransactions = [...DATA.transactions];
    let currentPage = 1;
    let pageSize = 50;

    function filterTransactions() {{
      const query = (document.getElementById('tx-search')?.value || '').toLowerCase();
      const proj = document.getElementById('tx-project')?.value || 'all';
      const exp = document.getElementById('tx-exp-type')?.value || 'all';
      const bill = document.getElementById('tx-billable')?.value || 'all';

      let sumHrs = 0;
      let sumCost = 0;
      let sumRev = 0;

      filteredTransactions = DATA.transactions.filter(t => {{
        if (proj !== 'all' && t.project !== proj) return false;
        if (exp !== 'all' && t.exp_type !== exp) return false;
        if (bill !== 'all' && t.billable !== bill) return false;
        if (query) {{
          const str = `${{t.employee}} ${{t.task}} ${{t.exp_type}} ${{t.item_date}} ${{t.task_desc}}`.toLowerCase();
          if (!str.includes(query)) return false;
        }}
        sumHrs += t.qty;
        sumCost += t.burdened_cost;
        sumRev += t.revenue;
        return true;
      }});

      document.getElementById('tx-stat-count').textContent = filteredTransactions.length.toLocaleString();
      document.getElementById('tx-stat-hours').textContent = sumHrs.toLocaleString(undefined, {{minimumFractionDigits: 1, maximumFractionDigits: 1}});
      document.getElementById('tx-stat-cost').textContent = formatMoney(sumCost);
      document.getElementById('tx-stat-rev').textContent = formatMoney(sumRev);

      currentPage = 1;
      renderTransactionPage();
    }}

    function changePageSize() {{
      pageSize = parseInt(document.getElementById('tx-page-size').value);
      currentPage = 1;
      renderTransactionPage();
    }}

    function changePage(delta) {{
      const maxPages = Math.ceil(filteredTransactions.length / pageSize) || 1;
      currentPage = Math.max(1, Math.min(maxPages, currentPage + delta));
      renderTransactionPage();
    }}

    function renderTransactionPage() {{
      const tbody = document.getElementById('table-tx-body');
      tbody.innerHTML = '';

      const total = filteredTransactions.length;
      const start = (currentPage - 1) * pageSize;
      const end = Math.min(start + pageSize, total);
      const pageRows = filteredTransactions.slice(start, end);

      pageRows.forEach(t => {{
        const tr = document.createElement('tr');
        tr.className = 'hover:bg-slate-800/40 transition font-mono text-[11px]';
        const isNeg = t.margin < 0;

        tr.innerHTML = `
          <td class="py-1.5 px-2.5 text-slate-500">${{t.id}}</td>
          <td class="py-1.5 px-2.5 text-slate-300 font-sans">${{t.item_date || 'N/A'}}</td>
          <td class="py-1.5 px-2.5"><span class="px-1.5 py-0.5 rounded bg-slate-800 text-teal-400 text-[10px]">${{t.project}}</span></td>
          <td class="py-1.5 px-2.5 text-slate-300" title="${{t.task_desc}}">${{t.task}}</td>
          <td class="py-1.5 px-2.5 text-white font-sans font-medium max-w-[180px] truncate" title="${{t.employee}}">${{t.employee}}</td>
          <td class="py-1.5 px-2.5 text-slate-400 font-sans text-[10px]">${{t.exp_type}}</td>
          <td class="py-1.5 px-2.5 text-right font-bold text-white">${{t.qty.toFixed(1)}}</td>
          <td class="py-1.5 px-2.5 text-right text-blue-400">${{formatMoneyExact(t.burdened_cost)}}</td>
          <td class="py-1.5 px-2.5 text-right text-teal-400">${{formatMoneyExact(t.revenue)}}</td>
          <td class="py-1.5 px-2.5 text-right font-medium ${{isNeg ? 'text-red-400' : 'text-emerald-400'}}">${{formatMoneyExact(t.margin)}}</td>
          <td class="py-1.5 px-2.5 text-center"><span class="px-1 py-0.5 rounded text-[10px] ${{t.billable === 'Y' ? 'bg-teal-500/10 text-teal-400' : 'bg-slate-800 text-slate-400'}}">${{t.billable}}</span></td>
        `;
        tbody.appendChild(tr);
      }});

      document.getElementById('tx-page-info').textContent = total === 0 ? 'No matching records' : `Showing ${{start + 1}} to ${{end}} of ${{total.toLocaleString()}}`;
      document.getElementById('btn-tx-prev').disabled = currentPage <= 1;
      document.getElementById('btn-tx-next').disabled = end >= total;
    }}

    function exportFilteredCSV() {{
      if (filteredTransactions.length === 0) {{
        alert('No records to export');
        return;
      }}
      const keys = Object.keys(filteredTransactions[0]);
      let csvContent = 'data:text/csv;charset=utf-8,' + keys.join(',') + '\\n';
      filteredTransactions.forEach(row => {{
        const vals = keys.map(k => `"${{String(row[k] || '').replace(/"/g, '""')}}"`);
        csvContent += vals.join(',') + '\\n';
      }});
      const encodedUri = encodeURI(csvContent);
      const link = document.createElement('a');
      link.setAttribute('href', encodedUri);
      link.setAttribute('download', `Oracle_Transactions_Filtered_${{new Date().toISOString().slice(0,10)}}.csv`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }}

    // Initialize Charts
    function initCharts() {{
      Chart.defaults.color = '#94a3b8';
      Chart.defaults.borderColor = '#1e293b';

      // 1. GM Trend Line Chart
      const gmCtx = document.getElementById('chart-gm-trend').getContext('2d');
      const weeks = DATA.gm_trend.map(g => `W${{g.week}} (${{g.date.slice(5)}})`);
      const budgetGm = DATA.gm_trend.map(g => g.budget_gm_pct);
      const actualGm = DATA.gm_trend.map(g => g.actual_gm_pct);

      new Chart(gmCtx, {{
        type: 'line',
        data: {{
          labels: weeks,
          datasets: [
            {{
              label: 'Budget GM %',
              data: budgetGm,
              borderColor: '#64748b',
              borderDash: [5, 5],
              borderWidth: 2,
              fill: false,
              pointRadius: 0
            }},
            {{
              label: 'Actual GM %',
              data: actualGm,
              borderColor: '#14b8a6',
              backgroundColor: 'rgba(20, 184, 166, 0.1)',
              borderWidth: 3,
              fill: true,
              pointBackgroundColor: '#14b8a6',
              pointRadius: 4,
              tension: 0.3
            }}
          ]
        }},
        options: {{
          responsive: true,
          maintainAspectRatio: false,
          plugins: {{
            legend: {{ display: false }},
            tooltip: {{
              callbacks: {{
                label: ctx => `${{ctx.dataset.label}}: ${{ctx.raw ? ctx.raw.toFixed(2) + '%' : 'N/A'}}`
              }}
            }}
          }},
          scales: {{
            y: {{
              min: 24,
              max: 36,
              ticks: {{ callback: v => v + '%' }}
            }}
          }}
        }}
      }});

      // 2. Regional Donut
      const regCtx = document.getElementById('chart-regional').getContext('2d');
      new Chart(regCtx, {{
        type: 'doughnut',
        data: {{
          labels: ['Saudi Arabia (SA)', 'UAE (AE)', 'UK (UF)'],
          datasets: [{{
            data: [2805, 127, 47],
            backgroundColor: ['#14b8a6', '#0ea5e9', '#8b5cf6'],
            borderWidth: 0
          }}]
        }},
        options: {{
          responsive: true,
          maintainAspectRatio: false,
          plugins: {{
            legend: {{ position: 'bottom', labels: {{ boxWidth: 10, font: {{ size: 10 }} }} }}
          }}
        }}
      }});

      // 3. Scope Bar Chart
      const scopeCtx = document.getElementById('chart-scope').getContext('2d');
      const activeScopes = DATA.scope_items.filter(s => s.pjtd_cost > 0 || s.baseline_cost > 0).slice(0, 5);
      new Chart(scopeCtx, {{
        type: 'bar',
        data: {{
          labels: activeScopes.map(s => s.name),
          datasets: [
            {{
              label: 'PJTD Revenue',
              data: activeScopes.map(s => s.pjtd_revenue),
              backgroundColor: '#14b8a6',
              borderRadius: 4
            }},
            {{
              label: 'PJTD Cost',
              data: activeScopes.map(s => s.pjtd_cost),
              backgroundColor: '#3b82f6',
              borderRadius: 4
            }}
          ]
        }},
        options: {{
          responsive: true,
          maintainAspectRatio: false,
          plugins: {{
            legend: {{ position: 'top', labels: {{ boxWidth: 12, font: {{ size: 11 }} }} }},
            tooltip: {{
              callbacks: {{
                label: ctx => `${{ctx.dataset.label}}: ${{formatMoney(ctx.raw)}}`
              }}
            }}
          }},
          scales: {{
            y: {{
              ticks: {{ callback: v => formatMoney(v) }}
            }}
          }}
        }}
      }});

      // 4. Weekly Spend Velocity
      const weeklyCtx = document.getElementById('chart-weekly').getContext('2d');
      const recentWeeks = DATA.weekly_series.slice(-10);
      new Chart(weeklyCtx, {{
        type: 'bar',
        data: {{
          labels: recentWeeks.map(w => w.week_start),
          datasets: [
            {{
              type: 'line',
              label: 'Hours Logged',
              data: recentWeeks.map(w => w.hours),
              borderColor: '#06b6d4',
              borderWidth: 2,
              yAxisID: 'y1',
              pointRadius: 3
            }},
            {{
              type: 'bar',
              label: 'Burdened Cost',
              data: recentWeeks.map(w => w.cost),
              backgroundColor: 'rgba(59, 130, 246, 0.7)',
              borderRadius: 4,
              yAxisID: 'y'
            }}
          ]
        }},
        options: {{
          responsive: true,
          maintainAspectRatio: false,
          plugins: {{
            legend: {{ position: 'top', labels: {{ boxWidth: 10, font: {{ size: 10 }} }} }}
          }},
          scales: {{
            y: {{
              position: 'left',
              ticks: {{ callback: v => formatMoney(v) }}
            }},
            y1: {{
              position: 'right',
              grid: {{ drawOnChartArea: false }},
              ticks: {{ callback: v => v + ' hrs' }}
            }}
          }}
        }}
      }});

      // 5. Top Staff Chart
      const topStaffCtx = document.getElementById('chart-top-staff').getContext('2d');
      const top10 = DATA.staff_analytics.slice(0, 8);
      new Chart(topStaffCtx, {{
        type: 'bar',
        data: {{
          labels: top10.map(s => s.name.split(',')[0]),
          datasets: [
            {{
              label: 'Burdened Cost',
              data: top10.map(s => s.burdened_cost),
              backgroundColor: '#ef4444',
              borderRadius: 4
            }},
            {{
              label: 'Accrued Revenue',
              data: top10.map(s => s.revenue),
              backgroundColor: '#10b981',
              borderRadius: 4
            }}
          ]
        }},
        options: {{
          responsive: true,
          maintainAspectRatio: false,
          plugins: {{
            legend: {{ position: 'top', labels: {{ boxWidth: 10, font: {{ size: 10 }} }} }},
            tooltip: {{
              callbacks: {{
                label: ctx => `${{ctx.dataset.label}}: ${{formatMoney(ctx.raw)}}`
              }}
            }}
          }},
          scales: {{
            y: {{
              ticks: {{ callback: v => formatMoney(v) }}
            }}
          }}
        }}
      }});
    }}

    // Boot
    window.addEventListener('DOMContentLoaded', () => {{
      updateKPIs();
      renderScopeTable();
      renderStaffTable();
      renderTaskTable();
      filterTransactions();
      initCharts();
      lucide.createIcons();
    }});
  </script>
</body>
</html>
'''

import os 
import time 

tmp_html ='dashboard.html.tmp'
with open (tmp_html ,'w',encoding ='utf-8')as f :
    f .write (html_template )

dst_html ='dashboard.html'
for _ in range (5 ):
    try :
        if os .path .exists (dst_html ):
            os .remove (dst_html )
        os .replace (tmp_html ,dst_html )
        break 
    except OSError :
        time .sleep (0.5 )

print ("Created dashboard.html successfully!")
