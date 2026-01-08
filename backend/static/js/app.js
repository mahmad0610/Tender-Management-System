// Custom Logic for Tender System

// State
let currentUser = JSON.parse(localStorage.getItem('user')) || null;
let currentView = 'Dashboard';

// Init
function init() {
    if (!currentUser) {
        window.location.href = '/';
        return;
    }
    document.getElementById('user-info').innerText = `${currentUser.full_name} (${currentUser.role})`;
    renderSidebar();
    loadView('Dashboard');
}

function logout() {
    localStorage.removeItem('user');
    window.location.href = '/';
}

function renderSidebar() {
    const allItems = [
        { label: 'Dashboard', icon: 'fa-home', roles: ['admin', 'technical', 'finance', 'vendor', 'client'] },
        { label: 'Tenders', icon: 'fa-file-text', roles: ['admin', 'technical', 'vendor', 'client'] },
        { label: 'Contracts', icon: 'fa-handshake', roles: ['admin', 'vendor', 'client'] },
        { label: 'Orders', icon: 'fa-shopping-cart', roles: ['admin', 'finance', 'vendor', 'client'] },
        { label: 'Delivery', icon: 'fa-truck', roles: ['admin', 'technical', 'vendor', 'client'] },
        { label: 'Payments', icon: 'fa-money-bill', roles: ['admin', 'finance', 'vendor', 'client'] }
    ];

    const role = currentUser.role.toLowerCase();
    const menuItems = allItems.filter(item => item.roles.includes(role));

    // Profile Header
    const avatarUrl = currentUser.profile_image || 'https://via.placeholder.com/70';
    const profileHeader = `
        <div class="sidebar-header">
            <div class="profile-avatar" style="background-image: url('${avatarUrl}')"></div>
            <div style="font-weight:700; font-size:1.1rem; color:white;">${currentUser.full_name}</div>
            <div style="font-size:0.8rem; color:var(--accent-blue); text-transform:uppercase; margin-top:5px;">${currentUser.role}</div>
        </div>
    `;

    document.getElementById('nav-menu').innerHTML = profileHeader + menuItems.map(item => `
        <div class="nav-item-metro" onclick="loadView('${item.label}')">
            <i class="fa ${item.icon}" style="width:25px; opacity:0.7"></i> ${item.label}
        </div>
    `).join('');
}

function loadView(view) {
    currentView = view;
    document.getElementById('page-title').innerText = view;
    const content = document.getElementById('main-content');
    content.innerHTML = '<div style="padding:40px; text-align:center;"><i class="fa fa-spinner fa-spin"></i> Loading...</div>';

    switch (view) {
        case 'Dashboard': renderDashboard(); break;
        case 'Tenders': renderTenders(); break;
        case 'Orders': renderOrders(); break;
        case 'Contracts': renderContracts(); break;
        case 'Delivery': renderDelivery(); break;
        case 'Payments': renderPayments(); break;
        default: content.innerHTML = `<div class="card">View <b>${view}</b> coming soon.</div>`;
    }
}

// --- 1. Dashboard (Real Data / No Mocks) ---
async function renderDashboard() {
    const content = document.getElementById('main-content');

    // Fetch stats in parallel
    const [tenders, pos, contracts, invoices] = await Promise.all([
        api.getTenders(),
        api.getPOs(),
        api.getContracts(),
        api.getInvoices()
    ]);

    const role = currentUser.role.toLowerCase();

    const tiles = [
        { label: 'Active Tenders', count: tenders.length, icon: 'fa-file-text', color: 'tile-blue', view: 'Tenders', roles: ['admin', 'technical', 'vendor', 'client'] },
        { label: 'Contracts', count: contracts.length, icon: 'fa-handshake', color: 'tile-purple', view: 'Contracts', roles: ['admin', 'vendor', 'client'] },
        { label: 'Purchase Orders', count: pos.length, icon: 'fa-shopping-cart', color: 'tile-orange', view: 'Orders', roles: ['admin', 'finance', 'vendor', 'client'] },
        { label: 'Pending Bills', count: invoices.filter(i => i.status !== 'Paid').length, icon: 'fa-file-invoice-dollar', color: 'tile-green', view: 'Payments', roles: ['admin', 'finance', 'vendor', 'client'] }
    ];

    const visibleTiles = tiles.filter(t => t.roles.includes(role));

    content.innerHTML = `
        <div class="tile-grid">
            ${visibleTiles.map(t => `
                <div class="tile ${t.color}" onclick="loadView('${t.view}')">
                    <div class="tile-count">${t.count}</div>
                    <div class="tile-title">${t.label}</div>
                    <i class="fa ${t.icon} fa-2x" style="opacity:0.3; position:absolute; bottom:20px; right:20px;"></i>
                </div>
            `).join('')}
        </div>
    `;
}

