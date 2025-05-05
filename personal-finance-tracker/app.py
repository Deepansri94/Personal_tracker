import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os
from datetime import datetime, timedelta

# Set page configuration
st.set_page_config(
    page_title="Personal Finance Tracker",
    page_icon="💰",
    layout="wide"
)

# ======= Session State Initialization =======
def initialize_session_state():
    if 'bank_accounts' not in st.session_state:
        st.session_state.bank_accounts = []
        if os.path.exists('data/bank_accounts.json'):
            with open('data/bank_accounts.json', 'r') as f:
                st.session_state.bank_accounts = json.load(f)
    
    if 'credit_cards' not in st.session_state:
        st.session_state.credit_cards = []
        if os.path.exists('data/credit_cards.json'):
            with open('data/credit_cards.json', 'r') as f:
                st.session_state.credit_cards = json.load(f)
    
    if 'demat_holdings' not in st.session_state:
        st.session_state.demat_holdings = []
        if os.path.exists('data/demat_holdings.json'):
            with open('data/demat_holdings.json', 'r') as f:
                st.session_state.demat_holdings = json.load(f)
    
    if 'loan_accounts' not in st.session_state:
        st.session_state.loan_accounts = []
        if os.path.exists('data/loan_accounts.json'):
            with open('data/loan_accounts.json', 'r') as f:
                st.session_state.loan_accounts = json.load(f)
    
    if 'transactions' not in st.session_state:
        st.session_state.transactions = []
        if os.path.exists('data/transactions.json'):
            with open('data/transactions.json', 'r') as f:
                st.session_state.transactions = json.load(f)
    
    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = 0

# Initialize session state
initialize_session_state()

# Ensure data directory exists
os.makedirs('data', exist_ok=True)

# ======= Helper Functions =======
def save_data(data_type):
    """Save data to JSON file"""
    if data_type == 'bank_accounts':
        with open('data/bank_accounts.json', 'w') as f:
            json.dump(st.session_state.bank_accounts, f)
    elif data_type == 'credit_cards':
        with open('data/credit_cards.json', 'w') as f:
            json.dump(st.session_state.credit_cards, f)
    elif data_type == 'demat_holdings':
        with open('data/demat_holdings.json', 'w') as f:
            json.dump(st.session_state.demat_holdings, f)
    elif data_type == 'loan_accounts':
        with open('data/loan_accounts.json', 'w') as f:
            json.dump(st.session_state.loan_accounts, f)
    elif data_type == 'transactions':
        with open('data/transactions.json', 'w') as f:
            json.dump(st.session_state.transactions, f)

def calculate_net_worth():
    """Calculate total net worth"""
    # Sum of bank balances
    bank_balance = sum(float(account['balance']) for account in st.session_state.bank_accounts)
    
    # Demat holdings value
    demat_value = sum(float(holding['current_value']) for holding in st.session_state.demat_holdings)
    
    # Credit card debt
    credit_debt = sum(float(card['outstanding_amount']) for card in st.session_state.credit_cards)
    
    # Loan debt
    loan_debt = sum(float(loan['outstanding_amount']) for loan in st.session_state.loan_accounts)
    
    # Net worth
    net_worth = bank_balance + demat_value - credit_debt - loan_debt
    
    return {
        'bank_balance': bank_balance,
        'demat_value': demat_value,
        'credit_debt': credit_debt,
        'loan_debt': loan_debt,
        'net_worth': net_worth
    }

def get_transaction_balance_trend():
    """Calculate account balance trend based on transactions"""
    if not st.session_state.transactions:
        return pd.DataFrame({'date': [], 'balance': []})
    
    # Convert transactions to DataFrame
    df = pd.DataFrame(st.session_state.transactions)
    if 'date' not in df.columns or df.empty:
        return pd.DataFrame({'date': [], 'balance': []})
    
    # Convert date strings to datetime
    df['date'] = pd.to_datetime(df['date'])
    
    # Sort by date
    df = df.sort_values('date')
    
    # Create running balance
    df['amount'] = df.apply(lambda x: float(x['amount']) if x['type'] == 'deposit' else -float(x['amount']), axis=1)
    df['balance'] = df['amount'].cumsum()
    
    # Select only necessary columns
    return df[['date', 'balance']]

# ======= App UI =======
# App title and description
st.title("Personal Finance Tracker")
st.markdown("""
This application helps you track your bank accounts, credit cards, and Demat holdings,
giving you a comprehensive view of your financial status.
""")

# Main navigation
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Dashboard", 
    "🏦 Bank Accounts", 
    "💳 Credit Cards", 
    "📈 Demat Holdings",
    "🏠 Loan Accounts",
    "💰 Transactions"
])

