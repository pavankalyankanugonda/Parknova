// ParkNova Smart Parking - Main Client-Side Logic

document.addEventListener('DOMContentLoaded', () => {
    // 1. Dark/Light Mode Theme Initialization
    initTheme();

    // 2. Setup SocketIO Connection
    initSocket();

    // 3. User Profile Dropdown Setup
    initDropdowns();
});

// Theme Management
function initTheme() {
    const themeToggleBtn = document.getElementById('theme-toggle');
    if (!themeToggleBtn) return;

    // Check localStorage or system settings
    const currentTheme = localStorage.getItem('theme');
    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

    if (currentTheme === 'dark' || (!currentTheme && systemPrefersDark)) {
        document.documentElement.classList.add('dark');
        updateThemeToggleIcons(true);
    } else {
        document.documentElement.classList.remove('dark');
        updateThemeToggleIcons(false);
    }

    // Toggle theme
    themeToggleBtn.addEventListener('click', () => {
        const isDark = document.documentElement.classList.toggle('dark');
        localStorage.setItem('theme', isDark ? 'dark' : 'light');
        updateThemeToggleIcons(isDark);
    });
}

function updateThemeToggleIcons(isDark) {
    const moonIcon = document.getElementById('theme-toggle-moon');
    const sunIcon = document.getElementById('theme-toggle-sun');
    if (!moonIcon || !sunIcon) return;

    if (isDark) {
        moonIcon.classList.add('hidden');
        sunIcon.classList.remove('hidden');
    } else {
        sunIcon.classList.add('hidden');
        moonIcon.classList.remove('hidden');
    }
}

// SocketIO Real-Time Updates
function initSocket() {
    if (typeof io === 'undefined') {
        console.log('Socket.IO is not imported in this view.');
        return;
    }

    const socket = io();

    socket.on('connect', () => {
        console.log('Successfully connected to ParkNova WebSocket server.');
    });

    // Handle slot update event
    socket.on('slot_updated', (data) => {
        console.log('Slot updated event received:', data);
        updateSlotUI(data.slot_id, data.status, data.type);
        showToast('Real-time Update', `Parking Slot ${data.slot_id} is now ${data.status}!`, 'info');
    });

    socket.on('slot_deleted', (data) => {
        console.log('Slot deleted event received:', data);
        const slotEl = document.getElementById(`slot-card-${data.slot_id}`);
        if (slotEl) {
            slotEl.remove();
        }
    });
}

// Update Slot Color and Text in Grid
function updateSlotUI(slotId, status, type) {
    const slotCard = document.getElementById(`slot-card-${slotId}`);
    if (!slotCard) return;

    const statusBadge = document.getElementById(`slot-status-${slotId}`);
    const selectButton = document.getElementById(`slot-btn-${slotId}`);

    // Standard styling dictionary
    const statusClasses = {
        'Available': {
            bg: 'bg-green-50/70',
            border: 'border-green-200',
            badgeBg: 'bg-green-100',
            badgeText: 'text-green-800',
            darkBg: 'dark:bg-green-950/20',
            darkBorder: 'dark:border-green-900/40',
            dot: 'bg-green-500'
        },
        'Occupied': {
            bg: 'bg-red-50/70',
            border: 'border-red-200',
            badgeBg: 'bg-red-100',
            badgeText: 'text-red-800',
            darkBg: 'dark:bg-red-950/20',
            darkBorder: 'dark:border-red-900/40',
            dot: 'bg-red-500'
        },
        'Reserved': {
            bg: 'bg-amber-50/70',
            border: 'border-amber-200',
            badgeBg: 'bg-amber-100',
            badgeText: 'text-amber-800',
            darkBg: 'dark:bg-amber-950/20',
            darkBorder: 'dark:border-amber-900/40',
            dot: 'bg-amber-500'
        },
        'Inactive': {
            bg: 'bg-gray-50/70',
            border: 'border-gray-200',
            badgeBg: 'bg-gray-100',
            badgeText: 'text-gray-800',
            darkBg: 'dark:bg-gray-800/20',
            darkBorder: 'dark:border-gray-700/40',
            dot: 'bg-gray-500'
        }
    };

    const style = statusClasses[status] || statusClasses['Inactive'];

    // Update main card styling
    slotCard.className = `slot-card glass-panel p-5 rounded-2xl border transition-all duration-300 ${style.bg} ${style.darkBg} ${style.border} ${style.darkBorder}`;

    // Update status badge
    if (statusBadge) {
        statusBadge.className = `px-2.5 py-1 text-xs font-semibold rounded-full flex items-center gap-1.5 ${style.badgeBg} ${style.badgeText}`;
        statusBadge.innerHTML = `<span class="h-2 w-2 rounded-full ${style.dot}"></span> ${status}`;
    }

    // Update booking page select buttons if present
    if (selectButton) {
        if (status === 'Available') {
            selectButton.disabled = false;
            selectButton.classList.remove('opacity-50', 'cursor-not-allowed');
            selectButton.classList.add('hover:bg-indigo-700');
            selectButton.textContent = 'Select Slot';
        } else {
            selectButton.disabled = true;
            selectButton.classList.add('opacity-50', 'cursor-not-allowed');
            selectButton.classList.remove('hover:bg-indigo-700');
            selectButton.textContent = 'Unavailable';
        }
    }
}

