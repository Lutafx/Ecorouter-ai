// ============================================
// EcoRouter AI Dashboard — Frontend JS
// ============================================

const API_BASE = window.location.origin;
let modelChart = null;
let complexityChart = null;
let timeChart = null;

// ============================================
// INIT
// ============================================
document.addEventListener('DOMContentLoaded', () => {
    refreshStats();
    setInterval(refreshStats, 5000); // auto-refresh every 5s
    updateCodeSnippet();
    updateDashboardNav();
});

// ============================================
// AUTH-AWARE NAV
// ============================================
function updateDashboardNav() {
    const user = JSON.parse(localStorage.getItem('eco_user') || 'null');
    const navReg = document.getElementById('navReg');
    if (!navReg) return;
    if (user) {
        navReg.textContent = user.contactName || user.companyName || 'Account';
        navReg.href = '/login.html';
        navReg.title = user.email || '';
    }
}

// ============================================
// FETCH STATS & UPDATE UI
// ============================================
async function refreshStats() {
    try {
        const [statsRes, hourlyRes] = await Promise.all([
            fetch(`${API_BASE}/api/stats`),
            fetch(`${API_BASE}/api/stats/hourly`)
        ]);

        const stats = await statsRes.json();
        const hourly = await hourlyRes.json();

        updateStatCards(stats);
        updateEquivalents(stats.equivalents);
        updateModelChart(stats.modelBreakdown);
        updateComplexityChart(stats.complexityBreakdown);
        updateTimeChart(hourly);
        updateRequestsTable(stats.recentRequests);
        updateESG(stats);
    } catch (err) {
        console.error('Failed to fetch stats:', err);
    }
}

// ============================================
// STAT CARDS
// ============================================
function updateStatCards(stats) {
    animateValue('totalRequests', stats.totalRequests);
    document.getElementById('co2Saved').textContent = formatCO2(stats.totalCo2Saved);
    document.getElementById('waterSaved').textContent = formatWater(stats.totalWaterSaved);
    document.getElementById('moneySaved').textContent = '$' + stats.totalMoneySaved.toFixed(2);
    
    // Update hero stats
    animateValue('heroRequests', stats.totalRequests);
    document.getElementById('heroCO2').textContent = (stats.totalCo2Saved / 1000).toFixed(2) + 'kg';
    document.getElementById('heroMoney').textContent = '$' + stats.totalMoneySaved.toFixed(2);
}

function formatCO2(grams) {
    if (grams >= 1000) return (grams / 1000).toFixed(2) + ' kg';
    return grams.toFixed(1) + ' g';
}

function formatWater(ml) {
    if (ml >= 1000) return (ml / 1000).toFixed(2) + ' L';
    return ml.toFixed(1) + ' ml';
}

function animateValue(elementId, value) {
    document.getElementById(elementId).textContent = value.toLocaleString();
}

// ============================================
// EQUIVALENTS BAR
// ============================================
function updateEquivalents(eq) {
    if (!eq) return;
    document.getElementById('eqTrees').textContent = eq.treesEquivalent;
    document.getElementById('eqCar').textContent = eq.carKmEquivalent;
    document.getElementById('eqPhone').textContent = eq.phoneCharges;
    document.getElementById('eqBulb').textContent = eq.lightbulbHours;
}

// ============================================
// MODEL DISTRIBUTION CHART (Doughnut)
// ============================================
function updateModelChart(breakdown) {
    const labels = Object.keys(breakdown);
    const data = Object.values(breakdown);

    if (labels.length === 0) return;

    const ctx = document.getElementById('modelChart').getContext('2d');

    if (modelChart) {
        modelChart.data.labels = labels;
        modelChart.data.datasets[0].data = data;
        modelChart.update();
        return;
    }

    modelChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels,
            datasets: [{
                data,
                backgroundColor: ['#10b981', '#60a5fa', '#fbbf24', '#a78bfa', '#f87171'],
                borderColor: '#08080c',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { color: '#8c8ca0', font: { size: 11 } }
                }
            }
        }
    });
}

