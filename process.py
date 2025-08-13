import pandas as pd
from pathlib import Path

# ====== Configuration ======
base_path = Path(r"C:\Users\siddh\OneDrive\Desktop\task_using_perplex\raw_data\maker")
output_file = Path(r"C:\Users\siddh\OneDrive\Desktop\task_using_perplex\master_Data.csv")

# Month names in order
month_labels_full = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                     'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

all_data = []

# ===== Loop through all files =====
for year_folder in sorted(base_path.iterdir()):
    if not year_folder.is_dir():
        continue
    year = int(year_folder.name)

    for file in year_folder.glob("*.xlsx"):
        fname = file.name.lower()
        # Detect category from file name
        if "two" in fname:
            category = "Two Wheeler"
        elif "three" in fname:
            category = "Three Wheeler"
        elif "four" in fname:
            category = "Four Wheeler"
        else:
            category = "Unknown"

        print(f"Processing {file} ({category}, {year})...")

        # Skip top title rows, actual Maker row is at index 4
        df = pd.read_excel(file, header=4)

        # Fill down merged cells in Maker col and strip spaces
        df.iloc[:, 1] = df.iloc[:, 1].ffill()
        df.iloc[:, 1] = df.iloc[:, 1].astype(str).str.strip()
        df.rename(columns={df.columns[1]: "Maker"}, inplace=True)

        # Determine how many "month" columns exist (exclude TOTAL if present)
        month_cols_raw = df.columns[2:]  # all columns after Maker
        # Drop any column named TOTAL (case-insensitive)
        month_cols_raw = [col for col in month_cols_raw if 'total' not in str(col).lower()]

        # Assign month labels dynamically based on how many columns are present
        month_labels = month_labels_full[:len(month_cols_raw)]
        monthly_data = df.iloc[:, 2:2+len(month_cols_raw)].copy()
        monthly_data.columns = month_labels

        # Convert all monthly data to numeric (handles commas / strings)
        monthly_data = monthly_data.apply(pd.to_numeric, errors='coerce').fillna(0)

        # Build cleaned dataframe
        clean_df = pd.concat([df[["Maker"]], monthly_data], axis=1)
        clean_df["Year"] = year
        clean_df["Vehicle_Category"] = category
        all_data.append(clean_df)

# ===== Combine all data =====
master_df = pd.concat(all_data, ignore_index=True)

# ===== Create Quarters dynamically =====
quarter_map = {
    'Q1': [m for m in ['Jan', 'Feb', 'Mar'] if m in master_df.columns],
    'Q2': [m for m in ['Apr', 'May', 'Jun'] if m in master_df.columns],
    'Q3': [m for m in ['Jul', 'Aug', 'Sep'] if m in master_df.columns],
    'Q4': [m for m in ['Oct', 'Nov', 'Dec'] if m in master_df.columns],
}

for q, months in quarter_map.items():
    if months:  # only sum if months exist
        master_df[q] = master_df[months].sum(axis=1)
    else:
        master_df[q] = None

# ===== Reshape to long format =====
quarterly_df = master_df.melt(
    id_vars=['Vehicle_Category', 'Maker', 'Year'],
    value_vars=['Q1', 'Q2', 'Q3', 'Q4'],
    var_name='Quarter',
    value_name='Registrations'
).sort_values(['Vehicle_Category', 'Maker', 'Year', 'Quarter'])

# Create YearQuarter
quarterly_df['YearQuarter'] = quarterly_df['Year'].astype(str) + quarterly_df['Quarter']

# ===== Calculate QoQ & YoY Growth =====
quarterly_df['QoQ_Growth'] = quarterly_df.groupby(
    ['Vehicle_Category', 'Maker']
)['Registrations'].pct_change() * 100

quarterly_df['YoY_Growth'] = quarterly_df.groupby(
    ['Vehicle_Category', 'Maker', 'Quarter']
)['Registrations'].pct_change(periods=4) * 100

# ===== Category totals (ALL_MAKERS) =====
category_totals = quarterly_df.groupby(
    ['Vehicle_Category', 'Year', 'Quarter', 'YearQuarter'], as_index=False
)['Registrations'].sum()
category_totals['Maker'] = 'ALL_MAKERS'
category_totals['QoQ_Growth'] = category_totals.groupby(
    ['Vehicle_Category']
)['Registrations'].pct_change() * 100
category_totals['YoY_Growth'] = category_totals.groupby(
    ['Vehicle_Category', 'Quarter']
)['Registrations'].pct_change(periods=4) * 100

# Merge totals and detail
final_df = pd.concat([quarterly_df, category_totals], ignore_index=True)

# ===== Save =====
final_df.to_csv(output_file, index=False)
print(f"\n✅ Master dataset saved at: {output_file}")
print(final_df.head(12))
