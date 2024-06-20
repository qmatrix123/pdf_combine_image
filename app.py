import streamlit as st
import fitz  # PyMuPDF
from io import BytesIO
import base64
import os
import tempfile
import streamlit.components.v1 as components

def insert_image_in_pdf(pdf_path, image_path, page_number, position):
    doc = fitz.open(pdf_path)
    
    page = doc.load_page(page_number)  # 页码从0开始
    
    img_rect = fitz.Rect(position[0], position[1], position[0] + position[2], position[1] + position[3])
    
    page.insert_image(img_rect, filename=image_path)
    
    output_pdf_path = os.path.join(tempfile.gettempdir(), "output.pdf")
    doc.save(output_pdf_path)
    doc.close()
    
    return output_pdf_path

# 设置页面布局为全屏
st.set_page_config(layout="wide")

st.title("PDF图片插入工具")

# 创建两列布局
col1, col2 = st.columns([1, 2], gap="medium")

with col1:
    st.header("参数输入")
    
    pdf_file = st.file_uploader("选择一个PDF文件", type=["pdf"], key="pdf")
    image_file = st.file_uploader("选择一个图片文件", type=["png", "jpg", "jpeg"], key="img")

    page_number = st.number_input("插入图片的页面编号（从0开始）", min_value=0, value=0, step=1)
    x = st.number_input("图片的X坐标", min_value=0, value=300, step=10)
    y = st.number_input("图片的Y坐标", min_value=0, value=550, step=10)
    width = st.number_input("图片的宽度", min_value=1, value=150, step=10)
    height = st.number_input("图片的高度", min_value=1, value=150, step=10)
    
    generate_button = st.button("生成PDF")

if generate_button:
    if pdf_file and image_file:
        original_filename = pdf_file.name
        
        pdf_path = os.path.join(tempfile.gettempdir(), "input.pdf")
        image_path = os.path.join(tempfile.gettempdir(), "image.png")
        
        with open(pdf_path, "wb") as f:
            f.write(pdf_file.read())
        
        with open(image_path, "wb") as f:
            f.write(image_file.read())
        
        output_pdf_path = insert_image_in_pdf(pdf_path, image_path, page_number, (x, y, width, height))
        
        with open(output_pdf_path, "rb") as f:
            pdf_bytes = f.read()
        
        # 清理上传的文件
        os.remove(pdf_path)
        os.remove(image_path)
        
        with col2:
            st.header("PDF预览与下载")
            
            st.download_button("下载PDF", data=pdf_bytes, file_name=original_filename, mime="application/pdf")
            
            pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
            
            pdf_display = f'''
                <!DOCTYPE html>
                <html>
                <head>
                    <title>PDF Preview</title>
                    <style>
                        @import url('https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css');
                        body {{
                            margin: 0;
                            display: flex;
                            justify-content: center;
                            align-items: center;
                            height: 100vh;
                            overflow: hidden;
                            background-color: #f0f4f8;
                        }}
                        #pdf-viewer {{
                            width: 100%;
                            height: 100%;
                            overflow: auto;
                        }}
                        #loading {{
                            display: flex;
                            justify-content: center;
                            align-items: center;
                            width: 100%;
                            height: 100%;
                            font-size: 20px;
                            color: #333;
                            position: absolute;
                            top: 0;
                            left: 0;
                        }}
                        .spinner {{
                            border: 8px solid rgba(0, 0, 0, 0.1);
                            width: 64px;
                            height: 64px;
                            border-radius: 50%;
                            border-left-color: #09f;
                            animation: spin 1s ease infinite;
                        }}
                        @keyframes spin {{
                            0% {{ transform: rotate(0deg); }}
                            100% {{ transform: rotate(360deg); }}
                        }}
                    </style>
                    <script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.9.359/pdf.min.js"></script>
                </head>
                <body>
                    <div id="loading">
                        <div class="spinner"></div>
                        <span class="ml-4">Loading...</span>
                    </div>
                    <div id="pdf-viewer" style="display: none;"></div>
                    <script>
                        var pdfData = atob("{pdf_base64}");
                        var pdfjsLib = window['pdfjs-dist/build/pdf'];
                        pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.9.359/pdf.worker.min.js';
                        
                        var loadingTask = pdfjsLib.getDocument({{data: pdfData}});
                        loadingTask.promise.then(function(pdf) {{
                            console.log('PDF loaded');
                            
                            var viewer = document.getElementById('pdf-viewer');
                            var loading = document.getElementById('loading');
                            loading.style.display = 'block';
                            viewer.style.display = 'none';
                            
                            for (var pageNumber = 1; pageNumber <= pdf.numPages; pageNumber++) {{
                                pdf.getPage(pageNumber).then(function(page) {{
                                    console.log('Page loaded');
                                    
                                    var scale = 1.5;
                                    var viewport = page.getViewport({{scale: scale}});
                                    
                                    var canvas = document.createElement('canvas');
                                    var context = canvas.getContext('2d');
                                    canvas.height = viewport.height;
                                    canvas.width = viewport.width;
                                    
                                    var renderContext = {{
                                        canvasContext: context,
                                        viewport: viewport
                                    }};
                                    page.render(renderContext).promise.then(function () {{
                                        console.log('Page rendered');
                                        viewer.appendChild(canvas);
                                    }});
                                }});
                            }}
                        }}, function (reason) {{
                            console.error(reason);
                        }});
                    </script>
                </body>
                </html>
            '''
            
            components.html(pdf_display, height=800)
            
            # 清理生成的 PDF 文件
            os.remove(output_pdf_path)
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