// ============================================
// COMPLEXITY CHART (Bar)
// ============================================
function updateComplexityChart(breakdown) {
    const labels = ['Simple', 'Medium', 'Complex'];
    const data = [breakdown.simple || 0, breakdown.medium || 0, breakdown.complex || 0];

    const ctx = document.getElementById('complexityChart').getContext('2d');

    if (complexityChart) {
        complexityChart.data.datasets[0].data = data;
        complexityChart.update();
        return;
    }

    complexityChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels,
            datasets: [{
                label: 'Requests',
                data,
                backgroundColor: ['#10b981', '#fbbf24', '#f87171'],
                borderRadius: 6,
                borderSkipped: false
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { color: '#8c8ca0' },
                    grid: { color: 'rgba(255,255,255,0.06)' }
                },
                x: {
                    ticks: { color: '#8c8ca0' },
                    grid: { display: false }
                }
            },
            plugins: {
                legend: { display: false }
            }
        }
    });
}

// ============================================
// TIME CHART (Line)
// ============================================
function updateTimeChart(hourly) {
    if (!hourly || hourly.length === 0) return;

    const labels = hourly.map(h => h.hour ? h.hour.slice(11) + ':00' : '');
    const co2Data = hourly.map(h => h.co2Saved);
    const moneyData = hourly.map(h => h.moneySaved);

    const ctx = document.getElementById('timeChart').getContext('2d');

    if (timeChart) {
        timeChart.data.labels = labels;
        timeChart.data.datasets[0].data = co2Data;
        timeChart.data.datasets[1].data = moneyData;
        timeChart.update();
        return;
    }

    timeChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels,
            datasets: [
                {
                    label: 'CO₂ Saved (g)',
                    data: co2Data,
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16,185,129,0.08)',
                    fill: true,
                    tension: 0.4
                },
                {
                    label: 'Money Saved ($)',
                    data: moneyData,
                    borderColor: '#fbbf24',
                    backgroundColor: 'rgba(251,191,36,0.08)',
                    fill: true,
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { color: '#8c8ca0' },
                    grid: { color: 'rgba(255,255,255,0.06)' }
                },
                x: {
                    ticks: { color: '#8c8ca0' },
                    grid: { display: false }
                }
            },
            plugins: {
                legend: {
                    labels: { color: '#8c8ca0', font: { size: 11 } }
                }
            }
        }
    });
}

// ============================================
// REQUESTS TABLE
// ============================================
function updateRequestsTable(requests) {
    const tbody = document.getElementById('requestsTable');

    if (!requests || requests.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="empty">No requests yet. Use the Test API button to try it out!</td></tr>';
        return;
    }

    tbody.innerHTML = requests.map(r => `
        <tr>
            <td>${r.id}</td>
            <td>${new Date(r.timestamp).toLocaleTimeString()}</td>
            <td>${r.originalModel}</td>
            <td><strong>${r.selectedModel}</strong></td>
            <td><span class="complexity-badge complexity-${r.complexity}">${r.complexity}</span></td>
            <td style="color: var(--accent)">${r.co2Saved.toFixed(3)}g</td>
            <td style="color: var(--gold)">$${r.moneySaved.toFixed(4)}</td>
        </tr>
    `).join('');
}

// ============================================
// ESG RATING
// ============================================
function updateESG(stats) {
    // Update reduction circle
    const percent = stats.averageSavingsPercent || 0;
    document.getElementById('reductionPercent').textContent = percent + '%';

    const circle = document.getElementById('reductionCircle');
    const circumference = 2 * Math.PI * 54; // r=54
    const offset = circumference - (percent / 100) * circumference;
    circle.style.strokeDashoffset = offset;

    // Fetch ESG report for grade
    fetch(`${API_BASE}/api/report`)
        .then(res => res.json())
        .then(report => {
            document.getElementById('esgGrade').textContent = report.rating.grade;
            document.getElementById('esgLabel').textContent = report.rating.label;
        })
        .catch(() => {});
}

// ============================================
// TEST API MODAL
// ============================================
function openTestModal() {
    document.getElementById('testModal').classList.add('active');
}

function closeTestModal() {
    document.getElementById('testModal').classList.remove('active');
}