# Tab 1: Dashboard
with tab1:
    st.header("Financial Dashboard")
    
    # Calculate net worth
    financial_summary = calculate_net_worth()
    
    # Display summary metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Bank Balance", f"₹{financial_summary['bank_balance']:,.2f}")
    
    with col2:
        st.metric("Demat Portfolio Value", f"₹{financial_summary['demat_value']:,.2f}")
    
    with col3:
        st.metric("Credit Card Debt", f"₹{financial_summary['credit_debt']:,.2f}")
    
    with col4:
        st.metric("Loan Debt", f"₹{financial_summary['loan_debt']:,.2f}")
    
    with col5:
        st.metric("Net Worth", f"₹{financial_summary['net_worth']:,.2f}")
    
    # Asset allocation chart
    st.subheader("Asset Allocation")
    
    if financial_summary['bank_balance'] > 0 or financial_summary['demat_value'] > 0:
        asset_data = {
            'Category': ['Bank Accounts', 'Demat Holdings'],
            'Value': [financial_summary['bank_balance'], financial_summary['demat_value']]
        }
        
        df_assets = pd.DataFrame(asset_data)
        
        fig = px.pie(
            df_assets, 
            values='Value', 
            names='Category',
            title='Asset Allocation',
            color_discrete_sequence=px.colors.sequential.Aggrnyl
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Add bank accounts and investments to view asset allocation")
        
    # Liabilities chart
    st.subheader("Liabilities")
    
    if financial_summary['credit_debt'] > 0 or financial_summary['loan_debt'] > 0:
        liability_data = {
            'Category': ['Credit Card Debt', 'Loan Debt'],
            'Value': [financial_summary['credit_debt'], financial_summary['loan_debt']]
        }
        
        df_liabilities = pd.DataFrame(liability_data)
        
        fig = px.pie(
            df_liabilities, 
            values='Value', 
            names='Category',
            title='Liabilities Distribution',
            color_discrete_sequence=px.colors.sequential.Reds
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Add credit cards and loans to view liabilities distribution")
    
    # Account balance trend
    st.subheader("Account Balance Trend")
    balance_trend = get_transaction_balance_trend()
    
    if not balance_trend.empty and 'date' in balance_trend.columns and 'balance' in balance_trend.columns:
        fig = px.line(
            balance_trend, 
            x='date', 
            y='balance',
            title='Account Balance Over Time',
            labels={'date': 'Date', 'balance': 'Balance (₹)'}
        )
        fig.update_traces(line=dict(color="#2E86C1", width=3))
        fig.update_layout(hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Add transactions to view balance trend")
    
    # Bank accounts overview
    st.subheader("Bank Accounts Overview")
    if st.session_state.bank_accounts:
        df_banks = pd.DataFrame(st.session_state.bank_accounts)
        fig = px.bar(
            df_banks, 
            x='bank_name', 
            y='balance',
            color='account_type',
            title='Bank Account Balances',
            labels={'bank_name': 'Bank', 'balance': 'Balance (₹)', 'account_type': 'Account Type'}
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Add bank accounts to view their overview")
    
    # Demat holdings overview
    st.subheader("Portfolio Performance")
    if st.session_state.demat_holdings:
        df_holdings = pd.DataFrame(st.session_state.demat_holdings)
        df_holdings['profit_loss'] = df_holdings.apply(
            lambda x: float(x['current_value']) - float(x['purchase_value']), 
            axis=1
        )
        df_holdings['profit_loss_percent'] = df_holdings.apply(
            lambda x: (float(x['current_value']) - float(x['purchase_value'])) / float(x['purchase_value']) * 100, 
            axis=1
        )
        
        fig = px.bar(
            df_holdings, 
            x='stock_name', 
            y='profit_loss',
            color='profit_loss_percent',
            color_continuous_scale=['red', 'green'],
            range_color=[-10, 10],
            title='Profit/Loss by Stock',
            labels={
                'stock_name': 'Stock', 
                'profit_loss': 'Profit/Loss (₹)', 
                'profit_loss_percent': 'Profit/Loss (%)'
            }
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Add Demat holdings to view portfolio performance")

# Tab 2: Bank Accounts
with tab2:
    st.header("Bank Accounts")
    
    # Add new bank account
    with st.expander("Add New Bank Account", expanded=False):
        with st.form("bank_account_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                bank_name = st.text_input("Bank Name")
                account_number = st.text_input("Account Number (Last 4 digits)")
                balance = st.number_input("Current Balance", min_value=0.0, format="%.2f")
            
            with col2:
                account_type = st.selectbox(
                    "Account Type",
                    ["Savings", "Current", "Fixed Deposit", "Recurring Deposit", "Other"]
                )
                interest_rate = st.number_input("Interest Rate (%)", min_value=0.0, max_value=20.0, format="%.2f")
                notes = st.text_area("Notes", height=100)
            
            submitted = st.form_submit_button("Add Bank Account")
            
            if submitted and bank_name and account_number:
                new_account = {
                    "bank_name": bank_name,
                    "account_number": account_number,
                    "account_type": account_type,
                    "balance": str(balance),
                    "interest_rate": str(interest_rate),
                    "notes": notes,
                    "last_updated": datetime.now().strftime("%Y-%m-%d")
                }
                
                st.session_state.bank_accounts.append(new_account)
                save_data('bank_accounts')
                st.success(f"Added {bank_name} account ending with {account_number}")
                st.rerun()
    
    # Display bank accounts
    if st.session_state.bank_accounts:
        for i, account in enumerate(st.session_state.bank_accounts):
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 1, 1])
                
                with col1:
                    st.markdown(f"**{account['bank_name']}**")
                    st.caption(f"A/C ending with {account['account_number']}")
                
                with col2:
                    st.markdown(f"**Balance: ₹{float(account['balance']):,.2f}**")
                    st.caption(f"Type: {account['account_type']}")
                
                with col3:
                    st.markdown(f"Interest Rate: {account['interest_rate']}%")
                    st.caption(f"Last updated: {account['last_updated']}")
                
                with col4:
                    if st.button("Edit", key=f"edit_bank_{i}"):
                        st.session_state.edit_bank_index = i
                        st.rerun()
                
                with col5:
                    if st.button("Delete", key=f"delete_bank_{i}"):
                        st.session_state.bank_accounts.pop(i)
                        save_data('bank_accounts')
                        st.success("Account deleted successfully")
                        st.rerun()
                
                st.divider()
        
        # Edit bank account
        if 'edit_bank_index' in st.session_state:
            i = st.session_state.edit_bank_index
            account = st.session_state.bank_accounts[i]
            
            st.subheader(f"Edit {account['bank_name']} Account")
            
            with st.form("edit_bank_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    bank_name = st.text_input("Bank Name", value=account['bank_name'])
                    account_number = st.text_input("Account Number", value=account['account_number'])
                    balance = st.number_input(
                        "Current Balance", 
                        min_value=0.0, 
                        value=float(account['balance']),
                        format="%.2f"
                    )
                
                with col2:
                    account_type = st.selectbox(
                        "Account Type",
                        ["Savings", "Current", "Fixed Deposit", "Recurring Deposit", "Other"],
                        index=["Savings", "Current", "Fixed Deposit", "Recurring Deposit", "Other"].index(account['account_type'])
                    )
                    interest_rate = st.number_input(
                        "Interest Rate (%)", 
                        min_value=0.0, 
                        max_value=20.0, 
                        value=float(account['interest_rate']),
                        format="%.2f"
                    )
                    notes = st.text_area("Notes", value=account.get('notes', ''), height=100)
                
                update_submitted = st.form_submit_button("Update Bank Account")
                
                if update_submitted:
                    updated_account = {
                        "bank_name": bank_name,
                        "account_number": account_number,
                        "account_type": account_type,
                        "balance": str(balance),
                        "interest_rate": str(interest_rate),
                        "notes": notes,
                        "last_updated": datetime.now().strftime("%Y-%m-%d")
                    }
                    
                    st.session_state.bank_accounts[i] = updated_account
                    save_data('bank_accounts')
                    st.success(f"Updated {bank_name} account details")
                    
                    # Clear edit state
                    del st.session_state.edit_bank_index
                    st.rerun()
            
            if st.button("Cancel Edit"):
                del st.session_state.edit_bank_index
                st.rerun()
    else:
        st.info("No bank accounts added yet. Use the form above to add your first account.")

# Tab 3: Credit Cards
with tab3:
    st.header("Credit Cards")
    
    # Add new credit card
    with st.expander("Add New Credit Card", expanded=False):
        with st.form("credit_card_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                card_issuer = st.text_input("Credit Card Issuer")
                card_number = st.text_input("Card Number (Last 4 digits)")
                card_type = st.selectbox(
                    "Card Type",
                    ["Visa", "Mastercard", "Rupay", "American Express", "Other"]
                )
            
            with col2:
                credit_limit = st.number_input("Credit Limit", min_value=0.0, format="%.2f")
                outstanding_amount = st.number_input("Outstanding Amount", min_value=0.0, format="%.2f")
                due_date = st.date_input("Payment Due Date", value=datetime.now() + timedelta(days=15))
            
            card_submitted = st.form_submit_button("Add Credit Card")
            
            if card_submitted and card_issuer and card_number:
                new_card = {
                    "card_issuer": card_issuer,
                    "card_number": card_number,
                    "card_type": card_type,
                    "credit_limit": str(credit_limit),
                    "outstanding_amount": str(outstanding_amount),
                    "due_date": due_date.strftime("%Y-%m-%d"),
                    "last_updated": datetime.now().strftime("%Y-%m-%d")
                }
                
                st.session_state.credit_cards.append(new_card)
                save_data('credit_cards')
                st.success(f"Added {card_issuer} credit card ending with {card_number}")
                st.rerun()
    
    # Display credit cards
    if st.session_state.credit_cards:
        for i, card in enumerate(st.session_state.credit_cards):
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 1, 1])
                
                # Calculate utilization percentage
                utilization = (float(card['outstanding_amount']) / float(card['credit_limit'])) * 100 if float(card['credit_limit']) > 0 else 0
                
                with col1:
                    st.markdown(f"**{card['card_issuer']} ({card['card_type']})**")
                    st.caption(f"Card ending with {card['card_number']}")
                
                with col2:
                    st.markdown(f"**Due: ₹{float(card['outstanding_amount']):,.2f}**")
                    st.caption(f"Limit: ₹{float(card['credit_limit']):,.2f}")
                
                with col3:
                    due_date = datetime.strptime(card['due_date'], "%Y-%m-%d").date()
                    days_left = (due_date - datetime.now().date()).days
                    
                    if days_left <= 3:
                        st.markdown(f"**Due Date: <span style='color:red'>{card['due_date']} ({days_left} days left)</span>**", unsafe_allow_html=True)
                    else:
                        st.markdown(f"**Due Date: {card['due_date']} ({days_left} days left)**")
                    
                    # Display utilization
                    if utilization >= 80:
                        st.caption(f"Utilization: <span style='color:red'>{utilization:.1f}%</span>", unsafe_allow_html=True)
                    elif utilization >= 50:
                        st.caption(f"Utilization: <span style='color:orange'>{utilization:.1f}%</span>", unsafe_allow_html=True)
                    else:
                        st.caption(f"Utilization: <span style='color:green'>{utilization:.1f}%</span>", unsafe_allow_html=True)
                
                with col4:
                    if st.button("Edit", key=f"edit_card_{i}"):
                        st.session_state.edit_card_index = i
                        st.rerun()
                
                with col5:
                    if st.button("Delete", key=f"delete_card_{i}"):
                        st.session_state.credit_cards.pop(i)
                        save_data('credit_cards')
                        st.success("Credit card deleted successfully")
                        st.rerun()
                
                st.divider()
        
        # Credit utilization chart
        if len(st.session_state.credit_cards) > 0:
            st.subheader("Credit Utilization")
            
            utilization_data = []
            for card in st.session_state.credit_cards:
                limit = float(card['credit_limit'])
                used = float(card['outstanding_amount'])
                available = limit - used
                
                if limit > 0:
                    utilization_data.append({
                        'Card': f"{card['card_issuer']} ({card['card_number']})",
                        'Limit': limit,
                        'Used': used,
                        'Available': available,
                        'Utilization (%)': (used / limit) * 100 if limit > 0 else 0
                    })
            
            if utilization_data:
                df_utilization = pd.DataFrame(utilization_data)
                
                # Bar chart showing used vs available credit
                fig = go.Figure()
                
                fig.add_trace(go.Bar(
                    x=df_utilization['Card'],
                    y=df_utilization['Used'],
                    name='Used Credit',
                    marker_color='#FF6B6B'
                ))
                
                fig.add_trace(go.Bar(
                    x=df_utilization['Card'],
                    y=df_utilization['Available'],
                    name='Available Credit',
                    marker_color='#4CAF50'
                ))
                
                fig.update_layout(
                    title='Credit Card Utilization',
                    barmode='stack',
                    xaxis_title='Credit Card',
                    yaxis_title='Amount (₹)',
                    legend_title='Category'
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Add utilization gauge charts
                st.subheader("Individual Card Utilization")
                
                # Create rows with 3 gauges per row
                cards_per_row = 3
                rows = (len(utilization_data) + cards_per_row - 1) // cards_per_row
                
                for row in range(rows):
                    cols = st.columns(cards_per_row)
                    
                    for col_idx in range(cards_per_row):
                        item_idx = row * cards_per_row + col_idx
                        
                        if item_idx < len(utilization_data):
                            card_data = utilization_data[item_idx]
                            utilization_pct = card_data['Utilization (%)']
                            
                            # Determine color based on utilization
                            if utilization_pct >= 80:
                                color = "red"
                            elif utilization_pct >= 50:
                                color = "orange"
                            else:
                                color = "green"
                            
                            # Create gauge chart
                            with cols[col_idx]:
                                fig = go.Figure(go.Indicator(
                                    mode="gauge+number",
                                    value=utilization_pct,
                                    title={'text': card_data['Card']},
                                    domain={'x': [0, 1], 'y': [0, 1]},
                                    gauge={
                                        'axis': {'range': [0, 100]},
                                        'bar': {'color': color},
                                        'steps': [
                                            {'range': [0, 50], 'color': "lightgreen"},
                                            {'range': [50, 80], 'color': "lightyellow"},
                                            {'range': [80, 100], 'color': "lightcoral"}
                                        ],
                                        'threshold': {
                                            'line': {'color': "red", 'width': 4},
                                            'thickness': 0.75,
                                            'value': 80
                                        }
                                    }
                                ))
                                
                                fig.update_layout(height=250)
                                st.plotly_chart(fig, use_container_width=True)
        
        # Edit credit card
        if 'edit_card_index' in st.session_state:
            i = st.session_state.edit_card_index
            card = st.session_state.credit_cards[i]
            
            st.subheader(f"Edit {card['card_issuer']} Credit Card")
            
            with st.form("edit_card_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    card_issuer = st.text_input("Credit Card Issuer", value=card['card_issuer'])
                    card_number = st.text_input("Card Number (Last 4 digits)", value=card['card_number'])
                    card_type = st.selectbox(
                        "Card Type",
                        ["Visa", "Mastercard", "Rupay", "American Express", "Other"],
                        index=["Visa", "Mastercard", "Rupay", "American Express", "Other"].index(card['card_type'])
                    )
                
                with col2:
                    credit_limit = st.number_input(
                        "Credit Limit", 
                        min_value=0.0, 
                        value=float(card['credit_limit']),
                        format="%.2f"
                    )
                    outstanding_amount = st.number_input(
                        "Outstanding Amount", 
                        min_value=0.0, 
                        value=float(card['outstanding_amount']),
                        format="%.2f"
                    )
                    due_date = st.date_input(
                        "Payment Due Date", 
                        value=datetime.strptime(card['due_date'], "%Y-%m-%d").date()
                    )
                
                update_card_submitted = st.form_submit_button("Update Credit Card")
                
                if update_card_submitted:
                    updated_card = {
                        "card_issuer": card_issuer,
                        "card_number": card_number,
                        "card_type": card_type,
                        "credit_limit": str(credit_limit),
                        "outstanding_amount": str(outstanding_amount),
                        "due_date": due_date.strftime("%Y-%m-%d"),
                        "last_updated": datetime.now().strftime("%Y-%m-%d")
                    }
                    
                    st.session_state.credit_cards[i] = updated_card
                    save_data('credit_cards')
                    st.success(f"Updated {card_issuer} credit card details")
                    
                    # Clear edit state
                    del st.session_state.edit_card_index
                    st.rerun()
            
            if st.button("Cancel Card Edit"):
                del st.session_state.edit_card_index
                st.rerun()
    else:
        st.info("No credit cards added yet. Use the form above to add your first card.")

# Tab 4: Demat Holdings
with tab4:
    st.header("Demat Holdings")
    
    # Add new stock/holding
    with st.expander("Add New Stock Holding", expanded=False):
        with st.form("demat_holding_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                stock_symbol = st.text_input("Stock Symbol (e.g., RELIANCE)")
                stock_name = st.text_input("Stock Name (e.g., Reliance Industries Ltd)")
                quantity = st.number_input("Quantity (Number of Shares)", min_value=1, step=1)
            
            with col2:
                purchase_price = st.number_input("Average Purchase Price (per share)", min_value=0.0, format="%.2f")
                current_price = st.number_input("Current Market Price (per share)", min_value=0.0, format="%.2f")
                purchase_date = st.date_input("Purchase Date", value=datetime.now().date())
            
            # Calculate values
            purchase_value = quantity * purchase_price
            current_value = quantity * current_price
            profit_loss = current_value - purchase_value
            profit_loss_percent = (profit_loss / purchase_value) * 100 if purchase_value > 0 else 0
            
            st.markdown(f"""
            **Investment Summary:**
            - Purchase Value: ₹{purchase_value:,.2f}
            - Current Value: ₹{current_value:,.2f}
            - Profit/Loss: ₹{profit_loss:,.2f} ({profit_loss_percent:.2f}%)
            """)
            
            holding_submitted = st.form_submit_button("Add Stock Holding")
            
            if holding_submitted and stock_symbol and stock_name and quantity > 0:
                stock_symbol = stock_symbol.upper()

                existing = next((h for h in st.session_state.demat_holdings if h['stock_symbol'] == stock_symbol), None)

                if existing:
                    # Update the existing holding
                    old_quantity = float(existing['quantity'])
                    old_price = float(existing['purchase_price'])
                    total_old_investment = old_quantity * old_price
                    total_new_investment = quantity * purchase_price
                    new_quantity = old_quantity + quantity

                    # Weighted average price
                    new_avg_price = (total_old_investment + total_new_investment) / new_quantity

                    existing['quantity'] = str(new_quantity)
                    existing['purchase_price'] = str(new_avg_price)
                    existing['current_price'] = str(current_price)
                    existing['purchase_date'] = purchase_date.strftime("%Y-%m-%d")
                    existing['purchase_value'] = str(new_quantity * new_avg_price)
                    existing['current_value'] = str(new_quantity * current_price)
                    existing['profit_loss'] = str(float(existing['current_value']) - float(existing['purchase_value']))
                    existing['profit_loss_percent'] = str((float(existing['profit_loss']) / float(existing['purchase_value'])) * 100 if float(existing['purchase_value']) > 0 else 0)
                    existing['last_updated'] = datetime.now().strftime("%Y-%m-%d")

                    st.success(f"Updated holding for {stock_symbol} with {quantity} additional shares.")

                else:
                    # Add new holding
                    new_holding = {
                        "stock_symbol": stock_symbol,
                        "stock_name": stock_name,
                        "quantity": str(quantity),
                        "purchase_price": str(purchase_price),
                        "current_price": str(current_price),
                        "purchase_date": purchase_date.strftime("%Y-%m-%d"),
                        "purchase_value": str(purchase_value),
                        "current_value": str(current_value),
                        "profit_loss": str(profit_loss),
                        "profit_loss_percent": str(profit_loss_percent),
                        "last_updated": datetime.now().strftime("%Y-%m-%d")
                    }
                    st.session_state.demat_holdings.append(new_holding)
                    st.success(f"Added new holding: {quantity} shares of {stock_name} ({stock_symbol})")
                
                save_data('demat_holdings')
                st.rerun()
    
    # Display demat holdings
    if st.session_state.demat_holdings:
        # Summary of portfolio
        total_investment = sum(float(holding['purchase_value']) for holding in st.session_state.demat_holdings)
        total_current_value = sum(float(holding['current_value']) for holding in st.session_state.demat_holdings)
        total_profit_loss = total_current_value - total_investment
        total_profit_loss_percent = (total_profit_loss / total_investment) * 100 if total_investment > 0 else 0
        
        # Display summary
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Total Investment", 
                f"₹{total_investment:,.2f}", 
                delta=None
            )
        
        with col2:
            st.metric(
                "Current Value", 
                f"₹{total_current_value:,.2f}", 
                delta=None
            )
        
        with col3:
            st.metric(
                "Profit/Loss", 
                f"₹{total_profit_loss:,.2f}", 
                delta=f"{total_profit_loss_percent:.2f}%"
            )
        
        st.subheader("Your Stock Holdings")
        st.markdown("### Update Current Prices")

        # Input for updated prices
        new_prices = {}

        for holding in st.session_state.demat_holdings:
            symbol = holding['stock_symbol']
            new_price = st.number_input(
                f"Enter current price for {symbol} ({holding['stock_name']}):",
                value=float(holding['current_price']),
                format="%.2f",
                key=f"price_input_{symbol}"
            )
            new_prices[symbol] = new_price

        # Update values when button clicked
        if st.button("Update Holdings"):
            for holding in st.session_state.demat_holdings:
                symbol = holding['stock_symbol']
                updated_price = new_prices[symbol]
                quantity = float(holding['quantity'])
                purchase_value = float(holding['purchase_value'])

                holding['current_price'] = updated_price
                holding['current_value'] = quantity * updated_price
                holding['profit_loss'] = holding['current_value'] - purchase_value
                holding['profit_loss_percent'] = (holding['profit_loss'] / purchase_value * 100) if purchase_value != 0 else 0
                holding['last_updated'] = datetime.now().strftime("%Y-%m-%d")

                    
            save_data('demat_holdings')
            st.success(f"Added {quantity} shares of {stock_name} ({stock_symbol})")
            st.rerun() 
            
        # Display table of holdings
        st.subheader("Your Stock Holdings")
        
        holdings_data = []
        for holding in st.session_state.demat_holdings:
            holdings_data.append({
                "Symbol": holding['stock_symbol'],
                "Name": holding['stock_name'],
                "Quantity": int(float(holding['quantity'])),
                "Avg. Price": f"₹{float(holding['purchase_price']):,.2f}",
                "Current Price": f"₹{float(holding['current_price']):,.2f}",
                "Investment": f"₹{float(holding['purchase_value']):,.2f}",
                "Current Value": f"₹{float(holding['current_value']):,.2f}",
                "P/L": f"₹{float(holding['profit_loss']):,.2f}",
                "P/L %": f"{float(holding['profit_loss_percent']):.2f}%"
            })
        
        df_holdings = pd.DataFrame(holdings_data)
        st.dataframe(df_holdings, use_container_width=True)
            
        # Portfolio Allocation Chart
        st.subheader("Portfolio Allocation")
        
        allocation_data = []
        for holding in st.session_state.demat_holdings:
            allocation_data.append({
                "Stock": f"{holding['stock_name']} ({holding['stock_symbol']})",
                "Value": float(holding['current_value']),
                "Percentage": (float(holding['current_value']) / total_current_value) * 100 if total_current_value > 0 else 0
            })
        
        df_allocation = pd.DataFrame(allocation_data)
        
        fig = px.pie(
            df_allocation, 
            values='Value', 
            names='Stock',
            title='Portfolio Allocation by Value',
            hover_data=['Percentage'],
            labels={'Value': 'Current Value (₹)'}
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Performance chart
        st.subheader("Stock Performance")
        
        performance_data = []
        for holding in st.session_state.demat_holdings:
            perf = float(holding['profit_loss_percent'])
            color = "green" if perf >= 0 else "red"
            
            performance_data.append({
                "Stock": f"{holding['stock_name']} ({holding['stock_symbol']})",
                "Profit/Loss (%)": perf,
                "Color": color
            })
        
        df_performance = pd.DataFrame(performance_data)
        df_performance = df_performance.sort_values("Profit/Loss (%)")
        
        fig = px.bar(
            df_performance,
            x="Stock",
            y="Profit/Loss (%)",
            color="Color",
            color_discrete_map={"green": "#4CAF50", "red": "#F44336"},
            title="Stock Performance (% Gain/Loss)",
            labels={"Profit/Loss (%)": "Profit/Loss (%)", "Stock": "Stock"}
        )
        
        fig.update_layout(showlegend=False)
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Actions for each holding
        st.subheader("Manage Holdings")
        
        for i, holding in enumerate(st.session_state.demat_holdings):
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
                
                with col1:
                    st.markdown(f"**{holding['stock_name']} ({holding['stock_symbol']})**")
                    st.caption(f"Purchased on {holding['purchase_date']} | {holding['quantity']} shares")
                
                with col2:
                    profit_loss = float(holding['profit_loss'])
                    profit_loss_percent = float(holding['profit_loss_percent'])
                    
                    if profit_loss >= 0:
                        st.markdown(f"**Profit: <span style='color:green'>₹{profit_loss:,.2f} ({profit_loss_percent:.2f}%)</span>**", unsafe_allow_html=True)
                    else:
                        st.markdown(f"**Loss: <span style='color:red'>₹{abs(profit_loss):,.2f} ({profit_loss_percent:.2f}%)</span>**", unsafe_allow_html=True)
                    
                    st.caption(f"Current: ₹{float(holding['current_price']):,.2f} | Avg: ₹{float(holding['purchase_price']):,.2f}")
                
                with col3:
                    if st.button("Edit", key=f"edit_stock_{i}"):
                        st.session_state.edit_stock_index = i
                        st.rerun()
                
                with col4:
                    if st.button("Delete", key=f"delete_stock_{i}"):
                        st.session_state.demat_holdings.pop(i)
                        save_data('demat_holdings')
                        st.success("Stock holding deleted successfully")
                        st.rerun()
                
                st.divider()
        
        # Edit stock holding
        if 'edit_stock_index' in st.session_state:
            i = st.session_state.edit_stock_index
            holding = st.session_state.demat_holdings[i]
            
            st.subheader(f"Edit {holding['stock_name']} Holding")
            
            with st.form("edit_holding_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    stock_symbol = st.text_input("Stock Symbol", value=holding['stock_symbol'])
                    stock_name = st.text_input("Stock Name", value=holding['stock_name'])
                    quantity = st.number_input(
                        "Quantity (Number of Shares)", 
                        min_value=1, 
                        step=1, 
                        value=int(float(holding['quantity']))
                    )
                
                with col2:
                    purchase_price = st.number_input(
                        "Average Purchase Price (per share)", 
                        min_value=0.0, 
                        value=float(holding['purchase_price']),
                        format="%.2f"
                    )
                    current_price = st.number_input(
                        "Current Market Price (per share)", 
                        min_value=0.0, 
                        value=float(holding['current_price']),
                        format="%.2f"
                    )
                    purchase_date = st.date_input(
                        "Purchase Date", 
                        value=datetime.strptime(holding['purchase_date'], "%Y-%m-%d").date()
                    )
                
                # Calculate values
                purchase_value = quantity * purchase_price
                current_value = quantity * current_price
                profit_loss = current_value - purchase_value
                profit_loss_percent = (profit_loss / purchase_value) * 100 if purchase_value > 0 else 0
                
                st.markdown(f"""
                **Investment Summary:**
                - Purchase Value: ₹{purchase_value:,.2f}
                - Current Value: ₹{current_value:,.2f}
                - Profit/Loss: ₹{profit_loss:,.2f} ({profit_loss_percent:.2f}%)
                """)
                
                update_holding_submitted = st.form_submit_button("Update Stock Holding")
                
                if update_holding_submitted:
                    updated_holding = {
                        "stock_symbol": stock_symbol.upper(),
                        "stock_name": stock_name,
                        "quantity": str(quantity),
                        "purchase_price": str(purchase_price),
                        "current_price": str(current_price),
                        "purchase_date": purchase_date.strftime("%Y-%m-%d"),
                        "purchase_value": str(purchase_value),
                        "current_value": str(current_value),
                        "profit_loss": str(profit_loss),
                        "profit_loss_percent": str(profit_loss_percent),
                        "last_updated": datetime.now().strftime("%Y-%m-%d")
                    }
                    
                    st.session_state.demat_holdings[i] = updated_holding
                    save_data('demat_holdings')
                    st.success(f"Updated {stock_name} ({stock_symbol}) holding details")
                    
                    # Clear edit state
                    del st.session_state.edit_stock_index
                    st.rerun()
            
            if st.button("Cancel Holding Edit"):
                del st.session_state.edit_stock_index
                st.rerun()
    else:
        st.info("No stock holdings added yet. Use the form above to add your investments.")

# Tab 5: Loan Accounts
with tab5:
    st.header("Loan Accounts")
    
    # Add new loan account
    with st.expander("Add New Loan", expanded=False):
        with st.form("loan_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                loan_type = st.selectbox(
                    "Loan Type",
                    ["Home Loan", "Car Loan", "Personal Loan", "Education Loan", "Business Loan", "Other"]
                )
                lender_name = st.text_input("Lender Name")
                account_number = st.text_input("Loan Account Number (Last 4 digits)")
            
            with col2:
                original_amount = st.number_input("Original Loan Amount", min_value=0.0, format="%.2f")
                outstanding_amount = st.number_input("Outstanding Amount", min_value=0.0, format="%.2f")
                interest_rate = st.number_input("Interest Rate (%)", min_value=0.0, max_value=30.0, format="%.2f")
            
            col3, col4 = st.columns(2)
            
            with col3:
                start_date = st.date_input("Loan Start Date", value=datetime.now())
                tenure_months = st.number_input("Tenure (in months)", min_value=1, step=1, value=36)
            
            with col4:
                emi_amount = st.number_input("EMI Amount", min_value=0.0, format="%.2f")
                next_payment_date = st.date_input("Next Payment Date", value=datetime.now() + timedelta(days=30))
            
            notes = st.text_area("Notes", height=100)
            
            loan_submitted = st.form_submit_button("Add Loan Account")
            
            if loan_submitted and lender_name and account_number:
                new_loan = {
                    "loan_type": loan_type,
                    "lender_name": lender_name,
                    "account_number": account_number,
                    "original_amount": str(original_amount),
                    "outstanding_amount": str(outstanding_amount),
                    "interest_rate": str(interest_rate),
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "tenure_months": str(tenure_months),
                    "emi_amount": str(emi_amount),
                    "next_payment_date": next_payment_date.strftime("%Y-%m-%d"),
                    "notes": notes,
                    "last_updated": datetime.now().strftime("%Y-%m-%d")
                }
                
                st.session_state.loan_accounts.append(new_loan)
                save_data('loan_accounts')
                st.success(f"Added {loan_type} from {lender_name}")
                st.rerun()
    
    # Display loan accounts
    if st.session_state.loan_accounts:
        # Total loan amount
        total_original = sum(float(loan['original_amount']) for loan in st.session_state.loan_accounts)
        total_outstanding = sum(float(loan['outstanding_amount']) for loan in st.session_state.loan_accounts)
        total_paid = total_original - total_outstanding
        
        # Progress overview
        st.subheader("Loan Repayment Progress")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Borrowed", f"₹{total_original:,.2f}")
        
        with col2:
            st.metric("Total Repaid", f"₹{total_paid:,.2f}")
        
        with col3:
            st.metric("Outstanding Amount", f"₹{total_outstanding:,.2f}")
        
        # Show progress bar
        progress_percent = (total_paid / total_original) * 100 if total_original > 0 else 0
        st.progress(progress_percent / 100)
        st.caption(f"{progress_percent:.1f}% of total loan amount repaid")
        
        # Individual loans
        st.subheader("Your Loan Accounts")
        
        for i, loan in enumerate(st.session_state.loan_accounts):
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 1, 1])
                
                with col1:
                    st.markdown(f"**{loan['loan_type']} - {loan['lender_name']}**")
                    st.caption(f"A/C ending with {loan['account_number']}")
                
                with col2:
                    st.markdown(f"**Outstanding: ₹{float(loan['outstanding_amount']):,.2f}**")
                    st.caption(f"Original Amount: ₹{float(loan['original_amount']):,.2f}")
                
                with col3:
                    next_payment = datetime.strptime(loan['next_payment_date'], "%Y-%m-%d").date()
                    days_left = (next_payment - datetime.now().date()).days
                    
                    if days_left <= 3:
                        st.markdown(f"**EMI: ₹{float(loan['emi_amount']):,.2f} <span style='color:red'>({days_left} days left)</span>**", unsafe_allow_html=True)
                    else:
                        st.markdown(f"**EMI: ₹{float(loan['emi_amount']):,.2f} ({days_left} days left)**")
                    
                    st.caption(f"Interest Rate: {loan['interest_rate']}%")
                
                with col4:
                    if st.button("Edit", key=f"edit_loan_{i}"):
                        st.session_state.edit_loan_index = i
                        st.rerun()
                
                with col5:
                    if st.button("Delete", key=f"delete_loan_{i}"):
                        st.session_state.loan_accounts.pop(i)
                        save_data('loan_accounts')
                        st.success("Loan account deleted successfully")
                        st.rerun()
                
                # Calculate loan progress
                original = float(loan['original_amount'])
                outstanding = float(loan['outstanding_amount'])
                paid = original - outstanding
                loan_progress = (paid / original) * 100 if original > 0 else 0
                
                st.caption(f"Repayment Progress: {loan_progress:.1f}%")
                st.progress(loan_progress / 100)
                st.divider()
        
        # Edit loan account
        if 'edit_loan_index' in st.session_state:
            i = st.session_state.edit_loan_index
            loan = st.session_state.loan_accounts[i]
            
            st.subheader(f"Edit {loan['loan_type']} from {loan['lender_name']}")
            
            with st.form("edit_loan_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    loan_type = st.selectbox(
                        "Loan Type",
                        ["Home Loan", "Car Loan", "Personal Loan", "Education Loan", "Business Loan", "Other"],
                        index=["Home Loan", "Car Loan", "Personal Loan", "Education Loan", "Business Loan", "Other"].index(loan['loan_type'])
                    )
                    lender_name = st.text_input("Lender Name", value=loan['lender_name'])
                    account_number = st.text_input("Loan Account Number", value=loan['account_number'])
                
                with col2:
                    original_amount = st.number_input(
                        "Original Loan Amount", 
                        min_value=0.0, 
                        value=float(loan['original_amount']),
                        format="%.2f"
                    )
                    outstanding_amount = st.number_input(
                        "Outstanding Amount", 
                        min_value=0.0, 
                        value=float(loan['outstanding_amount']),
                        format="%.2f"
                    )
                    interest_rate = st.number_input(
                        "Interest Rate (%)", 
                        min_value=0.0, 
                        max_value=30.0, 
                        value=float(loan['interest_rate']),
                        format="%.2f"
                    )
                
                col3, col4 = st.columns(2)
                
                with col3:
                    start_date = st.date_input(
                        "Loan Start Date", 
                        value=datetime.strptime(loan['start_date'], "%Y-%m-%d").date()
                    )
                    tenure_months = st.number_input(
                        "Tenure (in months)", 
                        min_value=1, 
                        step=1, 
                        value=int(float(loan['tenure_months']))
                    )
                
                with col4:
                    emi_amount = st.number_input(
                        "EMI Amount", 
                        min_value=0.0, 
                        value=float(loan['emi_amount']),
                        format="%.2f"
                    )
                    next_payment_date = st.date_input(
                        "Next Payment Date", 
                        value=datetime.strptime(loan['next_payment_date'], "%Y-%m-%d").date()
                    )
                
                notes = st.text_area("Notes", value=loan.get('notes', ''), height=100)
                
                update_loan_submitted = st.form_submit_button("Update Loan Account")
                
                if update_loan_submitted:
                    updated_loan = {
                        "loan_type": loan_type,
                        "lender_name": lender_name,
                        "account_number": account_number,
                        "original_amount": str(original_amount),
                        "outstanding_amount": str(outstanding_amount),
                        "interest_rate": str(interest_rate),
                        "start_date": start_date.strftime("%Y-%m-%d"),
                        "tenure_months": str(tenure_months),
                        "emi_amount": str(emi_amount),
                        "next_payment_date": next_payment_date.strftime("%Y-%m-%d"),
                        "notes": notes,
                        "last_updated": datetime.now().strftime("%Y-%m-%d")
                    }
                    
                    st.session_state.loan_accounts[i] = updated_loan
                    save_data('loan_accounts')
                    st.success(f"Updated {loan_type} from {lender_name}")
                    
                    # Clear edit state
                    del st.session_state.edit_loan_index
                    st.rerun()
            
            if st.button("Cancel Loan Edit"):
                del st.session_state.edit_loan_index
                st.rerun()
        
        # Loan Distribution
        st.subheader("Loan Distribution")
        
        loan_data = []
        for loan in st.session_state.loan_accounts:
            loan_data.append({
                'Loan': f"{loan['loan_type']} ({loan['lender_name']})",
                'Outstanding Amount': float(loan['outstanding_amount'])
            })
        
        if loan_data:
            df_loan = pd.DataFrame(loan_data)
            
            fig = px.pie(
                df_loan, 
                values='Outstanding Amount', 
                names='Loan',
                title='Outstanding Loan Distribution',
                color_discrete_sequence=px.colors.sequential.RdBu_r
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            
            st.plotly_chart(fig, use_container_width=True)
        
        # EMI Overview
        st.subheader("Monthly EMI Overview")
        
        emi_data = []
        for loan in st.session_state.loan_accounts:
            emi_data.append({
                'Loan': f"{loan['loan_type']} ({loan['lender_name']})",
                'EMI Amount': float(loan['emi_amount'])
            })
        
        if emi_data:
            df_emi = pd.DataFrame(emi_data)
            df_emi = df_emi.sort_values('EMI Amount', ascending=False)
            
            fig = px.bar(
                df_emi,
                x='Loan',
                y='EMI Amount',
                title='Monthly EMI by Loan',
                color='EMI Amount',
                color_continuous_scale=px.colors.sequential.Viridis
            )
            
            # Add total EMI amount as a line
            total_emi = df_emi['EMI Amount'].sum()
            
            fig.add_shape(
                type='line',
                x0=-0.5,
                y0=total_emi,
                x1=len(df_emi) - 0.5,
                y1=total_emi,
                line=dict(color='red', width=2, dash='dash')
            )
            
            fig.add_annotation(
                x=len(df_emi) - 0.7,
                y=total_emi,
                text=f"Total: ₹{total_emi:,.2f}",
                showarrow=False,
                yshift=10
            )
            
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No loan accounts added yet. Use the form above to add your first loan.")

# Tab 6: Transactions
with tab6:
    st.header("Transactions")
    
    # Add new transaction
    with st.expander("Add New Transaction", expanded=False):
        with st.form("transaction_form"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                transaction_date = st.date_input("Transaction Date", value=datetime.now().date())
                transaction_type = st.selectbox("Transaction Type", ["deposit", "withdrawal"])
            
            with col2:
                amount = st.number_input("Amount", min_value=0.0, format="%.2f")
                category = st.selectbox(
                    "Category",
                    ["Salary", "Investment", "Savings", "Bills", "Shopping", "Food", "Transport", "Entertainment", "Other"]
                )
            
            with col3:
                account = st.selectbox(
                    "Account",
                    [f"{a['bank_name']} (ending {a['account_number']})" for a in st.session_state.bank_accounts] if st.session_state.bank_accounts else ["Default"]
                )
                notes = st.text_area("Notes/Description", height=100)
            
            transaction_submitted = st.form_submit_button("Add Transaction")
            
            if transaction_submitted and amount > 0:
                new_transaction = {
                    "date": transaction_date.strftime("%Y-%m-%d"),
                    "type": transaction_type,
                    "amount": str(amount),
                    "category": category,
                    "account": account,
                    "notes": notes
                }
                
                st.session_state.transactions.append(new_transaction)
                save_data('transactions')
                
                # If transaction affects a bank account, update its balance
                if st.session_state.bank_accounts:
                    for i, a in enumerate(st.session_state.bank_accounts):
                        if account.startswith(f"{a['bank_name']} (ending {a['account_number']})"):
                            current_balance = float(a['balance'])
                            if transaction_type == "deposit":
                                new_balance = current_balance + amount
                            else:  # withdrawal
                                new_balance = current_balance - amount
                            
                            # Update account balance
                            st.session_state.bank_accounts[i]['balance'] = str(max(0, new_balance))
                            st.session_state.bank_accounts[i]['last_updated'] = datetime.now().strftime("%Y-%m-%d")
                            save_data('bank_accounts')
                            break
                
                st.success(f"Added {transaction_type} transaction of ₹{amount:,.2f}")
                st.rerun()
    
    # Display transactions
    if st.session_state.transactions:
        # Allow filtering and searching
        st.subheader("Transaction History")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            transaction_type_filter = st.multiselect(
                "Filter by Type",
                options=["deposit", "withdrawal"],
                default=["deposit", "withdrawal"]
            )
        
        with col2:
            categories = list(set(t['category'] for t in st.session_state.transactions))
            category_filter = st.multiselect(
                "Filter by Category",
                options=categories,
                default=categories
            )
        
        with col3:
            accounts = list(set(t['account'] for t in st.session_state.transactions))
            account_filter = st.multiselect(
                "Filter by Account",
                options=accounts,
                default=accounts
            )
        
        # Apply filters
        filtered_transactions = [
            t for t in st.session_state.transactions
            if t['type'] in transaction_type_filter
            and t['category'] in category_filter
            and t['account'] in account_filter
        ]
        
        # Sort by date (newest first)
        filtered_transactions.sort(key=lambda x: x['date'], reverse=True)
        
        # Create a dataframe for display
        if filtered_transactions:
            df_transactions = pd.DataFrame(filtered_transactions)
            
            # Format the dataframe
            df_display = df_transactions.copy()
            df_display['amount'] = df_display.apply(
                lambda x: f"₹{float(x['amount']):,.2f}", axis=1
            )
            df_display['transaction'] = df_display.apply(
                lambda x: f"{'➕' if x['type'] == 'deposit' else '➖'} {x['amount']}", axis=1
            )
            
            # Reorder and select columns for display
            df_display = df_display[['date', 'transaction', 'category', 'account', 'notes']]
            df_display.columns = ['Date', 'Transaction', 'Category', 'Account', 'Notes']
            
            st.dataframe(df_display, use_container_width=True)
            
            # Transaction analysis
            st.subheader("Transaction Analysis")
            
            # Create a numeric dataframe for analysis
            df_analysis = pd.DataFrame(filtered_transactions)
            df_analysis['date'] = pd.to_datetime(df_analysis['date'])
            df_analysis['amount'] = df_analysis['amount'].astype(float)
            df_analysis['month_year'] = df_analysis['date'].dt.strftime('%Y-%m')
            
            # Split by transaction type
            df_analysis['value'] = df_analysis.apply(
                lambda x: x['amount'] if x['type'] == 'deposit' else -x['amount'], 
                axis=1
            )
            
            # Monthly income vs expense
            st.markdown("#### Monthly Income vs Expense")
            monthly_summary = df_analysis.groupby(['month_year', 'type'])['amount'].sum().unstack().reset_index()
            
            if 'deposit' not in monthly_summary.columns:
                monthly_summary['deposit'] = 0
            if 'withdrawal' not in monthly_summary.columns:
                monthly_summary['withdrawal'] = 0
                
            monthly_summary['net'] = monthly_summary['deposit'] - monthly_summary['withdrawal']
            
            # Plot monthly income vs expense
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=monthly_summary['month_year'],
                y=monthly_summary['deposit'],
                name='Income',
                marker_color='#4CAF50'
            ))
            
            fig.add_trace(go.Bar(
                x=monthly_summary['month_year'],
                y=monthly_summary['withdrawal'],
                name='Expense',
                marker_color='#F44336'
            ))
            
            fig.add_trace(go.Scatter(
                x=monthly_summary['month_year'],
                y=monthly_summary['net'],
                name='Net',
                mode='lines+markers',
                line=dict(color='#2196F3', width=3)
            ))
            
            fig.update_layout(
                title='Monthly Income vs Expense',
                xaxis_title='Month',
                yaxis_title='Amount (₹)',
                barmode='group',
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Spending by category
            if 'withdrawal' in df_analysis['type'].unique():
                st.markdown("#### Spending by Category")
                
                spending_by_category = df_analysis[df_analysis['type'] == 'withdrawal'].groupby('category')['amount'].sum().reset_index()
                spending_by_category = spending_by_category.sort_values('amount', ascending=False)
                
                fig = px.pie(
                    spending_by_category,
                    values='amount',
                    names='category',
                    title='Expense Distribution by Category',
                    color_discrete_sequence=px.colors.sequential.Reds_r
                )
                fig.update_traces(textposition='inside', textinfo='percent+label')
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Income by category
            if 'deposit' in df_analysis['type'].unique():
                st.markdown("#### Income by Category")
                
                income_by_category = df_analysis[df_analysis['type'] == 'deposit'].groupby('category')['amount'].sum().reset_index()
                income_by_category = income_by_category.sort_values('amount', ascending=False)
                
                fig = px.pie(
                    income_by_category,
                    values='amount',
                    names='category',
                    title='Income Distribution by Category',
                    color_discrete_sequence=px.colors.sequential.Greens
                )
                fig.update_traces(textposition='inside', textinfo='percent+label')
                
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No transactions match the selected filters.")
    else:
        st.info("No transactions recorded yet. Use the form above to add your first transaction.")

# Footer
st.markdown("---")
st.markdown(
    "Personal Finance Tracker | "
    "A Streamlit application for tracking your financial assets and liabilities"
)