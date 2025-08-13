import streamlit as st
import pandas as pd
import plotly.express as px

# Load master data CSV
@st.cache_data
def load_data(path):
    df = pd.read_csv(path)
    df['Maker'] = df['Maker'].str.strip('"').str.strip()
    return df

data_path = "master_Data.csv"  # adjust if needed
df = load_data(data_path)

st.title("Vehicle Registrations Dashboard")

# Sidebar: Select dashboard mode
mode = st.sidebar.radio("Select Dashboard View", ["Single Manufacturer Dashboard", "Manufacturer Comparison Charts"])

if mode == "Single Manufacturer Dashboard":
    # Existing filters for single maker
    st.sidebar.header("Filters")

    categories = df['Vehicle_Category'].unique().tolist()
    selected_category = st.sidebar.selectbox("Select Vehicle Category", categories, index=0)

    makers = df[df['Vehicle_Category'] == selected_category]['Maker'].unique().tolist()
    makers_sorted = sorted(makers)
    default_index = makers_sorted.index("ALL_MAKERS") if "ALL_MAKERS" in makers_sorted else 0
    selected_maker = st.sidebar.selectbox("Select Maker", makers_sorted, index=default_index)

    years = sorted(df['Year'].unique())
    year_min, year_max = st.sidebar.select_slider("Select Year Range", options=years, value=(years[0], years[-1]))

    search_clicked = st.sidebar.button("Search")

    if search_clicked:
        filtered = df[
            (df['Vehicle_Category'] == selected_category) &
            (df['Maker'] == selected_maker) &
            (df['Year'] >= year_min) &
            (df['Year'] <= year_max)
        ]

        st.markdown(f"Showing data for **{selected_category}** / **{selected_maker}** from **{year_min}** to **{year_max}**.")

        quarter_order = {'Q1': 1, 'Q2': 2, 'Q3': 3, 'Q4': 4}
        filtered['Quarter_Num'] = filtered['Quarter'].map(quarter_order)
        filtered = filtered.sort_values(by=['Year', 'Quarter_Num'])

        filtered['YearQuarter'] = filtered['Year'].astype(str) + filtered['Quarter']

        def show_graph_or_message(fig_func, x, y, title, **kwargs):
            if filtered.empty or filtered[y].dropna().empty:
                st.warning(f"No data available for {title}")
            else:
                total = filtered[y].sum()
                st.markdown(f"**Total {y.replace('_', ' ').title()}: {int(total)}**")
                fig = fig_func(filtered, x=x, y=y, title=title, **kwargs)
                st.plotly_chart(fig, use_container_width=True)

        # Registrations Trend
        show_graph_or_message(
            px.line,
            x='YearQuarter',
            y='Registrations',
            title="Quarterly Vehicle Registrations",
            markers=True,
            labels={'YearQuarter': 'Year - Quarter', 'Registrations': 'Registrations'}
        )

        # QoQ Growth
        if filtered.empty or filtered['QoQ_Growth'].dropna().empty:
            st.warning("No data available for Quarter-on-Quarter (QoQ) Growth Rate")
        else:
            avg_qoq = filtered['QoQ_Growth'].mean()
            st.markdown(f"**Average QoQ Growth: {avg_qoq:.2f}%**")
            fig_qoq = px.bar(
                filtered, x='YearQuarter', y='QoQ_Growth',
                labels={'YearQuarter': 'Year - Quarter', 'QoQ_Growth': 'QoQ Growth (%)'},
                title="Quarter-on-Quarter Growth Rate",
                color='QoQ_Growth', color_continuous_scale='RdYlGn')
            st.plotly_chart(fig_qoq, use_container_width=True)

        # YoY Growth
        if filtered.empty or filtered['YoY_Growth'].dropna().empty:
            st.warning("No data available for Year-on-Year (YoY) Growth Rate")
        else:
            avg_yoy = filtered['YoY_Growth'].mean()
            st.markdown(f"**Average YoY Growth: {avg_yoy:.2f}%**")
            fig_yoy = px.bar(
                filtered, x='YearQuarter', y='YoY_Growth',
                labels={'YearQuarter': 'Year - Quarter', 'YoY_Growth': 'YoY Growth (%)'},
                title="Year-on-Year Growth Rate",
                color='YoY_Growth', color_continuous_scale='RdYlGn')
            st.plotly_chart(fig_yoy, use_container_width=True)

        if st.sidebar.checkbox("Show raw data"):
            st.subheader("Raw Data")
            st.write(filtered.drop(columns=['Quarter_Num']))

    else:
        st.info("Please select filters and click **Search** to view data and graphs.")

