document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.getElementById('product-search');
    const resultsContainer = document.getElementById('search-results');
    const cartContainer = document.getElementById('cart-items');
    const subtotalEl = document.getElementById('cart-subtotal');
    const totalEl = document.getElementById('cart-total');
    const taxEl = document.getElementById('cart-tax');
    const discountInput = document.getElementById('bill-discount');
    const checkoutBtn = document.getElementById('btn-checkout');
    const minSearchLength = 2;

    let cart = [];
    let initialResults = null;

    const manualAddBtn = document.getElementById('manualAddBtn');
    const manualNameInput = document.getElementById('manualName');
    const manualPriceInput = document.getElementById('manualPrice');
    const manualQtyInput = document.getElementById('manualQty');
    const customerPhoneInput = document.getElementById('customerPhone');

    // Init Customers
    const customerList = document.getElementById('customerList');
    const customerRecords = Array.isArray(window.customersData) ? window.customersData : [];
    if (customerList && customerRecords.length) {
        customerRecords.forEach(c => {
            const option = document.createElement('option');
            option.value = c.phone;
            option.textContent = `${c.name} (${c.phone})`;
            customerList.appendChild(option);
        });
    }

    function fillCustomerDetails(phone) {
        const customer = customerRecords.find(c => c.phone === phone);
        if (customer) {
            document.getElementById('customerName').value = customer.name;
        }
    }

    function addManualItem() {
        const name = document.getElementById('manualName').value;
        const price = parseFloat(document.getElementById('manualPrice').value);
        const qty = parseInt(document.getElementById('manualQty').value);

        if (!name || isNaN(price) || isNaN(qty) || price <= 0 || qty <= 0) {
            alert('Please enter valid item details');
            return;
        }

        const existingItem = cart.find(item => item.type === 'manual' && item.name === name && item.price === price);
        if (existingItem) {
            existingItem.quantity += qty;
        } else {
            cart.push({
                type: 'manual',
                id: 'MANUAL_' + Date.now(), // Temp ID
                name: name,
                price: price,
                quantity: qty,
                stock: 9999, // Infinite
                tax: 0
            });
        }

        document.getElementById('manualName').value = '';
        document.getElementById('manualPrice').value = '';
        document.getElementById('manualQty').value = 1;
        document.getElementById('manualName').focus();

        renderCart();
    }

    if (manualAddBtn) {
        manualAddBtn.addEventListener('click', addManualItem);
    }
    [manualNameInput, manualPriceInput, manualQtyInput].forEach(input => {
        if (!input) return;
        input.addEventListener('keydown', (event) => {
            if (event.key === 'Enter') {
                event.preventDefault();
                addManualItem();
            }
        });
    });
    if (customerPhoneInput) {
        customerPhoneInput.addEventListener('change', () => fillCustomerDetails(customerPhoneInput.value));
    }

    function renderResults(products, emptyMessage) {
        resultsContainer.innerHTML = '';
        if (!products || products.length === 0) {
            const message = emptyMessage || 'No products found.';
            resultsContainer.innerHTML = `
                <div style="grid-column: 1/-1; text-align: center; color: #aaa; margin-top: 2rem;">
                    ${message}
                </div>
            `;
            return;
        }
        products.forEach(p => {
            const card = document.createElement('div');
            card.className = 'product-card';
            card.style.cssText = 'border: 1px solid #eee; padding: 1rem; border-radius: 8px; cursor: pointer; transition: all 0.2s;';
            card.innerHTML = `
                <div style="font-weight: 600;">${p.name}</div>
                <div style="font-size: 0.8rem; color: #666;">${p.brand}</div>
                <div style="display: flex; justify-content: space-between; margin-top: 0.5rem;">
                    <span style="color: var(--primary); font-weight: 700;">Rs. ${p.price}</span>
                    <span style="font-size: 0.8rem; background: #e0f2f1; padding: 2px 6px; border-radius: 4px;">Stock: ${p.stock}</span>
                </div>
            `;
            card.addEventListener('click', () => addToCart(p));
            resultsContainer.appendChild(card);
        });
    }

    function fetchProducts(query, emptyMessage) {
        const encoded = encodeURIComponent(query || '');
        return fetch(`/sales/api/search/?q=${encoded}`)
            .then(res => res.json())
            .then(data => {
                const results = data.results || [];
                renderResults(results, emptyMessage);
                return results;
            })
            .catch(() => {
                renderResults([], 'Unable to load products.');
                return [];
            });
    }

    function loadInitialResults() {
        return fetchProducts('', 'No products available.').then(results => {
            initialResults = results;
        });
    }

    // Load initial products so the list isn't empty
    loadInitialResults();

    // Search Logic
    searchInput.addEventListener('input', debounce(function (e) {
        const query = e.target.value.trim();
        if (query.length === 0) {
            if (initialResults) {
                renderResults(initialResults, 'No products available.');
                return;
            }
            loadInitialResults();
            return;
        }
        if (query.length < minSearchLength) return;

        fetchProducts(query, 'No matching products.');
    }, 400));

    function addToCart(product) {
        const existing = cart.find(item => item.id === product.id);
        if (existing) {
            existing.quantity++;
        } else {
            cart.push({
                ...product,
                quantity: 1,
                userPrice: product.price // Allow override later
            });
        }
        renderCart();
    }

    function renderCart() {
        cartContainer.innerHTML = '';
        let subtotal = 0;
        let taxTotal = 0;

        cart.forEach((item, index) => {
            const row = document.createElement('div');
            row.style.cssText = 'display: flex; justify-content: space-between; align-items: center; padding: 0.5rem 0; border-bottom: 1px solid #f8f9fa;';

            // Manual items fallback
            const price = item.price || item.userPrice;
            const tax = item.tax || 0;
            const itemTotal = item.quantity * price;

            subtotal += itemTotal;
            taxTotal += itemTotal * (tax / 100);

            row.innerHTML = `
                <div style="flex: 2;">
                    <div style="font-weight: 500;">${item.name} ${item.type === 'manual' ? ' (Manual)' : ''}</div>
                    <div style="font-size: 0.8rem; color: #888;">@ ${price}</div>
                </div>
                <div style="flex: 1; display: flex; align-items: center; gap: 5px;">
                    <button onclick="updateQty(${index}, -1)" style="padding: 2px 6px;">-</button>
                    <span>${item.quantity}</span>
                    <button onclick="updateQty(${index}, 1)" style="padding: 2px 6px;">+</button>
                </div>
                <div style="flex: 1; text-align: right; font-weight: 600;">
                    ${itemTotal.toFixed(2)}
                </div>
            `;
            cartContainer.appendChild(row);
        });

        // Totals
        const discount = parseFloat(discountInput.value) || 0;
        const total = subtotal + taxTotal - discount;

        subtotalEl.textContent = subtotal.toFixed(2);
        taxEl.textContent = taxTotal.toFixed(2);
        totalEl.textContent = total.toFixed(2);

        // Expose data for checkout
        window.currentCartData = {
            sub_total: subtotal,
            tax_total: taxTotal,
            grand_total: total,
            items: cart.map(c => ({
                type: c.type || 'product',
                product_id: c.type === 'manual' ? null : c.id,
                name: c.name,
                quantity: c.quantity,
                price: c.price || c.userPrice,
                discount_percentage: 0,
                discount_amount: 0,
                tax_amount: (c.quantity * (c.price || c.userPrice)) * ((c.tax || 0) / 100),
                total: (c.quantity * (c.price || c.userPrice))
            }))
        };
    }

    // Global helpers for inline onclick
    window.updateQty = function (index, change) {
        cart[index].quantity += change;
        if (cart[index].quantity <= 0) {
            cart.splice(index, 1);
        }
        renderCart();
    };

    // Checkout Logic
    checkoutBtn.addEventListener('click', function () {
        console.log("Checkout button clicked");
        if (cart.length === 0) return alert("Cart is empty!");

        // Show processing state
        const originalText = checkoutBtn.innerText;
        checkoutBtn.innerText = "Processing...";
        checkoutBtn.disabled = true;

        const cName = document.getElementById('customerName') ? document.getElementById('customerName').value : '';
        const cPhone = document.getElementById('customerPhone') ? document.getElementById('customerPhone').value : '';

        const payload = {
            ...window.currentCartData,
            customer_name: cName,
            customer_phone: cPhone,
            payment_mode: document.getElementById('payment-mode').value,
            discount_amount: document.getElementById('bill-discount').value
        };

        console.log("Sending payload:", payload);

        fetch('/sales/api/create/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
            .then(res => {
                console.log("Response status:", res.status);
                return res.json();
            })
            .then(data => {
                console.log("Response data:", data);
                if (data.status === 'success') {
                    // Redirect to Print
                    window.location.href = `/sales/invoice/${data.invoice_id}/print/`;
                } else {
                    alert('Error: ' + data.message);
                    checkoutBtn.innerText = originalText;
                    checkoutBtn.disabled = false;
                }
            })
            .catch(err => {
                console.error("Fetch error:", err);
                alert('Network error: ' + err);
                checkoutBtn.innerText = originalText;
                checkoutBtn.disabled = false;
            });
    });

    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
});
