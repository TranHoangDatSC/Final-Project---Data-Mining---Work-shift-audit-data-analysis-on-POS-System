/* ═══════════════════════════════════════════════════════════════════════════
   script.js — Xử lý logic Frontend, gọi API và Render dữ liệu cho POS Audit
   ═══════════════════════════════════════════════════════════════════════════ */

document.addEventListener("DOMContentLoaded", async () => {
    // 1. Khởi tạo: Lấy dữ liệu từ API và render giao diện
    await loadDashboardData();
    
    // 2. Gắn sự kiện click cho các tab và sơ đồ CRISP-DM
    setupNavigation();
    
    // 3. Khởi tạo chức năng Lightbox (phóng to ảnh)
    setupLightbox();
});

// ─── GỌI API & RENDER DỮ LIỆU ──────────────────────────────────────────────

async function loadDashboardData() {
    try {
        // Fetch thông tin cấu trúc các phase
        const phasesRes = await fetch('/api/phases');
        if (!phasesRes.ok) throw new Error("Không thể tải cấu trúc Phase");
        const phasesData = await phasesRes.json();
        
        // Fetch toàn bộ KPI của 4 phases cùng lúc
        const summaryRes = await fetch('/api/summary');
        let summaryData = {};
        if (summaryRes.ok) {
            summaryData = await summaryRes.json();
        }

        // Render dữ liệu ra DOM
        renderPhases(phasesData.phases, summaryData);
        
    } catch (error) {
        console.error("Lỗi khởi tạo dữ liệu:", error);
        showToast("Lỗi khi tải dữ liệu: " + error.message);
    }
}

function renderPhases(phases, summaries) {
    phases.forEach(phase => {
        // 1. Render Biểu đồ (Charts)
        const chartsContainer = document.getElementById(`charts-phase-${phase.id}`);
        if (chartsContainer) {
            chartsContainer.innerHTML = phase.charts.map(chart => {
                // Làm đẹp tên file để làm tiêu đề biểu đồ
                const chartTitle = chart.replace('.png', '').replace(/-/g, ' ').toUpperCase();
                return `
                    <div class="chart-card">
                        <img src="/static/images/phase${phase.id}/${chart}" 
                             alt="${chartTitle}" 
                             class="chart-img" 
                             onclick="openLightbox(this.src, '${chartTitle}')"
                             loading="lazy">
                        <h4 class="chart-title">${chartTitle}</h4>
                    </div>
                `;
            }).join('');
        }

        // 2. Render KPIs
        const kpiContainer = document.getElementById(`kpis-phase-${phase.id}`);
        if (kpiContainer && summaries[phase.id]) {
            // Lấy object KPIs thực tế từ response
            const kpiObj = summaries[phase.id].kpis || summaries[phase.id];
            
            kpiContainer.innerHTML = Object.entries(kpiObj).map(([key, value]) => {
                // Parse object lồng nhau (như cluster_sizes) hoặc in trực tiếp
                if (typeof value === 'object' && value !== null) {
                    value = Object.entries(value).map(([k, v]) => `${k}: ${v}`).join(' | ');
                } else {
                    value = formatNumber(value);
                }
                
                const label = key.replace(/_/g, ' ').toUpperCase();
                
                return `
                    <div class="kpi-card" style="--kpi-color: ${phase.color}; border-left: 4px solid ${phase.color}">
                        <div class="kpi-label">${label}</div>
                        <div class="kpi-value">${value}</div>
                    </div>
                `;
            }).join('');
        }
    });
}

// Hàm format số liệu cho đẹp (thêm dấu phẩy nghìn)
function formatNumber(num) {
    if (typeof num === 'number') {
        return new Intl.NumberFormat('vi-VN').format(num);
    }
    return num;
}


// ─── LOGIC CHUYỂN TAB TƯƠNG TÁC ────────────────────────────────────────────

