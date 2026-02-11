import matplotlib.pyplot as plt
import pandas as pd
import six

def render_mpl_table(data, col_width=3.0, row_height=0.625, font_size=14,
                     header_color='#40466e', row_colors=['#f1f1f2', 'w'], edge_color='w',
                     bbox=[0, 0, 1, 1], header_columns=0,
                     ax=None, **kwargs):
    if ax is None:
        size = (np.array(data.shape[::-1]) + np.array([0, 1])) * np.array([col_width, row_height])
        fig, ax = plt.subplots(figsize=size)
        ax.axis('off')

    mpl_table = ax.table(cellText=data.values, bbox=bbox, colLabels=data.columns, **kwargs)

    mpl_table.auto_set_font_size(False)
    mpl_table.set_fontsize(font_size)

    for k, cell in six.iteritems(mpl_table._cells):
        cell.set_edgecolor(edge_color)
        if k[0] == 0 or k[1] < header_columns:
            cell.set_text_props(weight='bold', color='w')
            cell.set_facecolor(header_color)
        else:
            cell.set_facecolor(row_colors[k[0]%len(row_colors) ])
    return ax

def create_image(module_name, data_dict):
    # Flatten data for the module into a single DataFrame-like structure
    # We will just list all fields for all models in the module
    
    rows = []
    for model, fields in data_dict.items():
        # Add a separator row or just the model name as a "Field" with special distinct description?
        # Better: Add a row that says "MODEL: <Name>"
        rows.append([f"MODEL: {model}", "", ""])
        for field in fields:
            rows.append(field)
        rows.append(["", "", ""]) # Spacer

    if rows: rows.pop() # Remove last spacer

    # Create figure
    fig, ax = plt.subplots(figsize=(12, len(rows) * 0.5 + 2))
    ax.axis('off')
    
    # Custom Table
    # We build the cell text and colors manually for full control
    cell_text = []
    cell_colors = []
    
    header_color = '#333333'
    model_header_color = '#dddddd'
    row_alt_colors = ['#ffffff', '#f9f9f9']
    
    # Header
    col_labels = ["Field Name", "Data Type", "Description"]
    
    for i, row in enumerate(rows):
        is_model_header = row[0].startswith("MODEL:")
        is_spacer = row[0] == ""
        
        cell_text.append(row)
        
        if is_model_header:
            cell_colors.append([model_header_color] * 3)
        elif is_spacer:
            cell_colors.append(['#ffffff'] * 3)
        else:
            color = row_alt_colors[i % 2]
            cell_colors.append([color] * 3)

    # Draw Table
    table = ax.table(cellText=cell_text, colLabels=col_labels, loc='center', cellColours=cell_colors, cellLoc='left')
    
    # Styling
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1, 1.8) # More padding
    
    # Bold headers
    for (row, col), cell in table.get_celld().items():
        if row == 0:
            cell.set_text_props(weight='bold', color='white')
            cell.set_facecolor(header_color)
            cell.set_edgecolor('white')
            cell.set_height(0.08)
        else:
            # Check if this row index maps to a Model Header in our data
            # row index in table includes header at 0, so data index is row-1
            data_idx = row - 1
            if data_idx >= 0 and data_idx < len(rows):
                if rows[data_idx][0].startswith("MODEL:"):
                    cell.set_text_props(weight='bold')
                    cell.set_height(0.06)
                elif rows[data_idx][0] == "":
                     cell.set_edgecolor('white') # Hide border for spacer

    plt.title(f"{module_name} Schema", fontsize=16, pad=20, weight='bold')
    plt.tight_layout()
    
    filename = f"schema_{module_name.lower()}.png"
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    print(f"Created {filename}")
    plt.close()

# --- Data Definitions ---

accounts = {
    "CustomUser": [
        ["id", "INT (PK)", "Unique ID"],
        ["email", "VARCHAR", "Login Email"],
        ["full_name", "VARCHAR", "User's Full Name"],
        ["phone", "VARCHAR", "Contact Number"],
        ["profile_image", "IMAGE", "Profile Picture"],
        ["bio", "VARCHAR", "User Biography"],
        ["upi_id", "VARCHAR", "UPI ID for Payments"],
    ],
    "Notification": [
        ["id", "INT (PK)", "Unique ID"],
        ["user", "ForeignKey", "Recipient User"],
        ["message", "VARCHAR", "Notification Text"],
        ["is_read", "BOOLEAN", "Read Status"],
        ["created_at", "DATETIME", "Creation Timestamp"],
    ]
}

expenses = {
    "Expense": [
        ["id", "INT (PK)", "Unique ID"],
        ["group", "ForeignKey", "Expense Group"],
        ["amount", "DECIMAL", "Total Cost"],
        ["description", "VARCHAR", "Expense Details"],
        ["paid_by", "ForeignKey", "Payer"],
        ["split_type", "VARCHAR", "Split Method (Equal/%)"],
    ],
    "ExpenseSplit": [
        ["id", "INT (PK)", "Unique ID"],
        ["expense", "ForeignKey", "Related Expense"],
        ["user", "ForeignKey", "Debtor"],
        ["amount", "DECIMAL", "Owed Share"],
    ]
}

groups = {
    "Group": [
        ["id", "INT (PK)", "Unique ID"],
        ["title", "VARCHAR", "Group Name"],
        ["description", "TEXT", "Group Description"],
        ["members", "ManyToMany", "Group Members"],
        ["created_by", "ForeignKey", "Creator"],
        ["last_settled_at", "DATETIME", "Last Settlement Date"],
    ],
    "GroupInvite": [
        ["id", "INT (PK)", "Unique ID"],
        ["email", "EMAIL", "Invited Email"],
        ["token", "UUID", "Unique Invite Token"],
        ["invited_by", "ForeignKey", "Sender"],
        ["is_accepted", "BOOLEAN", "Acceptance Status"],
    ]
}

payments = {
    "Payment": [
        ["id", "INT (PK)", "Unique ID"],
        ["payer", "ForeignKey", "Money Sender"],
        ["receiver", "ForeignKey", "Money Receiver"],
        ["amount", "DECIMAL", "Transaction Amount"],
        ["status", "VARCHAR", "Pending/Success/Failed"],
        ["upi_id", "VARCHAR", "UPI ID Used"],
    ],
    "Settlement": [
        ["id", "INT (PK)", "Unique ID"],
        ["group", "ForeignKey", "Context Group"],
        ["payer", "ForeignKey", "Debtor"],
        ["receiver", "ForeignKey", "Creditor"],
        ["amount", "DECIMAL", "Settlement Amount"],
        ["status", "VARCHAR", "Settlement Status"],
    ]
}

if __name__ == "__main__":
    create_image("Accounts", accounts)
    create_image("Expenses", expenses)
    create_image("Groups", groups)
    create_image("Payments", payments)