// --- 2. Tenders (Single Interface) ---
async function renderTenders() {
    const content = document.getElementById('main-content');
    // Using Component Library for Toolbar and Nav
    const toolbar = Components.renderToolbar({ handler: 'handleTenderAction' });
    const nav = Components.renderNav('handleTenderNav');

    content.innerHTML = `
        <div class="animate-fade">
            ${toolbar}
            <div class="card glass" style="margin-top:20px; display:flex; gap:30px; border-radius:24px;">
                <!-- Left: Advanced Image UI -->
                <div style="width:250px; text-align:center;">
                    <div class="profile-upload-zone" id="tender-img" style="width:250px; height:250px; border-radius:16px; margin-bottom:15px; border-style:solid;">
                        <i class="fa fa-image fa-3x" style="opacity:0.2"></i>
                    </div>
                    <button class="btn-primary" style="width:100%" onclick="document.getElementById('t-img-up').click()">
                        <i class="fa fa-upload"></i> Change Image
                    </button>
                    <input type="file" id="t-img-up" class="hidden" onchange="uploadTenderImg(this)">
                </div>
                
                <!-- Right: High-Fidelity Form -->
                <div style="flex:1;">
                    <div class="form-group">
                        <label class="form-label">Tender Title</label>
                        <input class="form-control" style="font-size:1.2rem; font-weight:600; border-radius:12px;" id="t-title" placeholder="e.g., Annual Furniture Supply">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Detailed Description</label>
                        <textarea class="form-control" style="border-radius:12px;" id="t-desc" rows="4"></textarea>
                    </div>
                    <div style="display:flex; gap:20px;">
                        <div class="form-group" style="flex:1">
                            <label class="form-label">Estimated Budget ($)</label>
                            <input class="form-control" style="border-radius:12px;" type="number" id="t-budget">
                        </div>
                        <div class="form-group" style="flex:1">
                            <label class="form-label">Closing Date</label>
                            <input class="form-control" style="border-radius:12px;" type="date" id="t-deadline">
                        </div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Process Status</label>
                        <input class="form-control" style="background:#f1f5f9; border:none; border-radius:12px; font-weight:700; color:var(--accent-blue);" id="t-status" readonly value="Draft">
                    </div>
                </div>
            </div>
            ${nav}
        </div>
    `;

    window.currentTenders = await api.getTenders();
    window.tIndex = 0;
    if (window.currentTenders.length > 0) loadTenderForm(0);
}

function loadTenderForm(idx) {
    const list = window.currentTenders;
    if (idx < 0 || idx >= list.length) return;
    window.tIndex = idx;

    const t = list[idx];
    document.getElementById('t-title').value = t.title;
    document.getElementById('t-desc').value = t.description;
    document.getElementById('t-budget').value = t.budget;
    document.getElementById('t-deadline').value = t.deadline;
    document.getElementById('t-status').value = t.status;

    // Image handling
    const imgDiv = document.getElementById('tender-img');
    if (t.image_url) {
        imgDiv.innerText = '';
        imgDiv.style.backgroundImage = `url(${t.image_url})`;
    } else {
        imgDiv.innerText = 'No Image';
        imgDiv.style.backgroundImage = '';
    }

    // Update Nav Info
    document.getElementById('nav-info').innerText = `${idx + 1} / ${list.length}`;
}

