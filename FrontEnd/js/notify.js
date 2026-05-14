// notify.js – replaces browser alert() / confirm() with styled in-page UI

// ── TOAST ────────────────────────────────────────────────────────────────────
let _container = null;

function _getContainer() {
    if (!_container) {
        _container = document.createElement('div');
        _container.style.cssText = [
            'position:fixed', 'top:1.25rem', 'right:1.25rem',
            'z-index:9999', 'display:flex', 'flex-direction:column',
            'gap:0.5rem', 'pointer-events:none', 'max-width:380px', 'width:90%'
        ].join(';');
        document.body.appendChild(_container);

        const style = document.createElement('style');
        style.textContent = `
            @keyframes _toast-in  { from { transform:translateX(110%); opacity:0 } to { transform:translateX(0); opacity:1 } }
            @keyframes _toast-out { from { opacity:1 } to { opacity:0; transform:translateX(110%) } }
            ._toast { animation: _toast-in 0.22s cubic-bezier(.16,1,.3,1) both }
            ._toast._hiding { animation: _toast-out 0.2s ease forwards }
        `;
        document.head.appendChild(style);
    }
    return _container;
}

const _PALETTES = {
    error:   { bg:'#fee2e2', border:'#fca5a5', text:'#b91c1c', icon:'<svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>' },
    success: { bg:'#dcfce7', border:'#86efac', text:'#15803d', icon:'<svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><polyline points="9 12 11 14 15 10"/></svg>' },
    warning: { bg:'#fef9c3', border:'#fde047', text:'#854d0e', icon:'<svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>' },
    info:    { bg:'#dbeafe', border:'#93c5fd', text:'#1d4ed8', icon:'<svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>' },
};

/**
 * Show a toast notification.
 * @param {string} message
 * @param {'error'|'success'|'warning'|'info'} [type='error']
 * @param {number} [duration=4500]  ms before auto-dismiss
 */
export function showToast(message, type = 'error', duration = 4500) {
    const c = _PALETTES[type] || _PALETTES.error;

    const toast = document.createElement('div');
    toast.className = '_toast';
    toast.style.cssText = [
        `background:${c.bg}`, `border:1px solid ${c.border}`, `color:${c.text}`,
        'padding:0.75rem 0.875rem', 'border-radius:0.75rem',
        'box-shadow:0 4px 16px rgba(0,0,0,0.10)',
        'display:flex', 'align-items:flex-start', 'gap:0.5rem',
        'font-size:0.875rem', 'font-weight:500', 'line-height:1.5',
        'pointer-events:auto', 'width:100%', 'box-sizing:border-box'
    ].join(';');

    const closeBtn = `<button onclick="this.closest('._toast')._dismiss()" style="margin-left:auto;flex-shrink:0;background:none;border:none;cursor:pointer;color:${c.text};font-size:1.1rem;line-height:1;padding:0 0 0 0.5rem;opacity:0.7;" aria-label="Zamknij">×</button>`;
    toast.innerHTML = `<span style="flex-shrink:0;margin-top:1px;">${c.icon}</span><span style="flex:1;">${message}</span>${closeBtn}`;

    const dismiss = () => {
        toast.classList.add('_hiding');
        toast.addEventListener('animationend', () => toast.remove(), { once: true });
    };
    toast._dismiss = dismiss;

    _getContainer().appendChild(toast);

    const timer = setTimeout(dismiss, duration);
    toast.querySelector('button').addEventListener('click', () => clearTimeout(timer));
}

// ── CONFIRM DIALOG ───────────────────────────────────────────────────────────
/**
 * Show a styled confirm dialog. Returns a Promise<boolean>.
 * @param {string} message
 * @param {{ confirmLabel?: string, cancelLabel?: string, danger?: boolean }} [opts]
 */
export function showConfirm(message, opts = {}) {
    const {
        confirmLabel = 'Potwierdź',
        cancelLabel  = 'Anuluj',
        danger       = true,
    } = opts;

    return new Promise(resolve => {
        const overlay = document.createElement('div');
        overlay.style.cssText = [
            'position:fixed', 'inset:0',
            'background:rgba(0,0,0,0.55)',
            'backdrop-filter:blur(2px)',
            'z-index:10000',
            'display:flex', 'align-items:center', 'justify-content:center',
            'padding:1rem'
        ].join(';');

        const box = document.createElement('div');
        box.style.cssText = [
            'background:#1e293b', 'border:1px solid #334155',
            'border-radius:1rem', 'padding:1.5rem',
            'max-width:420px', 'width:100%',
            'color:#e2e8f0',
            'box-shadow:0 20px 60px rgba(0,0,0,0.5)',
            'font-size:0.9375rem', 'line-height:1.6'
        ].join(';');

        const btnOk  = danger  ? 'background:#ef4444;color:#fff;border:none;'
                                : 'background:#2563eb;color:#fff;border:none;';
        const btnCss = 'padding:0.5rem 1.25rem;border-radius:0.5rem;cursor:pointer;font-size:0.875rem;font-weight:600;';

        box.innerHTML = `
            <p style="margin:0 0 1.25rem;">${message}</p>
            <div style="display:flex;gap:0.75rem;justify-content:flex-end;">
                <button id="_c-cancel" style="${btnCss}background:#334155;color:#cbd5e1;border:1px solid #475569;">${cancelLabel}</button>
                <button id="_c-ok"     style="${btnCss}${btnOk}">${confirmLabel}</button>
            </div>
        `;

        overlay.appendChild(box);
        document.body.appendChild(overlay);

        const done = (val) => { overlay.remove(); resolve(val); };
        box.querySelector('#_c-ok').addEventListener('click', () => done(true));
        box.querySelector('#_c-cancel').addEventListener('click', () => done(false));
        overlay.addEventListener('click', e => { if (e.target === overlay) done(false); });
    });
}
