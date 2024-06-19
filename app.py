import streamlit as st
import fitz  # PyMuPDF
from io import BytesIO
import base64

def insert_image_in_pdf(pdf_path, image_path, page_number, position):
    # 打开PDF文件
    doc = fitz.open(pdf_path)
    
    # 选择页面
    page = doc.load_page(page_number)  # 注意：页码从0开始
    
    # 获取图片矩形框
    img_rect = fitz.Rect(position[0], position[1], position[0] + position[2], position[1] + position[3])
    
    # 插入图片
    page.insert_image(img_rect, filename=image_path)
    
    # 保存到字节流
    output_pdf = BytesIO()
    doc.save(output_pdf)
    doc.close()
    output_pdf.seek(0)
    
    return output_pdf

# 设置页面布局为全屏
st.set_page_config(layout="wide")

st.title("PDF图片插入工具")

# 创建两列布局
col1, col2 = st.columns([1, 2], gap="medium")

with col1:
    st.header("参数输入")
    
    # 文件上传
    pdf_file = st.file_uploader("选择一个PDF文件", type=["pdf"], key="pdf")
    image_file = st.file_uploader("选择一个图片文件", type=["png", "jpg", "jpeg"], key="img")

    # 输入参数
    page_number = st.number_input("插入图片的页面编号（从0开始）", min_value=0, value=0, step=1)
    x = st.number_input("图片的X坐标", min_value=0, value=300, step=10)
    y = st.number_input("图片的Y坐标", min_value=0, value=550, step=10)
    width = st.number_input("图片的宽度", min_value=1, value=150, step=10)
    height = st.number_input("图片的高度", min_value=1, value=150, step=10)
    
    # 生成PDF按钮
    generate_button = st.button("生成PDF")

if generate_button:
    if pdf_file and image_file:
        # 提取原始PDF文件名
        original_filename = pdf_file.name
        pdf_path = pdf_file.name
        image_path = image_file.name
        
        # 将文件保存到本地
        with open(pdf_path, "wb") as f:
            f.write(pdf_file.getbuffer())
        
        with open(image_path, "wb") as f:
            f.write(image_file.getbuffer())
        
        # 调用函数生成PDF
        output_pdf = insert_image_in_pdf(pdf_path, image_path, page_number, (x, y, width, height))
        
        # 将BytesIO对象转换为字节
        pdf_bytes = output_pdf.getvalue()
        
        with col2:
            st.header("PDF预览与下载")
            
            # 显示下载按钮，使用原始文件名
            st.download_button("下载PDF", data=pdf_bytes, file_name=original_filename, mime="application/pdf")
            
            # 使用iframe显示PDF
            pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
            pdf_display = f'<iframe src="data:application/pdf;base64,{pdf_base64}" width="100%" height="800px" type="application/pdf"></iframe>'
            st.markdown(pdf_display, unsafe_allow_html=True)
    else:
        st.error("请上传PDF文件和图片文件")

# 设置样式
st.markdown("""
    <style>
    .css-18e3th9 {
        padding-top: 2rem;
    }
    .css-1kyxreq {
        padding: 2rem 1rem;
    }
    .css-1d391kg {
        gap: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)