// Toast Notification Manager
function showToast(title, message, type = 'success') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    // Toast Card
    const toast = document.createElement('div');
    
    // Choose colors based on type
    const colors = {
        'success': {
            bg: 'bg-emerald-50 dark:bg-emerald-950/80',
            border: 'border-emerald-200 dark:border-emerald-900',
            iconColor: 'text-emerald-500',
            icon: 'fa-check-circle'
        },
        'info': {
            bg: 'bg-indigo-50 dark:bg-indigo-950/80',
            border: 'border-indigo-200 dark:border-indigo-900',
            iconColor: 'text-indigo-500',
            icon: 'fa-info-circle'
        },
        'warning': {
            bg: 'bg-amber-50 dark:bg-amber-950/80',
            border: 'border-amber-200 dark:border-amber-900',
            iconColor: 'text-amber-500',
            icon: 'fa-exclamation-triangle'
        },
        'danger': {
            bg: 'bg-rose-50 dark:bg-rose-950/80',
            border: 'border-rose-200 dark:border-rose-900',
            iconColor: 'text-rose-500',
            icon: 'fa-exclamation-circle'
        }
    };

    const style = colors[type] || colors['success'];

    toast.className = `flex items-center gap-3 p-4 rounded-xl border shadow-lg max-w-sm transition-all duration-500 opacity-0 translate-y-2 ${style.bg} ${style.border}`;
    toast.innerHTML = `
        <div class="${style.iconColor} text-lg">
            <i class="fas ${style.icon}"></i>
        </div>
        <div class="flex-1">
            <h4 class="text-sm font-semibold text-slate-800 dark:text-slate-100">${title}</h4>
            <p class="text-xs text-slate-600 dark:text-slate-300 mt-0.5">${message}</p>
        </div>
        <button class="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 text-sm focus:outline-none" onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;

    container.appendChild(toast);

    // Fade In
    setTimeout(() => {
        toast.classList.remove('opacity-0', 'translate-y-2');
    }, 10);

    // Auto dismiss after 5 seconds
    setTimeout(() => {
        toast.classList.add('opacity-0', '-translate-y-2');
        setTimeout(() => toast.remove(), 500);
    }, 5000);
}

// Dropdowns and menus
function initDropdowns() {
    // User profile menu dropdown
    const userBtn = document.getElementById('user-menu-btn');
    const dropdown = document.getElementById('user-menu-dropdown');
    
    if (userBtn && dropdown) {
        userBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            dropdown.classList.toggle('hidden');
        });

        // Close when clicking outside
        document.addEventListener('click', () => {
            dropdown.classList.add('hidden');
        });
    }

    // Sidebar Mobile Toggle
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebar = document.getElementById('sidebar');
    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', (e) => {
            e.stopPropagation();
            sidebar.classList.toggle('-translate-x-full');
        });
        
        // Prevent clicking inside sidebar from closing it
        sidebar.addEventListener('click', (e) => {
            e.stopPropagation();
        });
        
        // Click outside closes sidebar on mobile
        document.addEventListener('click', () => {
            if (window.innerWidth < 1024) {
                sidebar.classList.add('-translate-x-full');
            }
        });
    }
}
