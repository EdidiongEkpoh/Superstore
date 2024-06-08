import streamlit as st                           # Import Streamlit library for creating web apps
import plotly.express as px                     # Import Plotly Express for interactive visualizations
import pandas as pd                             # Import Pandas library for data manipulation
import plotly.figure_factory as ff              # Import Plotly Figure Factory for creating interactive tables
import os                                       # Import os module for operating system functionalities
import warnings                                 # Import warnings module to suppress warnings

warnings.filterwarnings('ignore')               # Suppress warnings

# Set Streamlit page configuration
st.set_page_config(page_title="Superstore", page_icon=":bar_chart:", layout="wide")

# Display title and set styling
st.title(" :bar_chart: Sample SuperStore EDA")
st.markdown('<style>div.block-container{padding-top:5rem;}</style>', unsafe_allow_html=True)

# Read data from Excel file into a DataFrame
url = "https://raw.githubusercontent.com/EdidiongEkpoh/Portfolio/main/Superstore/Superstore.xls"

@st.cache_data
def load_data(url):
    # Read the Excel file from the URL
    data = pd.read_excel(url)
    return data

df = load_data(url)

# Ensure all columns have consistent data types
for column in df.columns:
    if df[column].dtype == 'object':
        df[column] = df[column].astype(str)

# Create two columns layout
col1, col2 = st.columns((2))
df["Order Date"] = pd.to_datetime(df["Order Date"])  # Convert 'Order Date' column to datetime format

# Getting the min and max date 
startDate = pd.to_datetime(df["Order Date"]).min()
endDate = pd.to_datetime(df["Order Date"]).max()

# Allow users to select start and end dates
with col1:
    date1 = pd.to_datetime(st.date_input("Start Date", startDate))
with col2:
    date2 = pd.to_datetime(st.date_input("End Date", endDate))

# Filter data based on selected dates
df = df[(df["Order Date"] >= date1) & (df["Order Date"] <= date2)].copy()

# Create sidebar for filtering options
st.sidebar.header("Choose your filter: ")

# Create multiselect filters for Region, State, and City
region = st.sidebar.multiselect("Pick your Region", df["Region"].unique())
if not region:
    df2 = df.copy()
else:
    df2 = df[df["Region"].isin(region)]

state = st.sidebar.multiselect("Pick the State", df2["State"].unique())
if not state:
    df3 = df2.copy()
else:
    df3 = df2[df2["State"].isin(state)]

city = st.sidebar.multiselect("Pick the City", df3["City"].unique())

# Filter the data based on selected filters
if not region and not state and not city:
    filtered_df = df
elif not state and not city:
    filtered_df = df[df["Region"].isin(region)]
elif not region and not city:
    filtered_df = df[df["State"].isin(state)]
elif state and city:
    filtered_df = df3[df["State"].isin(state) & df3["City"].isin(city)]
elif region and city:
    filtered_df = df3[df["Region"].isin(region) & df3["City"].isin(city)]
elif region and state:
    filtered_df = df3[df["Region"].isin(region) & df3["State"].isin(state)]
elif city:
    filtered_df = df3[df3["City"].isin(city)]
else:
    filtered_df = df3[df3["Region"].isin(region) & df3["State"].isin(state) & df3["City"].isin(city)]

# Group by Category and sum Sales
category_df = filtered_df.groupby(by=["Category"], as_index=False)["Sales"].sum()

# Display Category wise Sales
with col1:
    st.subheader("Category wise Sales")
    fig = px.bar(category_df, x="Category", y="Sales", text=['${:,.2f}'.format(x) for x in category_df["Sales"]],
                 template="seaborn")
    st.plotly_chart(fig, use_container_width=True, height=200)

# Display Region wise Sales as a pie chart
with col2:
    st.subheader("Region wise Sales")
    fig = px.pie(filtered_df, values="Sales", names="Region", hole=0.5)
    fig.update_traces(text=filtered_df["Region"], textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

col3, col4 = st.columns((2))
with col3:
    with st.expander("Category_ViewData"):
        st.write(category_df.style.background_gradient(cmap="Blues"))
        csv = category_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Data", data=csv, file_name="Category.csv", mime="text/csv",
                            help='Click here to download the data as a CSV file')

