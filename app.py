import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json

@st.cache_data
def load_data(file_path):
    df = pd.read_parquet(file_path)
    return df

df =load_data('菜品数据分析.parquet')

# Round '菜品平均价格' to 2 decimal places
df['菜品平均价格'] = df['菜品平均价格'].round(2)


# 定义一个函数，将年份和小数部分的月份解析为正确的日期格式
def parse_year_month(value):
    try:
        # 将年份和月份从字符串中分离
        year, month = str(value).split('.')
        # 创建一个新的日期字符串，例如 "2023-03-01"
        return pd.Timestamp(year=int(year), month=int(float(month)), day=1)
    except:
        return pd.NaT  # 如果解析失败，返回 NaT

# 应用函数，将日期列中的每个值转换为合适的日期格式
df['日期'] = df['日期'].apply(parse_year_month)

#去掉日期时间
df['日期'] = pd.to_datetime(df['日期']).dt.date

# 将百分比转换为数值形式，去掉百分比符号并转换为数值
df['推荐数同比增长率'] = df['推荐数同比增长率'].str.replace('%', '').astype(float)
df['推荐数环比增长率'] = df['推荐数环比增长率'].str.replace('%', '').astype(float)

# 创建侧边栏页面选择
st.sidebar.title("导航")
page = st.sidebar.radio("选择页面", ["数据概览", "菜品分析", "省份分析"])



