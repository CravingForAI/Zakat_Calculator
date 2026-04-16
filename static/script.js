// JavaScript code for interactive Zakat calculator

// Function to calculate the Zakat
function calculateZakat() {
    const totalWealth = document.getElementById('totalWealth').value;
    const zakatRate = 0.025; // 2.5% Zakat rate
    const zakatAmount = totalWealth * zakatRate;

    document.getElementById('result').innerText = `Zakat Amount: $${zakatAmount.toFixed(2)}`;
}

// Example API call to fetch the latest gold prices (for calculation)
async function fetchGoldPrice() {
    try {
        const response = await fetch('https://api.example.com/gold-price'); // Replace with a valid API
        const data = await response.json();
        console.log('Current Gold Price:', data.price);
    } catch (error) {
        console.error('Error fetching gold price:', error);
    }
}

// Event listener for the calculate button
document.getElementById('calculateBtn').addEventListener('click', calculateZakat);

// Call the function to fetch gold prices on load
fetchGoldPrice();