with col4:
    with st.expander("Region_ViewData"):
        region = filtered_df.groupby(by="Region", as_index=False)["Sales"].sum()
        st.write(region.style.background_gradient(cmap="Oranges"))
        csv = region.to_csv(index=False).encode('utf-8')
        st.download_button("Download Data", data=csv, file_name="Region.csv", mime="text/csv",
                        help='Click here to download the data as a CSV file')
        
filtered_df["month_year"] = filtered_df["Order Date"].dt.to_period("M")
st.subheader('Time Series Analysis')

# Perform Time Series Analysis and display the chart
linechart = pd.DataFrame(filtered_df.groupby(filtered_df["month_year"].dt.strftime("%Y : %b"))["Sales"].sum()).reset_index()
fig2 = px.line(linechart, x="month_year", y="Sales", labels={"Sales": "Amount"}, height=500, width=1000, template="gridon")
fig2.update_xaxes(tickangle=45)
st.plotly_chart(fig2, use_container_width=True)

# Display time series data with download button
with st.expander("View Data of TimeSeries:"):
    st.write(linechart.T.style.background_gradient(cmap="Blues"))
    csv = linechart.to_csv(index=False).encode("utf-8")
    st.download_button('Download Data', data=csv, file_name="TimeSeries.csv", mime='text/csv')

# Create a TreeMap based on Region, Category, and Sub-Category
st.subheader("Hierarchical view of Sales using TreeMap")
fig3 = px.treemap(filtered_df, path=["Region", "Category", "Sub-Category"], values="Sales", hover_data=["Sales"],
                  color="Sub-Category")
fig3.update_layout(width=800, height=650)
st.plotly_chart(fig3, use_container_width=True)

# Display Segment wise Sales and Category wise Sales as pie charts
chart1, chart2 = st.columns((2))
with chart1:
    st.subheader('Segment wise Sales')
    fig = px.pie(filtered_df, values="Sales", names="Segment", template="plotly_dark")
    fig.update_traces(text=filtered_df["Segment"], textposition="inside")
    st.plotly_chart(fig, use_container_width=True)

with chart2:
    st.subheader('Category wise Sales')
    fig = px.pie(filtered_df, values="Sales", names="Category", template="gridon")
    fig.update_traces(text=filtered_df["Category"], textposition="inside")
    st.plotly_chart(fig, use_container_width=True)

# Display a subheader for the Month wise Sub-Category Sales Summary
st.subheader(":point_right: Month wise Sub-Category Sales Summary")

# Create an expander for the Summary Table
with st.expander("Summary_Table"):
    # Extract a sample DataFrame with specific columns for display
    df_sample = df[0:5][["Region", "State", "City", "Category", "Sales", "Profit", "Quantity"]]
    
    # Create an interactive table using Plotly Figure Factory
    fig = ff.create_table(df_sample, colorscale="Cividis")
    
    # Display the table
    st.plotly_chart(fig, use_container_width=True)

    # Display a markdown text indicating Month wise sub-Category Table
    st.markdown("Month wise sub-Category Table")
    
    # Calculate the sales for each sub-category for each month
    filtered_df["month"] = filtered_df["Order Date"].dt.month_name()
    sub_category_Year = pd.pivot_table(data=filtered_df, values="Sales", index=["Sub-Category"], columns="month")
    
    # Display the pivot table with background gradient for better visualization
    st.write(sub_category_Year.style.background_gradient(cmap="Blues"))

# Create a scatter plot to visualize the relationship between Sales and Profits
data1 = px.scatter(filtered_df, x="Sales", y="Profit", size="Quantity")

# Update layout of the scatter plot with title and axis labels
data1['layout'].update(title="Relationship between Sales and Profits using Scatter Plot.",
                       titlefont=dict(size=20), xaxis=dict(title="Sales", titlefont=dict(size=19)),
                       yaxis=dict(title="Profit", titlefont=dict(size=19)))

# Display the scatter plot
st.plotly_chart(data1, use_container_width=True)

# Create an expander for viewing data
with st.expander("View Data"):
    # Display a subset of the filtered DataFrame with specific columns and gradient background
    st.write(filtered_df.iloc[:500, 1:20:2].style.background_gradient(cmap="Oranges"))

# Download the original DataSet as a CSV file
csv = df.to_csv(index=False).encode('utf-8')
st.download_button('Download Data', data=csv, file_name="Data.csv", mime="text/csv")