async function sendTestRequest() {
    const message = document.getElementById('testMessage').value.trim();
    const model = document.getElementById('testModel').value;
    const btn = document.getElementById('testBtn');
    const resultDiv = document.getElementById('testResult');
    const resultContent = document.getElementById('testResultContent');

    if (!message) return;

    btn.textContent = 'Sending...';
    btn.disabled = true;

    try {
        const res = await fetch(`${API_BASE}/v1/chat/demo`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer eco-demo-key-2026'
            },
            body: JSON.stringify({
                model,
                messages: [{ role: 'user', content: message }]
            })
        });

        const data = await res.json();
        const eco = data.ecorouter;

        resultDiv.style.display = 'block';
        resultContent.innerHTML = `
            <div class="result-row">
                <span class="result-label">Original Model</span>
                <span class="result-value">${eco.originalModel}</span>
            </div>
            <div class="result-row">
                <span class="result-label">Routed To</span>
                <span class="result-value green">${eco.selectedModel}</span>
            </div>
            <div class="result-row">
                <span class="result-label">Reason</span>
                <span class="result-value">${eco.reason}</span>
            </div>
            <div class="result-row">
                <span class="result-label">Complexity</span>
                <span class="result-value blue">${eco.complexity}</span>
            </div>
            <div class="result-row">
                <span class="result-label">CO₂ Saved</span>
                <span class="result-value green">${eco.savings.co2SavedGrams}g</span>
            </div>
            <div class="result-row">
                <span class="result-label">Money Saved</span>
                <span class="result-value gold">$${eco.savings.moneySaved}</span>
            </div>
            <div class="result-row">
                <span class="result-label">Reduction</span>
                <span class="result-value green">${eco.savings.reductionPercent}%</span>
            </div>
        `;

        // Refresh dashboard stats
        setTimeout(refreshStats, 500);
    } catch (err) {
        resultDiv.style.display = 'block';
        resultContent.innerHTML = `<div style="color: var(--red)">Error: ${err.message}</div>`;
    }

    btn.textContent = 'Send Request';
    btn.disabled = false;
}

// ============================================
// ESG REPORT DOWNLOAD
// ============================================
async function downloadReport() {
    try {
        const res = await fetch(`${API_BASE}/api/report`);
        const report = await res.json();

        const text = `
═══════════════════════════════════════════════
        EcoRouter AI — ESG Report
═══════════════════════════════════════════════

Period: ${report.period}
Generated: ${report.generated}

── Summary ──────────────────────────────────
Total Requests:     ${report.summary.totalRequests}
CO₂ Saved:          ${report.summary.totalCo2SavedKg} kg
Water Saved:        ${report.summary.totalWaterSavedLiters} liters
Money Saved:        $${report.summary.totalMoneySaved}

── Environmental Equivalents ────────────────
Trees Planted:      ${report.equivalents.treesPlanted}
Car Km Avoided:     ${report.equivalents.carKmAvoided}
Phone Charges:      ${report.equivalents.phoneChargesAvoided}
Lightbulb Hours:    ${report.equivalents.lightbulbHoursSaved}

── Green AI Rating ──────────────────────────
Grade:              ${report.rating.grade}
Label:              ${report.rating.label}

── Recommendations ──────────────────────────
${report.recommendations.map((r, i) => `${i + 1}. ${r}`).join('\n')}

═══════════════════════════════════════════════
        Powered by EcoRouter AI
     Eco Business Case Competition 2026
═══════════════════════════════════════════════
`;

        const blob = new Blob([text], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `ecorouter-esg-report-${report.period}.txt`;
        a.click();
        URL.revokeObjectURL(url);
    } catch (err) {
        alert('Failed to generate report: ' + err.message);
    }
}

// ============================================
// COPY CODE SNIPPET
// ============================================
function copyCode() {
    const code = document.getElementById('codeSnippet').innerText;
    navigator.clipboard.writeText(code).then(() => {
        const btn = document.querySelector('.copy-btn');
        btn.textContent = 'Copied!';
        setTimeout(() => btn.textContent = 'Copy', 2000);
    });
}

// ============================================
// UPDATE CODE SNIPPET WITH CURRENT URL
// ============================================
function updateCodeSnippet() {
    const code = document.getElementById('codeSnippet');
    if (code) {
        code.innerHTML = code.innerHTML.replace('{YOUR_ECOROUTER_URL}', window.location.origin);
    }
}
