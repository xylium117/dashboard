window.ChartsManager = (function() {
  let chartGmTrend = null;
  let chartRegional = null;
  let chartScope = null;
  let chartWeekly = null;
  let chartTopStaff = null;

  function destroyAll() {
    [chartGmTrend, chartRegional, chartScope, chartWeekly, chartTopStaff].forEach(c => {
      if (c) {
        try { c.destroy(); } catch(e) {}
      }
    });
    chartGmTrend = null;
    chartRegional = null;
    chartScope = null;
    chartWeekly = null;
    chartTopStaff = null;
  }

  function init(data) {
    destroyAll();
    if (!data) return;

    const isDark = document.documentElement.classList.contains('dark');
    Chart.defaults.color = isDark ? '#94a3b8' : '#64748b';
    Chart.defaults.borderColor = isDark ? '#1e293b' : '#e2e8f0';

    const gmCanvas = document.getElementById('chart-gm-trend');
    if (gmCanvas && data.gm_trend && data.gm_trend.length > 0) {
      const weeks = data.gm_trend.map(g => `W${g.week} (${g.date ? g.date.slice(5) : ''})`);
      const budgetGm = data.gm_trend.map(g => g.budget_gm_pct);
      const actualGm = data.gm_trend.map(g => g.actual_gm_pct);

      chartGmTrend = new Chart(gmCanvas.getContext('2d'), {
        type: 'line',
        data: {
          labels: weeks,
          datasets: [
            {
              label: 'Budget GM %',
              data: budgetGm,
              borderColor: isDark ? '#64748b' : '#94a3b8',
              borderDash: [5, 5],
              borderWidth: 2,
              fill: false,
              pointRadius: 0
            },
            {
              label: 'Actual GM %',
              data: actualGm,
              borderColor: '#14b8a6',
              backgroundColor: 'rgba(20, 184, 166, 0.1)',
              borderWidth: 3,
              fill: true,
              pointBackgroundColor: '#14b8a6',
              pointRadius: 4,
              tension: 0.3
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
            tooltip: {
              callbacks: {
                label: ctx => `${ctx.dataset.label}: ${ctx.raw !== null ? ctx.raw.toFixed(2) + '%' : 'N/A'}`
              }
            }
          },
          scales: {
            y: {
              min: 24,
              max: 36,
              ticks: { callback: v => v + '%' }
            }
          }
        }
      });
    }

    const regCanvas = document.getElementById('chart-regional');
    if (regCanvas) {
      chartRegional = new Chart(regCanvas.getContext('2d'), {
        type: 'doughnut',
        data: {
          labels: ['Saudi Arabia (SA)', 'UAE (AE)', 'UK (UF)'],
          datasets: [{
            data: [2805, 127, 47],
            backgroundColor: ['#14b8a6', '#0ea5e9', '#8b5cf6'],
            borderWidth: 0
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { position: 'bottom', labels: { boxWidth: 10, font: { size: 10 } } }
          }
        }
      });
    }

    const scopeCanvas = document.getElementById('chart-scope');
    if (scopeCanvas && data.scope_items) {
      const activeScopes = data.scope_items.filter(s => s.pjtd_cost > 0 || s.baseline_cost > 0).slice(0, 5);
      chartScope = new Chart(scopeCanvas.getContext('2d'), {
        type: 'bar',
        data: {
          labels: activeScopes.map(s => s.name),
          datasets: [
            {
              label: 'PJTD Revenue',
              data: activeScopes.map(s => s.pjtd_revenue),
              backgroundColor: '#14b8a6',
              borderRadius: 4
            },
            {
              label: 'PJTD Cost',
              data: activeScopes.map(s => s.pjtd_cost),
              backgroundColor: '#3b82f6',
              borderRadius: 4
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { position: 'top', labels: { boxWidth: 12, font: { size: 11 } } },
            tooltip: {
              callbacks: {
                label: ctx => `${ctx.dataset.label}: ${window.App ? window.App.formatMoney(ctx.raw) : ctx.raw}`
              }
            }
          },
          scales: {
            y: {
              ticks: { callback: v => window.App ? window.App.formatMoney(v) : v }
            }
          }
        }
      });
    }

    const weeklyCanvas = document.getElementById('chart-weekly');
    if (weeklyCanvas && data.weekly_series) {
      const recentWeeks = data.weekly_series.slice(-10);
      chartWeekly = new Chart(weeklyCanvas.getContext('2d'), {
        type: 'bar',
        data: {
          labels: recentWeeks.map(w => w.week_start),
          datasets: [
            {
              type: 'line',
              label: 'Hours Logged',
              data: recentWeeks.map(w => w.hours),
              borderColor: '#06b6d4',
              borderWidth: 2,
              yAxisID: 'y1',
              pointRadius: 3
            },
            {
              type: 'bar',
              label: 'Burdened Cost',
              data: recentWeeks.map(w => w.cost),
              backgroundColor: 'rgba(59, 130, 246, 0.7)',
              borderRadius: 4,
              yAxisID: 'y'
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { position: 'top', labels: { boxWidth: 10, font: { size: 10 } } }
          },
          scales: {
            y: {
              position: 'left',
              ticks: { callback: v => window.App ? window.App.formatMoney(v) : v }
            },
            y1: {
              position: 'right',
              grid: { drawOnChartArea: false },
              ticks: { callback: v => v + ' hrs' }
            }
          }
        }
      });
    }

    const staffCanvas = document.getElementById('chart-top-staff');
    if (staffCanvas && data.staff_analytics) {
      const top10 = data.staff_analytics.slice(0, 8);
      chartTopStaff = new Chart(staffCanvas.getContext('2d'), {
        type: 'bar',
        data: {
          labels: top10.map(s => s.name.split(',')[0]),
          datasets: [
            {
              label: 'Burdened Cost',
              data: top10.map(s => s.burdened_cost),
              backgroundColor: '#ef4444',
              borderRadius: 4
            },
            {
              label: 'Accrued Revenue',
              data: top10.map(s => s.revenue),
              backgroundColor: '#10b981',
              borderRadius: 4
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { position: 'top', labels: { boxWidth: 10, font: { size: 10 } } },
            tooltip: {
              callbacks: {
                label: ctx => `${ctx.dataset.label}: ${window.App ? window.App.formatMoney(ctx.raw) : ctx.raw}`
              }
            }
          },
          scales: {
            y: {
              ticks: { callback: v => window.App ? window.App.formatMoney(v) : v }
            }
          }
        }
      });
    }
  }

  return {
    init,
    destroyAll
  };
})();
