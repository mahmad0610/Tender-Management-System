/**
 * Component Library for Evaluation Compliance
 * Implements: Toolbar, Navigation, Transaction Grid
 */

const Components = {
    // --- 1. CRUD Toolbar ---
    renderToolbar: (options) => {
        const actions = [
            { id: 'add', label: 'Add', icon: '➕' },
            { id: 'edit', label: 'Edit', icon: '✎' },
            { id: 'delete', label: 'Delete', icon: '🗑' },
            { id: 'save', label: 'Save', icon: '💾' },
            { id: 'cancel', label: 'Cancel', icon: '✖' },
            { id: 'search', label: 'Search', icon: '🔍' },
            { id: 'refresh', label: 'Refresh', icon: '↻' },
            { id: 'help', label: 'Help', icon: '?' }
        ];

        return `
            <div class="toolbar">
                ${actions.map(act => `
                    <button class="tool-btn" onclick="${options.handler}('${act.id}')">
                        <span style="font-size:18px">${act.icon}</span>
                        <span>${act.label}</span>
                    </button>
                `).join('')}
            </div>
            <!-- Feedback Bar -->
            <div id="feedback-bar" style="background:#ffc; padding:5px; font-size:12px; border-bottom:1px solid #ccc; display:none;">Ready</div>
        `;
    },

    showFeedback: (msg, type = 'info') => {
        const bar = document.getElementById('feedback-bar');
        if (bar) {
            bar.innerText = msg;
            bar.style.display = 'block';
            bar.style.background = type === 'error' ? '#fee' : '#ffc';
            setTimeout(() => bar.style.display = 'none', 3000);
        }
    },

    // --- 2. Navigation Bar ---
    renderNav: (handler) => {
        return `
            <div class="toolbar" style="justify-content: center; margin-top:10px;">
                <button class="tool-btn" onclick="${handler}('first')">|&lt; First</button>
                <button class="tool-btn" onclick="${handler}('prev')">&lt; Prev</button>
                <span id="nav-info" style="margin:0 15px; font-weight:bold;">0 / 0</span>
                <button class="tool-btn" onclick="${handler}('next')">Next &gt;</button>
                <button class="tool-btn" onclick="${handler}('last')">Last &gt;|</button>
            </div>
        `;
    },

    // --- 3. Transaction Grid (Editable Table) ---
    renderGrid: (id, columns, data = []) => {
        // Columns schema: { key, label, type: 'text'|'number'|'combo', source: [] }
        let html = `
            <div class="grid-container">
            <table class="sys-grid" id="${id}">
                <thead>
                    <tr>
                        ${columns.map(c => `<th>${c.label}</th>`).join('')}
                        <th style="width:30px">X</th>
                    </tr>
                </thead>
                <tbody>
        `;

        // Render rows logic to be handled by specific renderers or initial data
        // For dynamic adding, we use JS
        html += `</tbody></table></div>
        <div style="padding:5px;">
            <button class="btn btn-sm" onclick="Components.gridAddRow('${id}')">+ Add Line</button>
        </div>`;

        // Store schema for later
        window.gridSchemas = window.gridSchemas || {};
        window.gridSchemas[id] = columns;

        return html;
    },

    gridAddRow: (gridId, rowData = {}) => {
        const schema = window.gridSchemas[gridId];
        const tbody = document.querySelector(`#${gridId} tbody`);
        const tr = document.createElement('tr');

        tr.innerHTML = schema.map(col => {
            let val = rowData[col.key] || '';
            let input = '';

            if (col.type === 'combo') {
                const opts = col.source.map(opt => `<option value="${opt.id}" ${opt.id == val ? 'selected' : ''}>${opt.name}</option>`).join('');
                input = `<select class="grid-select" onchange="Components.calcGrid('${gridId}')" data-key="${col.key}">${opts}</select>`;
            } else if (col.type === 'number') {
                input = `<input class="grid-input" type="number" value="${val}" data-key="${col.key}" oninput="Components.calcGrid('${gridId}')">`;
            } else if (col.type === 'image') {
                const url = val || '/static/img/placeholder.png'; // Fallback
                input = `<img src="${url}" class="grid-thumbnail" onerror="this.src='https://via.placeholder.com/40'">`;
            } else {
                input = `<input class="grid-input" value="${val}" data-key="${col.key}">`;
            }
            return `<td>${input}</td>`;
        }).join('') + `<td><button onclick="this.closest('tr').remove(); Components.calcGrid('${gridId}')" style="border:none; background:none; color:var(--accent-red); cursor:pointer;">&times;</button></td>`;

        tbody.appendChild(tr);
    },

    calcGrid: (gridId) => {
        if (gridId === 'order-grid') {
            let total = 0;
            const schema = window.gridSchemas[gridId];
            const itemCol = schema.find(c => c.key === 'item_id');
            const itemSource = itemCol ? itemCol.source : [];

            const rows = document.querySelectorAll(`#${gridId} tbody tr`);
            rows.forEach(row => {
                const combo = row.querySelector('[data-key="item_id"]');
                const qtyInput = row.querySelector('[data-key="qty"]');
                const rateInput = row.querySelector('[data-key="rate"]');
                const img = row.querySelector('.grid-thumbnail');

                const itemId = combo ? combo.value : null;
                const item = itemSource.find(i => i.id == itemId);

                // Auto-fill Rate if present and not already touched (optional logic)
                if (item && rateInput && !rateInput.value) {
                    rateInput.value = item.rate || 0;
                }

                // Update Image
                if (item && img && item.image_url) {
                    img.src = item.image_url;
                } else if (img) {
                    img.src = 'https://via.placeholder.com/40';
                }

                const qty = parseFloat(qtyInput ? qtyInput.value : 0) || 0;
                const rate = parseFloat(rateInput ? rateInput.value : 0) || 0;
                const amt = qty * rate;

                // Update Amount field if exists
                const amtInput = row.querySelector('[data-key="amount"]');
                if (amtInput) amtInput.value = amt.toFixed(2);

                total += amt;
            });

            // Update Totals
            const sub = document.getElementById('grid-subtotal');
            const tax = document.getElementById('grid-tax');
            const grand = document.getElementById('grid-grand');

            if (sub) sub.innerText = total.toFixed(2);
            if (tax) tax.innerText = (total * 0.18).toFixed(2);
            if (grand) grand.innerText = (total * 1.18).toFixed(2);
        }
    }
};