// Global Handlers
window.handleTenderAction = (action) => {
    if (action === 'add') {
        // Clear form
        document.querySelectorAll('#main-content input').forEach(i => i.value = '');
        document.getElementById('t-status').value = 'New';
        document.getElementById('nav-info').innerText = 'New Record';
        Components.showFeedback('Enter details and click Save.');
    } else if (action === 'save') {
        // Logic to save
        const data = {
            title: document.getElementById('t-title').value,
            description: document.getElementById('t-desc').value,
            budget: parseFloat(document.getElementById('t-budget').value),
            deadline: document.getElementById('t-deadline').value,
            image_url: window.tempTenderImg || null
        };
        api.createTender(data).then(() => {
            Components.showFeedback('Saved Successfully!');
            renderTenders(); // Reload
        });
    } else {
        Components.showFeedback(`Action ${action} not implemented in demo`, 'info');
    }
};

window.handleTenderNav = (dir) => {
    const max = window.currentTenders.length - 1;
    if (dir === 'first') loadTenderForm(0);
    if (dir === 'prev') loadTenderForm(Math.max(0, window.tIndex - 1));
    if (dir === 'next') loadTenderForm(Math.min(max, window.tIndex + 1));
    if (dir === 'last') loadTenderForm(max);
};


// --- 3. Orders (Transactional Interface) ---
async function renderOrders() {
    const content = document.getElementById('main-content');
    const items = await api.getItems(); // Fetch Item Master for Combo Box
    const tenders = await api.getTenders();

    // Toolbar
    const toolbar = Components.renderToolbar({ handler: 'handleOrderAction' });

    content.innerHTML = `
        <div class="animate-fade">
            ${toolbar}
            <div class="card glass" style="margin-top:20px; border-radius:24px;">
                <h3 style="margin-top:0; font-weight:700; color:var(--text-main);">Purchase Order Creation</h3>
                <p style="color:var(--text-muted); font-size:0.9rem;">Generate professional POs with real-time tax calculation.</p>
                <div style="display:grid; grid-template-columns: 1fr 1fr; gap:30px; margin:25px 0; background:#f8fafc; padding:20px; border-radius:16px;">
                <div class="form-group">
                    <label class="form-label">Tender Reference</label>
                    <select class="form-control" id="po-tender">
                        <option>Select Tender...</option>
                        ${tenders.map(t => `<option value="${t.id}">${t.title}</option>`).join('')}
                    </select>
                </div>
                <div class="form-group">
                    <label class="form-label">PO Date</label>
                    <input type="date" class="form-control" value="${new Date().toISOString().split('T')[0]}">
                </div>
            </div>

            <h3>Line Items (Transactional Grid)</h3>
            <!-- Grid with Combo (3 Marks) -->
            ${Components.renderGrid('order-grid', [
        { key: 'image_url', label: 'Img', type: 'image' },
        { key: 'item_id', label: 'Item (Product)', type: 'combo', source: items },
        { key: 'qty', label: 'Quantity', type: 'number' },
        { key: 'rate', label: 'Rate ($)', type: 'number' },
        { key: 'amount', label: 'Amount', type: 'number', readonly: true }
    ])}
            
            <!-- Totals -->
            <div style="display:flex; justify-content:flex-end; margin-top:20px; font-weight:bold; font-size:16px;">
                <div style="text-align:right;">
                    <div>Subtotal: $<span id="grid-subtotal">0.00</span></div>
                    <div>Tax (18%): $<span id="grid-tax">0.00</span></div>
                    <div style="font-size:20px; margin-top:10px; color:var(--metro-blue);">Grand Total: $<span id="grid-grand">0.00</span></div>
                </div>
            </div>
            
            <button class="btn btn-primary" style="margin-top:20px;" onclick="handleOrderAction('save')">Create Order</button>
        </div>
    `;
    // Add one empty row to start
    Components.gridAddRow('order-grid');
}

