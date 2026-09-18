/* MD FUAR TAKİP SİSTEMİ - JavaScript İstemci Mantığı */

const MONTH_NAMES = [
    "", "Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
    "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"
];
const DAY_NAMES = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"];

let currentYear = new Date().getFullYear();
let currentMonth = new Date().getMonth() + 1; // 1-12
let selectedDate = new Date(); // Date Object

document.addEventListener("DOMContentLoaded", function () {
    // PWA Service Worker Kaydı
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/static/sw.js').catch(err => console.log('SW Hata:', err));
    }

    // Varsayılan Excel Tarihleri
    const todayStr = formatDateISO(new Date());
    const weekAgo = new Date();
    weekAgo.setDate(weekAgo.getDate() - 6);
    document.getElementById("exStart").value = formatDateISO(weekAgo);
    document.getElementById("exEnd").value = todayStr;

    // Etkinlik Dinleyicileri
    document.getElementById("btnPrevMonth").addEventListener("click", prevMonth);
    document.getElementById("btnNextMonth").addEventListener("click", nextMonth);
    document.getElementById("btnToday").addEventListener("click", goToday);
    document.getElementById("btnThemeToggle").addEventListener("click", toggleTheme);

    document.getElementById("numReceived").addEventListener("input", calculateNetProfit);
    document.getElementById("numExpense").addEventListener("input", calculateNetProfit);

    document.getElementById("btnSaveRecord").addEventListener("click", saveRecord);
    document.getElementById("btnDeleteRecord").addEventListener("click", deleteRecord);
    document.getElementById("btnClearForm").addEventListener("click", clearForm);

    document.getElementById("btnDownloadExcel").addEventListener("click", downloadExcel);
    document.getElementById("txtSearch").addEventListener("input", searchRecords);

    // Modal Açıldığında Veri Yükleme
    const firmModalEl = document.getElementById("firmModal");
    if (firmModalEl) {
        firmModalEl.addEventListener("show.bs.modal", loadFirmSummary);
    }

    const searchModalEl = document.getElementById("searchModal");
    if (searchModalEl) {
        searchModalEl.addEventListener("show.bs.modal", function () {
            searchRecords();
        });
    }

    // İlk Yükleme
    refreshCalendar();
    loadSelectedDateRecord();
    updateMonthlySummary();
});

function formatDateISO(d) {
    const yyyy = d.getFullYear();
    const mm = String(d.getMonth() + 1).padStart(2, '0');
    const dd = String(d.getDate()).padStart(2, '0');
    return `${yyyy}-${mm}-${dd}`;
}

function formatDateFormatted(d) {
    const day = d.getDate();
    const month = MONTH_NAMES[d.getMonth() + 1];
    const year = d.getFullYear();
    const dayName = DAY_NAMES[(d.getDay() + 6) % 7];
    return `📅 ${day} ${month} ${year} ${dayName}`;
}

function toggleTheme() {
    const body = document.body;
    body.classList.toggle("dark-mode");
    const icon = document.querySelector("#btnThemeToggle i");
    if (body.classList.contains("dark-mode")) {
        icon.className = "fa-solid fa-sun text-warning";
    } else {
        icon.className = "fa-solid fa-moon";
    }
}

function prevMonth() {
    if (currentMonth === 1) {
        currentMonth = 12;
        currentYear--;
    } else {
        currentMonth--;
    }
    refreshCalendar();
    updateMonthlySummary();
}

function nextMonth() {
    if (currentMonth === 12) {
        currentMonth = 1;
        currentYear++;
    } else {
        currentMonth++;
    }
    refreshCalendar();
    updateMonthlySummary();
}

function goToday() {
    selectedDate = new Date();
    currentYear = selectedDate.getFullYear();
    currentMonth = selectedDate.getMonth() + 1;
    refreshCalendar();
    loadSelectedDateRecord();
    updateMonthlySummary();
}

function refreshCalendar() {
    document.getElementById("lblMonthYear").innerText = `${MONTH_NAMES[currentMonth]} ${currentYear}`;
    const container = document.getElementById("calendarDays");
    container.innerHTML = "";

    fetch(`/api/monthly-summary?year=${currentYear}&month=${currentMonth}`)
        .then(res => res.json())
        .then(resData => {
            const recordedMap = resData.recorded_dates || {};
            buildCalendarGrid(recordedMap);
        })
        .catch(err => console.error("Takvim veri hatası:", err));
}