else:
    # Manufacturer Comparison Charts Mode
        # Manufacturer Comparison Charts Mode
    st.sidebar.header("Filters for Comparison")

    categories = df['Vehicle_Category'].unique().tolist()
    selected_category = st.sidebar.selectbox("Select Vehicle Category for Comparison", categories, index=0)

    makers = df[df['Vehicle_Category'] == selected_category]['Maker'].unique().tolist()
    makers_sorted = sorted(makers)

    selected_makers = st.sidebar.multiselect(
        "Select up to 5 Manufacturers",
        options=makers_sorted,
        default=makers_sorted[:5],
        max_selections=5
    )

    years = sorted(df['Year'].unique())
    year_min, year_max = st.sidebar.select_slider(
        "Select Year Range for Comparison", options=years, value=(years[0], years[-1])
    )

    compare_clicked = st.sidebar.button("Show Comparison")
    if compare_clicked:
        if not selected_makers:
            st.warning("Please select at least one manufacturer to compare.")
        else:
            comp_df = df[
                (df['Vehicle_Category'] == selected_category) &
                (df['Maker'].isin(selected_makers)) &
                (df['Year'] >= year_min) &
                (df['Year'] <= year_max)
            ]

            if comp_df.empty:
                st.warning("No data available for the selected manufacturers and date range.")
            else:
                st.markdown(
                    f"Comparing manufacturers in **{selected_category}** from **{year_min}** to **{year_max}**:"
                )

                quarter_order = {'Q1': 1, 'Q2': 2, 'Q3': 3, 'Q4': 4}
                comp_df['Quarter_Num'] = comp_df['Quarter'].map(quarter_order)
                comp_df = comp_df.sort_values(by=['Maker', 'Year', 'Quarter_Num'])
                comp_df['YearQuarter'] = comp_df['Year'].astype(str) + comp_df['Quarter']

                for maker in selected_makers:
                    maker_data = comp_df[comp_df['Maker'] == maker]
                    st.markdown(f"### {maker}")

                    # Layout: three columns for charts, wider for better clarity
                    col1, col2, col3 = st.columns([1.3, 1.3, 1.3])

                    with col1:
                        if maker_data.empty or maker_data['Registrations'].dropna().empty:
                            st.warning("No registration data available")
                        else:
                            fig_reg = px.line(
                                maker_data, x='YearQuarter', y='Registrations',
                                markers=True, title="Registrations",
                                labels={'YearQuarter': 'Year-Quarter', 'Registrations': 'Registrations'},
                                width=700, height=400
                            )
                            st.plotly_chart(fig_reg, use_container_width=True)

                    with col2:
                        if maker_data.empty or maker_data['QoQ_Growth'].dropna().empty:
                            st.warning("No QoQ growth data available")
                        else:
                            fig_qoq = px.line(
                                maker_data, x='YearQuarter', y='QoQ_Growth',
                                markers=True, title="QoQ Growth (%)",
                                labels={'YearQuarter': 'Year-Quarter', 'QoQ_Growth': 'QoQ Growth (%)'},
                                width=700, height=400
                            )
                            st.plotly_chart(fig_qoq, use_container_width=True)

                    with col3:
                        valid_yoy = maker_data['YoY_Growth'].dropna()
                        if maker_data.empty or valid_yoy.empty:
                            st.warning("No YoY growth data available")
                        else:
                            fig_yoy = px.line(
                                maker_data, x='YearQuarter', y='YoY_Growth',
                                markers=True, title="YoY Growth (%)",
                                labels={'YearQuarter': 'Year-Quarter', 'YoY_Growth': 'YoY Growth (%)'},
                                width=700, height=400
                            )
                            st.plotly_chart(fig_yoy, use_container_width=True)

    else:
        st.info("Please select filters and click **Show Comparison** to view the comparative charts.")

