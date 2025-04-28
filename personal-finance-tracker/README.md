# Personal Finance Tracker

A comprehensive web application to track your personal finances, including bank accounts, credit cards, Demat holdings, loan accounts, and transactions.

## Features

- **Dashboard**: View a complete overview of your financial status with visualizations
- **Bank Accounts**: Manage your bank accounts and track balances
- **Credit Cards**: Monitor credit card debt, due dates, and utilization
- **Demat Holdings**: Track your stock investments and portfolio performance  
- **Loan Accounts**: Manage loan details and monitor repayment progress
- **Transactions**: Record and analyze income and expenses

## Screenshots

![Dashboard](screenshots/dashboard.png)
![Bank Accounts](screenshots/bank_accounts.png)
![Loan Accounts](screenshots/loan_accounts.png)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/personal-finance-tracker.git
cd personal-finance-tracker
```

2. Create a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the Streamlit application:
```bash
streamlit run app.py
```

2. Open your web browser and navigate to:
```
http://localhost:8501
```

## Data Storage

All data is stored locally in JSON files within the `data` directory:
- Bank accounts: `data/bank_accounts.json`
- Credit cards: `data/credit_cards.json`
- Demat holdings: `data/demat_holdings.json`
- Loan accounts: `data/loan_accounts.json`
- Transactions: `data/transactions.json`

## Requirements

- Python 3.7+
- pandas
- plotly
- streamlit
- yfinance

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.