# # 页面1：数据预览
if page == "数据概览":
    st.title("菜品数据概览") 
    st.write("数据预览:")
    st.dataframe(df)
    
    df_no_date = df.drop(columns=['日期'], errors='ignore')
    st.write("数据描述:")
    st.write(df_no_date.describe())
    

    # 按照大区分组，计算平均推荐数和平均价格
    region_grouped = df.groupby('大区').agg({
        '菜品推荐数': 'mean',
        '菜品平均价格': 'mean'
    }).reset_index()

    # 创建一个带有多条Y轴的柱状图
    fig = px.bar(region_grouped, x='大区', y=['菜品推荐数', '菜品平均价格'], 
                 title="各大区的平均推荐数和菜品平均价格",
                 labels={'value': '数值', '大区': '大区'},
                 barmode='group')  # 设置柱状图为分组显示

    # 更新布局
    fig.update_layout(
        yaxis_title="数值",
        xaxis_title="大区",
        legend_title="指标",
        width=800,
        height=600
    )

    # 在Streamlit中展示图表
    st.plotly_chart(fig)
    
     #---------------------所有菜品的平均价格增长率--------------------------
    
    # 将所有菜品按日期分组，计算平均价格
    grouped_data_all_dishes = df.groupby('日期').agg({
        '菜品平均价格': 'mean'
    }).reset_index()

    # 首先按日期排序
    grouped_data_all_dishes = grouped_data_all_dishes.sort_values(by='日期')

    # 计算环比增长率：与前一个时间点相比的增长率
    grouped_data_all_dishes['环比增长率'] = grouped_data_all_dishes['菜品平均价格'].pct_change() * 100

    # 计算同比增长率：与去年同期相比的增长率（如果数据跨年）
    grouped_data_all_dishes['同比增长率'] = grouped_data_all_dishes['菜品平均价格'].pct_change(periods=4) * 100

    # 将增长率四舍五入保留两位小数
    grouped_data_all_dishes['环比增长率'] = grouped_data_all_dishes['环比增长率'].round(2)
    grouped_data_all_dishes['同比增长率'] = grouped_data_all_dishes['同比增长率'].round(2)

    # ------------------折线图------------------
    # st.write("所有菜品的平均价格同比与环比增长率趋势图")

    # 绘制折线图，展示所有菜品的平均价格同比和环比增长率
    fig_growth_rate_all = px.line(
        grouped_data_all_dishes,
        x='日期',
        y=['同比增长率', '环比增长率'],
        title="所有菜品的平均价格同比与环比增长率趋势",
        labels={'value': '增长率 (%)', 'variable': '增长类型'},
        markers=True
    )
    
    # 更新Y轴格式为百分比，并保留两位小数
    fig_growth_rate_all.update_yaxes(tickformat=".2f")

    # 添加悬浮标签的格式，确保显示更精确的百分比
    fig_growth_rate_all.update_traces(
        hovertemplate='%{y:.2f}%<extra></extra>'  # 悬浮时显示百分比保留两位小数
    )
    
    st.plotly_chart(fig_growth_rate_all)
    
    
     #---------------------所有菜品的平均推荐数增长率--------------------------
    
     # 按日期分组，计算平均推荐数同比增长率和环比增长率
    grouped_data_all_dishes = df.groupby('日期').agg({
        '推荐数同比增长率': 'mean',
        '推荐数环比增长率': 'mean'
    }).reset_index()

    # 将同比和环比增长率四舍五入保留两位小数
    grouped_data_all_dishes['推荐数同比增长率'] = grouped_data_all_dishes['推荐数同比增长率'].round(2)
    grouped_data_all_dishes['推荐数环比增长率'] = grouped_data_all_dishes['推荐数环比增长率'].round(2)

    # ------------------折线图------------------
    # 绘制折线图，展示所有菜品的推荐数同比和环比增长率
    fig_growth_rate_all = px.line(
        grouped_data_all_dishes,
        x='日期',
        y=['推荐数同比增长率', '推荐数环比增长率'],
        title="所有菜品的平均推荐数同比与环比增长率趋势",
        labels={'value': '增长率 (%)', 'variable': '增长类型'},
        markers=True
    )

    # 更新Y轴格式为百分比，并保留两位小数
    fig_growth_rate_all.update_yaxes(tickformat=".2f")

    # 添加悬浮标签的格式，确保显示更精确的百分比
    fig_growth_rate_all.update_traces(
        hovertemplate='%{y:.2f}%<extra></extra>'  # 悬浮时显示百分比保留两位小数
    )

    # 在Streamlit中展示图表
    st.plotly_chart(fig_growth_rate_all)
    
        # Group the data by '省份' and calculate the average of '菜品平均价格'
    province_avg_price = df.groupby('省份')['菜品平均价格'].mean().reset_index().round(2)
    
    # 计算各省份的平均推荐数
    province_avg_recommendation = df.groupby('省份')['菜品推荐数'].mean().reset_index().round(2)

    # Load the geojson file for China provinces
    geojson_file_path = 'china_province.geojson'
    with open(geojson_file_path, 'r', encoding='utf-8') as f:
        provinces_map = json.load(f)

    # Create the choropleth map
    fig = px.choropleth_mapbox(
        province_avg_price,
        geojson=provinces_map,
        locations="省份",
        color="菜品平均价格",
        featureidkey="properties.NL_NAME_1",
        mapbox_style="open-street-map",  # Set to a brighter map style
        color_continuous_scale='greens',  # Use a high-contrast color scale
        center={"lat": 37.110573, "lon": 106.493924},
        zoom=3,
        title="中国各省份湘菜平均价格分布",
        width=900,  # Set the width of the map
        height=600  # Set the height of the map
    )

    # Show the map
    st.plotly_chart(fig)
    
    # 创建湘菜平均推荐数分布地图
    fig_recommendation = px.choropleth_mapbox(
        province_avg_recommendation,
        geojson=provinces_map,
        locations="省份",
        color="菜品推荐数",
        featureidkey="properties.NL_NAME_1",
        mapbox_style="open-street-map",
        color_continuous_scale='Blues',  # 使用不同的颜色映射
        center={"lat": 37.110573, "lon": 106.493924},
        zoom=3,
        title="中国各省份湘菜平均推荐数分布",
        width=900,
        height=600
    )

    # 展示湘菜平均推荐数分布地图
    st.plotly_chart(fig_recommendation)
    


# 页面2：按菜品类别分析