function buildCalendarGrid(recordedMap) {
    const container = document.getElementById("calendarDays");
    container.innerHTML = "";

    const firstDayIndex = new Date(currentYear, currentMonth - 1, 1).getDay();
    const daysInMonth = new Date(currentYear, currentMonth, 0).getDate();

    // Pazartesi = 0 yapmak için kaydırma
    const startOffset = (firstDayIndex + 6) % 7;

    for (let i = 0; i < startOffset; i++) {
        const emptyDiv = document.createElement("div");
        container.appendChild(emptyDiv);
    }

    const todayStr = formatDateISO(new Date());
    const selectedStr = formatDateISO(selectedDate);

    for (let day = 1; day <= daysInMonth; day++) {
        const dObj = new Date(currentYear, currentMonth - 1, day);
        const dStr = formatDateISO(dObj);

        const btn = document.createElement("div");
        btn.className = "day-btn";
        if (dStr === selectedStr) btn.classList.add("selected");
        if (dStr === todayStr) btn.classList.add("today");

        let dayText = day;
        const status = recordedMap[dStr];

        if (status && dStr !== selectedStr) {
            let badgeIcon = "🟢";
            if (status === "PARTIAL") badgeIcon = "🟡";
            if (status === "PENDING") badgeIcon = "🔴";
            btn.innerHTML = `<span>${day}</span><span class="day-badge">${badgeIcon}</span>`;
        } else {
            btn.innerText = day;
        }

        btn.addEventListener("click", function () {
            selectedDate = dObj;
            refreshCalendar();
            loadSelectedDateRecord();
        });

        container.appendChild(btn);
    }
}

function loadSelectedDateRecord() {
    const dateStr = formatDateISO(selectedDate);
    document.getElementById("lblSelectedDate").innerText = formatDateFormatted(selectedDate);

    fetch(`/api/record/${dateStr}`)
        .then(res => res.json())
        .then(res => {
            clearForm(false);
            const rec = res.data;
            if (rec) {
                document.getElementById("badgeFormStatus").innerText = "Kayıt Var";
                document.getElementById("badgeFormStatus").className = "badge bg-success";
                document.getElementById("txtFirmName").value = rec.firm_name || "";
                document.getElementById("numYovmiye").value = rec.yovmiye || 1;
                document.getElementById("numReceived").value = rec.amount_received || "";
                document.getElementById("numExpense").value = rec.worker_expense || "";
                document.getElementById("txtNotes").value = rec.notes || "";

                const st = rec.payment_status || "PAID";
                if (st === "PAID") document.getElementById("stPaid").checked = true;
                if (st === "PARTIAL") document.getElementById("stPartial").checked = true;
                if (st === "PENDING") document.getElementById("stPending").checked = true;

                calculateNetProfit();
            } else {
                document.getElementById("badgeFormStatus").innerText = "Yeni Kayıt";
                document.getElementById("badgeFormStatus").className = "badge bg-secondary";
            }
        });
}

function calculateNetProfit() {
    const recv = parseFloat(document.getElementById("numReceived").value) || 0;
    const exp = parseFloat(document.getElementById("numExpense").value) || 0;
    const net = recv - exp;
    document.getElementById("lblNetProfit").innerText = `₺${net.toLocaleString("tr-TR", { minimumFractionDigits: 2 })}`;
}

function clearForm(resetSelected = true) {
    document.getElementById("txtFirmName").value = "";
    document.getElementById("numYovmiye").value = "1";
    document.getElementById("numReceived").value = "";
    document.getElementById("numExpense").value = "";
    document.getElementById("stPaid").checked = true;
    document.getElementById("txtNotes").value = "";
    document.getElementById("lblNetProfit").innerText = "₺0,00";
}

function saveRecord() {
    const dateStr = formatDateISO(selectedDate);
    const firmName = document.getElementById("txtFirmName").value.trim();
    const yovmiye = parseFloat(document.getElementById("numYovmiye").value) || 0;
    const received = parseFloat(document.getElementById("numReceived").value) || 0;
    const expense = parseFloat(document.getElementById("numExpense").value) || 0;
    const notes = document.getElementById("txtNotes").value.trim();

    let status = "PAID";
    if (document.getElementById("stPartial").checked) status = "PARTIAL";
    if (document.getElementById("stPending").checked) status = "PENDING";

    const payload = {
        record_date: dateStr,
        firm_name: firmName,
        yovmiye: yovmiye,
        amount_received: received,
        worker_expense: expense,
        payment_status: status,
        notes: notes
    };

    fetch("/api/record", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    })
    .then(res => res.json())
    .then(res => {
        if (res.success) {
            alert(`${dateStr} tarihli kayıt başarıyla kaydedildi!`);
            refreshCalendar();
            loadSelectedDateRecord();
            updateMonthlySummary();
        } else {
            alert("Hata: " + res.error);
        }
    });
}

function deleteRecord() {
    const dateStr = formatDateISO(selectedDate);
    if (!confirm(`${dateStr} tarihli kaydı silmek istediğinize emin misiniz?`)) return;

    fetch(`/api/record/${dateStr}`, { method: "DELETE" })
        .then(res => res.json())
        .then(res => {
            if (res.success) {
                alert("Kayıt silindi.");
                clearForm();
                refreshCalendar();
                loadSelectedDateRecord();
                updateMonthlySummary();
            }
        });
}