window.handleOrderAction = (act) => {
    if (act === 'save') {
        const tid = document.getElementById('po-tender').value;
        if (!tid || tid === 'Select Tender...') {
            alert("Select a Tender first!"); return;
        }
        // Collect items
        const rows = document.querySelectorAll('#order-grid tbody tr');
        let itemsText = [];
        let total = 0;
        rows.forEach(r => {
            const qty = r.querySelector('[data-key="qty"]').value;
            const rate = r.querySelector('[data-key="rate"]').value;
            const iid = r.querySelector('[data-key="item_id"]').value;
            if (qty && iid) {
                itemsText.push(`Item:${iid} Qty:${qty} Rate:${rate}`);
                total += (qty * rate);
            }
        });

        const data = {
            tender_id: parseInt(tid),
            vendor_id: 1, // Default to first vendor for now
            po_number: "PO-" + Math.floor(Math.random() * 10000),
            items: itemsText.join('\n'), // Store as simple text for now
            total_amount: total,
            approved_by: currentUser.username
        };

        api.createPO(data).then(() => {
            Components.showFeedback('Order Created Successfully!');
            loadView('Dashboard');
        });
    } else {
        Components.showFeedback(`${act} clicked`);
    }
};


// --- Other Views ---
async function renderContracts() {
    const tenders = await api.getTenders();
    const content = document.getElementById('main-content');
    const role = currentUser.role.toLowerCase();

    content.innerHTML = `
        <div class="card" style="max-width:800px">
            <h3>Contract Management</h3>
            ${(role === 'admin' || role === 'client') ? `
                <div class="mt-4" style="background:#f9f9f9; padding:15px; border:1px solid #ddd;">
                    <h4>Draft New Contract</h4>
                    <div class="form-group">
                        <label>Select Tender:</label>
                        <select id="con_tender" class="form-control">
                            ${tenders.map(t => `<option value="${t.id}">${t.tender_id} - ${t.title}</option>`).join('')}
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Scope of Work:</label>
                        <textarea id="con_scope" class="form-control" rows="3" placeholder="Enter detailed scope..."></textarea>
                    </div>
                    <button class="btn btn-primary" onclick="handleCreateContract()">Dispatch Contract</button>
                </div>
            ` : '<p>View signed contracts below.</p>'}
            
            <hr>
            <h4>Active Contracts</h4>
            <div id="contracts-list">Loading...</div>
        </div>
    `;
    loadContractsList();
}

