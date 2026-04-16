const GOLD_NISAB_GRAMS = 87.48;
const SILVER_NISAB_GRAMS = 612.36;
const ZAKAT_RATE = 0.025;
const FALLBACK_PRICES = {
    gold_price_aed: 572.50,
    silver_price_aed: 4.80
};

let currentPrices = { ...FALLBACK_PRICES, source: 'fallback' };

const formatAED = (value) =>
    new Intl.NumberFormat('en-AE', {
        style: 'currency',
        currency: 'AED',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(Number.isFinite(value) ? value : 0);

const parseInput = (id) => {
    const value = parseFloat(document.getElementById(id).value);
    return Number.isFinite(value) && value > 0 ? value : 0;
};

function getSelectedNisabType() {
    return document.querySelector('input[name="nisabType"]:checked').value;
}

function calculateNisabThreshold(nisabType) {
    return nisabType === 'silver'
        ? SILVER_NISAB_GRAMS * currentPrices.silver_price_aed
        : GOLD_NISAB_GRAMS * currentPrices.gold_price_aed;
}

function updateConvertedValues() {
    const goldValue = parseInput('goldGrams') * currentPrices.gold_price_aed;
    const silverValue = parseInput('silverGrams') * currentPrices.silver_price_aed;

    document.getElementById('goldValue').value = goldValue.toFixed(2);
    document.getElementById('silverValue').value = silverValue.toFixed(2);

    const nisabThreshold = calculateNisabThreshold(getSelectedNisabType());
    document.getElementById('nisabThreshold').textContent = formatAED(nisabThreshold);
}

async function fetchPrices() {
    try {
        const response = await fetch('/api/prices');
        if (!response.ok) throw new Error('Price request failed');

        const data = await response.json();
        currentPrices = {
            gold_price_aed: Number(data.gold_price_aed) || FALLBACK_PRICES.gold_price_aed,
            silver_price_aed: Number(data.silver_price_aed) || FALLBACK_PRICES.silver_price_aed,
            source: data.source || 'live'
        };

        document.getElementById('priceSource').textContent =
            currentPrices.source === 'fallback' ? 'Fallback prices in use' : 'Live prices updated';
    } catch (error) {
        currentPrices = { ...FALLBACK_PRICES, source: 'fallback' };
        document.getElementById('priceSource').textContent = 'Using fallback prices';
    }

    document.getElementById('goldPrice').textContent = formatAED(currentPrices.gold_price_aed);
    document.getElementById('silverPrice').textContent = formatAED(currentPrices.silver_price_aed);
    updateConvertedValues();
}

function displayResults(result) {
    const summary = document.getElementById('resultSummary');
    const breakdown = document.getElementById('resultBreakdown');
    const statusClass = result.isZakatable ? 'status-pass' : 'status-fail';
    const statusText = result.isZakatable ? 'Above Nisab (Zakat is due)' : 'Below Nisab (No Zakat due)';

    summary.innerHTML = `
        <div><strong>Net Wealth:</strong> ${formatAED(result.netWealth)}</div>
        <div><strong>Nisab Threshold:</strong> ${formatAED(result.nisabThreshold)}</div>
        <div><strong>Status:</strong> <span class="${statusClass}">${statusText}</span></div>
        <div><strong>Zakat Due (2.5%):</strong> ${formatAED(result.zakatDue)}</div>
    `;

    breakdown.innerHTML = [
        `Cash: ${formatAED(result.cash)}`,
        `Gold Value: ${formatAED(result.goldValue)}`,
        `Silver Value: ${formatAED(result.silverValue)}`,
        `Property Value: ${formatAED(result.propertyValue)}`,
        `Investments: ${formatAED(result.investments)}`,
        `Total Assets: ${formatAED(result.totalAssets)}`,
        `Debts: ${formatAED(result.debts)}`
    ].map((line) => `<li>${line}</li>`).join('');

    document.getElementById('results').style.display = 'block';
}

function calculateZakat() {
    const cash = parseInput('cash');
    const goldGrams = parseInput('goldGrams');
    const silverGrams = parseInput('silverGrams');
    const propertyValue = parseInput('propertyValue');
    const investments = parseInput('investments');
    const debts = parseInput('debts');

    const goldValue = goldGrams * currentPrices.gold_price_aed;
    const silverValue = silverGrams * currentPrices.silver_price_aed;

    const totalAssets = cash + goldValue + silverValue + propertyValue + investments;
    const netWealth = Math.max(0, totalAssets - debts);

    const nisabType = getSelectedNisabType();
    const nisabThreshold = calculateNisabThreshold(nisabType);
    const isZakatable = netWealth >= nisabThreshold;
    const zakatDue = isZakatable ? netWealth * ZAKAT_RATE : 0;

    displayResults({
        cash,
        goldValue,
        silverValue,
        propertyValue,
        investments,
        debts,
        totalAssets,
        netWealth,
        nisabThreshold,
        isZakatable,
        zakatDue
    });
}

function resetForm() {
    document.querySelectorAll('input[type="number"]').forEach((input) => {
        input.value = input.readOnly ? '0.00' : '0';
    });
    document.querySelector('input[name="nisabType"][value="gold"]').checked = true;
    document.getElementById('results').style.display = 'none';
    updateConvertedValues();
}

document.addEventListener('DOMContentLoaded', () => {
    const watchedFields = ['cash', 'goldGrams', 'silverGrams', 'propertyValue', 'investments', 'debts'];
    watchedFields.forEach((fieldId) => {
        document.getElementById(fieldId).addEventListener('input', updateConvertedValues);
    });

    document.querySelectorAll('input[name="nisabType"]').forEach((radio) => {
        radio.addEventListener('change', updateConvertedValues);
    });

    document.getElementById('calculateBtn').addEventListener('click', calculateZakat);
    document.getElementById('resetBtn').addEventListener('click', resetForm);

    fetchPrices();
    const priceRefreshInterval = setInterval(fetchPrices, 5 * 60 * 1000);
    window.priceRefreshInterval = priceRefreshInterval;
});