elif page == "菜品分析":
    st.title("菜品分析")
    
    # 添加搜索框用于选择菜品，并为st.text_input添加唯一key
    search_query = st.text_input("搜索菜品", "", key="search_dish_input")
    
    # 根据搜索条件筛选菜品名称
    dish_options = df['菜品名称'].unique()
    if search_query:
        dish_options = [dish for dish in dish_options if search_query in dish]
    
    # 选择菜品
    dish_name = st.selectbox("选择菜品", dish_options, key="select_dish")

    # 筛选所选菜品的数据
    filtered_data_dish = df[df['菜品名称'] == dish_name]
    

    # 去除时间中的时分秒，只保留日期
    if '日期' in filtered_data_dish.columns:
        filtered_data_dish['日期'] = pd.to_datetime(filtered_data_dish['日期']).dt.date
    
    st.write(f"筛选后的 {dish_name} 数据:")
    st.dataframe(filtered_data_dish)
    
   

    #---------------------特定菜品的平均价格增长率--------------------------
    
    # 对相同日期的菜品价格进行平均计算，确保只有一个菜品的数据
    grouped_data = filtered_data_dish.groupby('日期').agg({
        '菜品平均价格': 'mean'
    }).reset_index()


    # 首先按日期排序
    grouped_data = grouped_data.sort_values(by='日期')

    # 计算环比增长率：与前一个时间点相比的增长率
    grouped_data['环比增长率'] = grouped_data['菜品平均价格'].pct_change() * 100

    # 计算同比增长率：与去年同期相比的增长率（如果数据跨年）
    grouped_data['同比增长率'] = grouped_data['菜品平均价格'].pct_change(periods=4) * 100

    # 将增长率四舍五入保留两位小数
    grouped_data['环比增长率'] = grouped_data['环比增长率'].round(2)
    grouped_data['同比增长率'] = grouped_data['同比增长率'].round(2)

    # ------------------折线图------------------
    # st.write(f"{dish_name} 平均价格同比与环比增长率折线图")

    # 绘制折线图，展示平均的同比和环比增长率
    fig_growth_rate = px.line(
        grouped_data,
        x='日期',
        y=['同比增长率', '环比增长率'],
        title=f"{dish_name} 平均价格同比与环比增长率趋势",
        labels={'value': '增长率 (%)', 'variable': '增长类型'},
        markers=True
    )
    
    # 更新Y轴格式为百分比，并保留两位小数
    fig_growth_rate.update_yaxes(tickformat=".2f")

    # 添加悬浮标签的格式，确保显示更精确的百分比
    fig_growth_rate.update_traces(
        hovertemplate='%{y:.2f}%<extra></extra>'  # 悬浮时显示百分比保留两位小数
    )
    
    st.plotly_chart(fig_growth_rate)
    
      #---------------------特定菜品的推荐数增长率--------------------------

    # 通过日期对相同菜品进行分组，并计算推荐数同比增长率和环比增长率的平均值
    grouped_data = filtered_data_dish.groupby('日期').agg({
        '推荐数同比增长率': 'mean',
        '推荐数环比增长率': 'mean'
    }).reset_index()

    # 将增长率四舍五入保留两位小数
    grouped_data['推荐数同比增长率'] = grouped_data['推荐数同比增长率'].round(2)
    grouped_data['推荐数环比增长率'] = grouped_data['推荐数环比增长率'].round(2)

      # ------------------折线图------------------
    # st.write(f"{dish_name} 推荐数同比与环比增长率折线图")

    # 绘制折线图，展示平均的同比和环比增长率
    fig_growth_rate = px.line(
        grouped_data,
        x='日期',
        y=['推荐数同比增长率', '推荐数环比增长率'],
        title=f"{dish_name} 平均推荐数同比与环比增长率趋势",
        labels={'value': '增长率 (%)', 'variable': '增长类型'},
        markers=True
    )
    
    # 更新Y轴格式为百分比，并保留两位小数
    fig_growth_rate.update_yaxes(tickformat=".2f")

    # 添加悬浮标签的格式，确保显示更精确的百分比
    fig_growth_rate.update_traces(
        hovertemplate='%{y:.2f}%<extra></extra>'  # 悬浮时显示百分比保留两位小数
    )
    
    st.plotly_chart(fig_growth_rate)
    
    #-----------------------------菜品地图可视化-------------------------------
    
    # 使用地图展示菜品推荐数
    # st.write(f"{dish_name} 的推荐数地图分布")

    # 计算各省份的推荐数总和
    province_recommendation = filtered_data_dish.groupby('省份')['菜品推荐数'].sum().reset_index()

    # 加载中国省份GeoJSON文件
    geojson_file_path = 'china_province.geojson'
    with open(geojson_file_path, 'r', encoding='utf-8') as f:
        provinces_map = json.load(f)

    # 计算各省份的平均价格
    province_avg_price = filtered_data_dish.groupby('省份')['菜品平均价格'].mean().reset_index()


    # 绘制推荐数的地图
    fig_recommendation_map = px.choropleth_mapbox(
        province_recommendation,
        geojson=provinces_map,
        locations="省份",
        color="菜品推荐数",
        featureidkey="properties.NL_NAME_1",
        mapbox_style="open-street-map",
        color_continuous_scale='Blues',
        center={"lat": 37.110573, "lon": 106.493924},
        zoom=3,
        title=f"{dish_name} 推荐数地图分布",
        width=900,
        height=600
    )
    # 调整推荐数地图的布局
    fig_recommendation_map.update_layout(margin={"r":0, "t":30, "l":0, "b":10})  # 缩小地图的外边距
    st.plotly_chart(fig_recommendation_map)


    # 绘制平均价格的地图
    fig_price_map = px.choropleth_mapbox(
        province_avg_price,
        geojson=provinces_map,
        locations="省份",
        color="菜品平均价格",
        featureidkey="properties.NL_NAME_1",
        mapbox_style="open-street-map",
        color_continuous_scale='Reds',
        center={"lat": 37.110573, "lon": 106.493924},
        zoom=3,
        title=f"{dish_name} 平均价格地图分布",
        width=900,
        height=600
    )
    
    # 调整平均价格地图的布局
    fig_price_map.update_layout(margin={"r":0, "t":30, "l":0, "b":10})  # 缩小地图的外边距
    st.plotly_chart(fig_price_map)