async function loadContractsList() {
    const list = await api.getContracts();
    const area = document.getElementById('contracts-list');
    const role = currentUser.role.toLowerCase();

    if (list.length === 0) {
        area.innerHTML = '<i>No contracts found.</i>';
        return;
    }

    area.innerHTML = `
        <table class="sys-grid">
            <thead>
                <tr>
                    <th>Tender #</th>
                    <th>Status</th>
                    <th>Signed Date</th>
                    <th>Action</th>
                </tr>
            </thead>
            <tbody>
                ${list.map(c => `
                    <tr>
                        <td>${c.tender_id}</td>
                        <td><span class="badge ${c.status === 'Signed' ? 'badge-success' : 'badge-warning'}">${c.status}</span></td>
                        <td>${c.signed_date ? new Date(c.signed_date).toLocaleDateString() : 'Pending'}</td>
                        <td>
                            ${(role === 'client' || role === 'vendor') && c.status !== 'Signed' ? `
                                <button class="btn btn-sm" onclick="signContract(${c.id})">Sign Now</button>
                            ` : '---'}
                        </td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

window.signContract = async (id) => {
    await fetch(`/contracts/${id}/sign?signer=${currentUser.username}`, { method: 'PUT' });
    Components.showFeedback("Contract Signed Successfully!");
    loadContractsList();
};

async function renderDelivery() {
    const content = document.getElementById('main-content');
    const contracts = await api.getContracts();

    content.innerHTML = `
        <div class="animate-fade">
            <div class="card glass" style="border-radius:24px;">
                <h3 style="margin-top:0; font-weight:700;">Project Delivery & Milestones</h3>
                <p style="color:var(--text-muted);">Real-time tracking of project progress and compliance.</p>
                
                <div class="form-group" style="max-width:400px; margin:25px 0;">
                    <label class="form-label">Select Contract/Project:</label>
                    <select id="del-contract" class="form-control" style="border-radius:12px;" onchange="loadProjectMilestones(this.value)">
                        <option value="">-- Choose Project --</option>
                        ${contracts.map(c => `<option value="${c.tender_id}">Project #${c.tender_id}</option>`).join('')}
                    </select>
                </div>
                
                <div id="milestone-area" style="min-height:200px; background:#f8fafc; border-radius:16px; padding:20px;">
                    <div style="color:var(--text-muted); text-align:center; padding:40px;">
                        <i class="fa fa-hand-pointer fa-3x" style="opacity:0.1; margin-bottom:15px; display:block;"></i>
                        Select a project above to view and manage milestones.
                    </div>
                </div>
            </div>
        </div>
    `;
}

async function loadProjectMilestones(tenderId) {
    if (!tenderId) return;
    const area = document.getElementById('milestone-area');
    area.innerHTML = '<div style="text-align:center;"><i class="fa fa-spinner fa-spin"></i> Loading Milestones...</div>';

    const ms = await api.getMilestones(tenderId);

    if (ms.length === 0) {
        area.innerHTML = '<div class="alert alert-info">No milestones defined for this project yet.</div>';
        return;
    }

    const role = currentUser.role.toLowerCase();

    area.innerHTML = `
        <table class="sys-grid">
            <thead>
                <tr>
                    <th>Milestone</th>
                    <th>Status</th>
                    <th>Inspection</th>
                    <th>Proof</th>
                    <th>Action</th>
                </tr>
            </thead>
            <tbody>
                ${ms.map(m => `
                    <tr>
                        <td>
                            <b>${m.title}</b><br>
                            <small>${m.description}</small>
                        </td>
                        <td><span class="badge ${m.status === 'Completed' ? 'badge-success' : 'badge-warning'}">${m.status}</span></td>
                        <td>
                             <span class="badge ${m.inspection_status === 'Passed' ? 'badge-success' : m.inspection_status === 'Failed' ? 'badge-error' : 'badge-info'}">
                                ${m.inspection_status}
                             </span>
                             ${m.quality_remarks ? `<br><small>${m.quality_remarks}</small>` : ''}
                        </td>
                        <td>
                            ${m.proof_url ? `<a href="${m.proof_url}" target="_blank">View Proof</a>` : '<i>None</i>'}
                        </td>
                        <td>
                            ${role === 'vendor' && m.status !== 'Completed' ? `
                                <button class="btn btn-sm" onclick="triggerMilestoneUpload(${m.id})">Upload Proof</button>
                            ` : ''}
                            ${(role === 'technical' || role === 'admin') && m.status === 'In Progress' ? `
                                <button class="btn btn-sm btn-primary" onclick="inspectMilestone(${m.id})">Inspect</button>
                            ` : ''}
                        </td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
        <input type="file" id="ms-upload" class="hidden" onchange="handleMilestoneUpload(this)">
    `;
}

window.triggerMilestoneUpload = (id) => {
    window.activeMilestoneId = id;
    document.getElementById('ms-upload').click();
};

window.handleMilestoneUpload = async (input) => {
    if (!input.files[0] || !window.activeMilestoneId) return;
    Components.showFeedback("Uploading proof...");
    try {
        const res = await api.upload(input.files[0]);
        await api.updateMilestone(window.activeMilestoneId, {
            proof_url: res.url,
            status: 'In Progress'
        });
        Components.showFeedback("Proof uploaded! Status: In Progress", "success");
        loadProjectMilestones(document.getElementById('del-contract').value);
    } catch (e) {
        Components.showFeedback("Upload failed", "error");
    }
};

window.inspectMilestone = async (id) => {
    const status = confirm("Does this milestone PASS inspection?") ? "Passed" : "Failed";
    const remarks = prompt("Enter quality remarks:", "");

    await api.updateMilestone(id, {
        inspection_status: status,
        quality_remarks: remarks,
        status: status === 'Passed' ? 'Completed' : 'In Progress'
    });

    Components.showFeedback(`Inspection recorded: ${status}`);
    loadProjectMilestones(document.getElementById('del-contract').value);
};

async function handleCreateContract() {
    const tid = document.getElementById('con_tender').value;
    const scope = document.getElementById('con_scope').value;
    try {
        await api.createContract({
            tender_id: parseInt(tid),
            content: "Standard Agreement",
            scope_of_work: scope,
            start_date: new Date().toISOString(),
            end_date: new Date().toISOString(),
            status: "Draft",
            vetting_status: "Pending",
            dispatch_id: "DSP-" + Math.floor(Math.random() * 1000)
        });
        Components.showFeedback('Contract Created & Dispatched!');
        renderContracts();
    } catch (e) { alert('Error: ' + e); }
}

async function renderPayments() {
    const invoices = await api.getInvoices();
    const payments = await api.getPayments();
    const content = document.getElementById('main-content');
    const role = currentUser.role.toLowerCase();

    content.innerHTML = `
        <div class="animate-fade">
            <div class="card glass" style="border-radius:24px; max-width:1000px;">
                <h3 style="margin-top:0; font-weight:700;">Financial Operations</h3>
                <p style="color:var(--text-muted);">Manage invoices, record payments, and track revenue commissions.</p>
                
                ${(role === 'finance' || role === 'admin') ? `
                    <div style="background:var(--primary-gradient); padding:30px; border-radius:20px; color:white; margin:25px 0;">
                        <h4 style="margin-top:0;">Record Settlement</h4>
                        <div style="display:flex; gap:20px; align-items:flex-end;">
                            <div class="form-group" style="flex:2">
                                <label style="color:rgba(255,255,255,0.8); font-size:0.8rem;">SELECT INVOICE</label>
                                <select id="pay_inv" class="form-control" style="background:rgba(255,255,255,0.1); border:1px solid rgba(255,255,255,0.2); color:white; border-radius:12px;">
                                    ${invoices.map(i => `<option value="${i.id}" style="color:black;">${i.invoice_number} - $${i.total_payable} (${i.status})</option>`).join('')}
                                </select>
                            </div>
                            <div class="form-group" style="flex:1">
                                <label style="color:rgba(255,255,255,0.8); font-size:0.8rem;">AMOUNT RECEIVED ($)</label>
                                <input id="pay_amt" type="number" class="form-control" style="background:rgba(255,255,255,0.1); border:1px solid rgba(255,255,255,0.2); color:white; border-radius:12px;">
                            </div>
                            <button class="btn-primary" onclick="handlePayment()" style="background:white; color:var(--accent-blue); height:45px; margin-bottom:15px;">
                                CONFIRM PAYMENT
                            </button>
                        </div>
                    </div>
                ` : ''}

                <h4 style="font-weight:700; color:var(--text-main);">Transaction History</h4>
                <div class="grid-container" style="border:none;">
                    <table class="sys-grid">
                        <thead>
                            <tr>
                                <th>Date</th>
                                <th>Reference</th>
                                <th>Amount</th>
                                <th>Commission</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${payments.length === 0 ? '<tr><td colspan="5" style="text-align:center; padding:40px; color:var(--text-muted);">No transactions found.</td></tr>' :
            payments.map(p => `
                                <tr>
                                    <td><b>${new Date(p.payment_date).toLocaleDateString()}</b></td>
                                    <td>Settlement for Inv #${p.invoice_id}</td>
                                    <td style="color:var(--accent-green); font-weight:700;">$${p.amount_paid.toLocaleString()}</td>
                                    <td style="color:var(--text-muted);">$${p.commission_amount.toLocaleString()}</td>
                                    <td><span class="badge badge-success">${p.status}</span></td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    `;
}

async function handlePayment() {
    const iid = document.getElementById('pay_inv').value;
    const amt = parseFloat(document.getElementById('pay_amt').value);
    if (!amt) return;
    try {
        await api.createPayment({
            invoice_id: parseInt(iid),
            amount_paid: amt,
            payment_mode: "Bank Transfer",
            commission_amount: amt * 0.10
        });
        Components.showFeedback('Payment Recorded!');
        renderPayments();
    } catch (e) { alert('Error'); }
}

// Helpers
window.uploadTenderImg = async (input) => {
    if (input.files[0]) {
        const res = await api.upload(input.files[0]);
        window.tempTenderImg = res.url;
        document.getElementById('tender-img').style.backgroundImage = `url(${res.url})`;
        document.getElementById('tender-img').innerText = '';
    }
};

// Start
init();