function updateMonthlySummary() {
    fetch(`/api/monthly-summary?year=${currentYear}&month=${currentMonth}`)
        .then(res => res.json())
        .then(res => {
            const s = res.summary || {};
            document.getElementById("lblSummaryTitle").innerText = `📊 ${MONTH_NAMES[currentMonth].toUpperCase()} ${currentYear} ÖZETİ`;
            document.getElementById("statYovmiye").innerText = `${(s.total_yovmiye || 0).toFixed(1)} Yövmiye`;
            document.getElementById("statReceived").innerText = `₺${(s.total_received || 0).toLocaleString("tr-TR", { minimumFractionDigits: 2 })}`;
            document.getElementById("statExpense").innerText = `₺${(s.total_expense || 0).toLocaleString("tr-TR", { minimumFractionDigits: 2 })}`;
            document.getElementById("statNet").innerText = `₺${(s.total_net || 0).toLocaleString("tr-TR", { minimumFractionDigits: 2 })}`;
        });
}

function loadFirmSummary() {
    const tbody = document.getElementById("tblFirmSummary");
    tbody.innerHTML = "<tr><td colspan='7' class='text-center py-3'>Yükleniyor...</td></tr>";

    fetch("/api/firm-summary")
        .then(res => res.json())
        .then(res => {
            tbody.innerHTML = "";
            const list = res.data || [];
            if (list.length === 0) {
                tbody.innerHTML = "<tr><td colspan='7' class='text-center py-3 text-muted'>Henüz kayıtlı firma bulunamadı.</td></tr>";
                return;
            }

            list.forEach(item => {
                const tr = document.createElement("tr");
                let badgeStr = `<span class="badge bg-success">🟢 Ödendi</span>`;
                if (item.pending_count > 0 || item.partial_count > 0) {
                    badgeStr = `<span class="badge bg-warning text-dark">🟡 ${item.pending_count + item.partial_count} Alacak Var</span>`;
                }

                tr.innerHTML = `
                    <td class="fw-bold">${item.firm_name}</td>
                    <td class="text-center">${item.total_jobs}</td>
                    <td class="text-center">${item.total_yovmiye.toFixed(1)}</td>
                    <td class="text-end text-success fw-bold">₺${item.total_received.toLocaleString("tr-TR", { minimumFractionDigits: 2 })}</td>
                    <td class="text-end text-danger">₺${item.total_expense.toLocaleString("tr-TR", { minimumFractionDigits: 2 })}</td>
                    <td class="text-end text-orange fw-bold">₺${item.total_net.toLocaleString("tr-TR", { minimumFractionDigits: 2 })}</td>
                    <td class="text-center">${badgeStr}</td>
                `;
                tbody.appendChild(tr);
            });
        });
}

function searchRecords() {
    const q = document.getElementById("txtSearch").value.trim();
    const tbody = document.getElementById("tblSearchResults");

    fetch(`/api/search?q=${encodeURIComponent(q)}`)
        .then(res => res.json())
        .then(res => {
            tbody.innerHTML = "";
            const list = res.data || [];
            if (list.length === 0) {
                tbody.innerHTML = "<tr><td colspan='6' class='text-center py-3 text-muted'>Kayıt bulunamadı.</td></tr>";
                return;
            }

            list.forEach(item => {
                const tr = document.createElement("tr");
                tr.style.cursor = "pointer";

                let stBadge = `<span class="badge bg-success">🟢 Ödendi</span>`;
                if (item.payment_status === "PARTIAL") stBadge = `<span class="badge bg-warning text-dark">🟡 Alacak Var</span>`;
                if (item.payment_status === "PENDING") stBadge = `<span class="badge bg-danger">🔴 Bekliyor</span>`;

                tr.innerHTML = `
                    <td class="fw-bold">${item.record_date}</td>
                    <td>${item.firm_name}</td>
                    <td class="text-center">${item.yovmiye}</td>
                    <td class="text-end text-success fw-bold">₺${item.amount_received.toLocaleString("tr-TR", { minimumFractionDigits: 2 })}</td>
                    <td class="text-end text-danger">₺${item.worker_expense.toLocaleString("tr-TR", { minimumFractionDigits: 2 })}</td>
                    <td>${stBadge}</td>
                `;

                tr.addEventListener("click", function () {
                    const parts = item.record_date.split("-");
                    selectedDate = new Date(parts[0], parts[1] - 1, parts[2]);
                    currentYear = selectedDate.getFullYear();
                    currentMonth = selectedDate.getMonth() + 1;
                    refreshCalendar();
                    loadSelectedDateRecord();
                    updateMonthlySummary();

                    const modalEl = document.getElementById("searchModal");
                    const modal = bootstrap.Modal.getInstance(modalEl);
                    if (modal) modal.hide();
                });

                tbody.appendChild(tr);
            });
        });
}

function downloadExcel() {
    const sDate = document.getElementById("exStart").value;
    const eDate = document.getElementById("exEnd").value;
    const firm = document.getElementById("exFirm").value.trim();

    if (!sDate || !eDate) {
        alert("Lütfen başlangıç ve bitiş tarihlerini girin!");
        return;
    }

    const url = `/api/export-excel?start_date=${sDate}&end_date=${eDate}&firm_name=${encodeURIComponent(firm)}`;
    window.location.href = url;
}