# 页面3：按省份分析
elif page == "省份分析":
    st.title("按省份分析")

    province = st.selectbox("选择省份进行分析", df['省份'].unique(), key="select_province_page2")
    filtered_data_province = df[df['省份'] == province]

    st.write(f"筛选后的 {province} 数据:")
    st.dataframe(filtered_data_province)
    
    # st.title("中国各省份湘菜平均价格分布")


    
    

    # ------------------频率直方图------------------
    
    # 计算该省份的菜品的平均推荐数和平均价格
    dish_avg_stats = filtered_data_province.groupby('菜品名称').agg({
        '菜品推荐数': 'mean',
        '菜品平均价格': 'mean'
    }).reset_index()

    # 选择出该省份的前10个平均推荐数最高的菜品
    top_10_avg_recommendation = dish_avg_stats.nlargest(10, '菜品推荐数')

    # 选择出该省份前10个平均价格最高的菜品
    top_10_avg_price = dish_avg_stats.nlargest(10, '菜品平均价格')

    # 创建前10名平均推荐数的频率直方图
    # st.write(f"{province} 前10名平均推荐数频率直方图")
    fig_hist_avg_recommendation = px.bar(
        top_10_avg_recommendation,
        x="菜品名称",
        y="菜品推荐数",
        title=f"{province} 平均推荐数前10的菜品",
        labels={'菜品推荐数': '平均推荐数', '菜品名称': '菜品名称'}
    )
    fig_hist_avg_recommendation.update_yaxes(tickformat="d")
    st.plotly_chart(fig_hist_avg_recommendation)

    # 创建前10名平均价格的频率直方图
    # st.write(f"{province} 前10名平均价格频率直方图")
    fig_hist_avg_price = px.bar(
        top_10_avg_price,
        x="菜品名称",
        y="菜品平均价格",
        title=f"{province} 平均价格前10的菜品",
        labels={'菜品平均价格': '平均价格', '菜品名称': '菜品名称'}
    )
    st.plotly_chart(fig_hist_avg_price)
    

    
    # 将'菜品推荐数'按照菜品名称进行分组并计算每个省份的推荐数前10菜品
    df_grouped = df.groupby(['省份', '菜品名称']).agg({'菜品推荐数': 'mean'}).reset_index().round(2)

    # 选择前10个推荐数最高的菜品
    df_grouped_top10 = df_grouped.groupby('省份').apply(lambda x: x.nlargest(10, '菜品推荐数')).reset_index(drop=True)

    # 获取所有的省份
    provinces = df_grouped_top10['省份'].unique()

    # 创建堆叠柱状图
    fig = go.Figure()

    # 对于每个菜品名称，生成堆叠部分
    for dish in df_grouped_top10['菜品名称'].unique():
        # 生成当前菜品在不同省份的推荐数
        dish_data = df_grouped_top10[df_grouped_top10['菜品名称'] == dish]
        fig.add_trace(go.Bar(
            x=dish_data['省份'],
            y=dish_data['菜品推荐数'],
            name=dish,
            text=dish_data['菜品名称'],  # 将菜品名称传入text
            hoverinfo='text+y',  # 悬浮时显示菜品名称和推荐数
            hovertemplate='<b>%{text}</b><br>推荐数: %{y:.2f}<extra></extra>'  # 自定义悬浮标签显示格式
        ))

    # 更新布局
    fig.update_layout(
        barmode='stack',
        title="各省平均推荐数前10菜品堆叠柱状图",
        xaxis_title="省份",
        yaxis_title="推荐数",
        legend_title="菜品名称",
        width=900,
        height=600
    )

    # 在Streamlit中展示图表
    st.plotly_chart(fig)
    
    
    # 将'菜品平均价格'按照菜品名称进行分组并计算每个省份的平均价格
    df_grouped_price = df.groupby(['省份', '菜品名称']).agg({'菜品平均价格': 'mean'}).reset_index()

    # 选择前10个平均价格最高的菜品
    df_grouped_price_top10 = df_grouped_price.groupby('省份').apply(lambda x: x.nlargest(10, '菜品平均价格')).reset_index(drop=True)

    # 获取所有的省份
    provinces = df_grouped_price_top10['省份'].unique()

    # 创建堆叠柱状图
    fig_price = go.Figure()

    # 对于每个菜品名称，生成堆叠部分
    for dish in df_grouped_price_top10['菜品名称'].unique():
        # 生成当前菜品在不同省份的平均价格
        dish_data_price = df_grouped_price_top10[df_grouped_price_top10['菜品名称'] == dish]
        
        # 添加柱状图trace，并在text中显示菜品名称
        fig_price.add_trace(go.Bar(
            x=dish_data_price['省份'],
            y=dish_data_price['菜品平均价格'],
            name=dish,
            text=dish_data_price['菜品名称'],  # 将菜品名称传入text
            hoverinfo='text+y',  # 悬浮时显示菜品名称和平均价格
            hovertemplate='<b>%{text}</b><br>平均价格: %{y:.2f}<extra></extra>'  # 自定义悬浮标签显示格式
        ))

    # 更新布局
    fig_price.update_layout(
        barmode='stack',
        title="各省平均价格前10菜品堆叠柱状图",
        xaxis_title="省份",
        yaxis_title="平均价格",
        legend_title="菜品名称",
        width=900,
        height=600
    )

    # 在Streamlit中展示图表
    st.plotly_chart(fig_price)
    


    


    
  