function setupNavigation() {
    // Lấy tất cả các class có khả năng click chuyển trang (Tab, Node, Card)
    const triggers = document.querySelectorAll('.nav-tab, .crisp-node, .home-card');
    
    triggers.forEach(trigger => {
        trigger.addEventListener('click', (e) => {
            // Lấy giá trị data-target (ví dụ: "home", "phase-1", "phase-2")
            const targetId = trigger.getAttribute('data-target');
            
            // Nếu click vào Node 1 (Business Understanding) không có target
            if (targetId === "") {
                showToast("Business Understanding là nền tảng. Vui lòng chọn các Vòng 1-4.");
                return;
            }

            if (targetId) {
                e.preventDefault();
                switchPhase(targetId);
            }
        });
    });
}

function switchPhase(targetId) {
    // 1. Đổi active state của Panels
    // Ghép chữ 'panel-' với targetId để trỏ đúng id trong HTML (vd: panel-home, panel-phase-1)
    document.querySelectorAll('.panel').forEach(panel => {
        panel.classList.remove('active');
    });
    
    const activePanel = document.getElementById(`panel-${targetId}`);
    if (activePanel) {
        activePanel.classList.add('active');
        activePanel.style.animation = 'fadeIn 0.4s ease-in-out';
    }

    // 2. Đổi active state của Navigation Tabs
    document.querySelectorAll('.nav-tab').forEach(tab => {
        tab.classList.remove('active');
        if (tab.getAttribute('data-target') === targetId) {
            tab.classList.add('active');
        }
    });

    // 3. Đổi active state của các node trên sơ đồ CRISP-DM
    document.querySelectorAll('.crisp-node').forEach(node => {
        node.classList.remove('active');
        if (node.getAttribute('data-target') === targetId) {
            node.classList.add('active');
        }
    });
    
    // 4. Trải nghiệm cuộn trang
    if (targetId !== 'home' && activePanel) {
        // Cuộn xuống panel nếu chọn các vòng
        activePanel.scrollIntoView({ behavior: 'smooth', block: 'start' });
    } else {
        // Cuộn lên đầu nếu bấm về trang chủ
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
}


// ─── LOGIC LIGHTBOX (PHÓNG TO ẢNH BIỂU ĐỒ) ──────────────────────────────────

function setupLightbox() {
    const lightbox = document.getElementById('lightbox');
    const closeBtn = document.getElementById('lightbox-close');
    const backdrop = document.getElementById('lightbox-backdrop');

    if (!lightbox) return;

    const closeLightbox = () => {
        lightbox.hidden = true;
        document.body.style.overflow = ''; // Trả lại scroll cho trang web
    };

    closeBtn.addEventListener('click', closeLightbox);
    backdrop.addEventListener('click', closeLightbox);
    
    // Hỗ trợ đóng bằng nút ESC
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && !lightbox.hidden) {
            closeLightbox();
        }
    });
}

// Đưa hàm ra Global scope để dùng trong thuộc tính onclick của thẻ img
window.openLightbox = function(src, title = '') {
    const lightbox = document.getElementById('lightbox');
    const img = document.getElementById('lightbox-img');
    const desc = document.getElementById('lightbox-desc'); // Hoặc caption tùy bạn đặt ở HTML
    
    if (lightbox && img) {
        img.src = src;
        if (desc) desc.textContent = title;
        
        lightbox.hidden = false;
        document.body.style.overflow = 'hidden'; // Khóa scroll trang khi mở ảnh
    }
};


// ─── TIỆN ÍCH: TOAST THÔNG BÁO ──────────────────────────────────────────────

function showToast(message) {
    const toast = document.createElement('div');
    toast.className = 'toast show';
    toast.textContent = message;
    
    // Gắn style inline tạm thời phòng trường hợp CSS chưa có class .toast
    Object.assign(toast.style, {
        position: 'fixed',
        bottom: '20px',
        left: '50%',
        transform: 'translateX(-50%)',
        backgroundColor: '#ff4757',
        color: 'white',
        padding: '10px 20px',
        borderRadius: '8px',
        zIndex: '9999',
        boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
    });

    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transition = 'opacity 0.5s';
        setTimeout(() => toast.remove(), 500);
    }, 3000);
}

/* Thêm keyframe cho animation fadeIn */
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
`;
document.head.appendChild(style);

