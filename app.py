import streamlit as st
import fitz  # PyMuPDF
from io import BytesIO
import base64
import streamlit.components.v1 as components

def insert_image_in_pdf(pdf_bytes, image_bytes, page_number, position):
    pdf_file = BytesIO(pdf_bytes)
    doc = fitz.open(stream=pdf_file, filetype="pdf")
    
    page = doc.load_page(page_number)  # 页码从0开始
    
    img_rect = fitz.Rect(position[0], position[1], position[0] + position[2], position[1] + position[3])
    
    img_file = BytesIO(image_bytes)
    page.insert_image(img_rect, stream=img_file)
    
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
        
        pdf_bytes = pdf_file.read()
        image_bytes = image_file.read()
        
        output_pdf = insert_image_in_pdf(pdf_bytes, image_bytes, page_number, (x, y, width, height))
        
        pdf_bytes = output_pdf.getvalue()
        
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
                        body {{
                            margin: 0;
                            display: flex;
                            justify-content: center;
                            align-items: center;
                            height: 100vh;
                            overflow: hidden;
                        }}
                        #pdf-viewer {{
                            width: 100%;
                            height: 100%;
                            overflow: auto;
                        }}
                        canvas {{
                            display: block;
                            margin: auto;
                        }}
                    </style>
                    <script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.9.359/pdf.min.js"></script>
                </head>
                <body>
                    <div id="pdf-viewer"></div>
                    <script>
                        var pdfData = atob("{pdf_base64}");
                        var pdfjsLib = window['pdfjs-dist/build/pdf'];
                        pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.9.359/pdf.worker.min.js';
                        
                        var loadingTask = pdfjsLib.getDocument({{data: pdfData}});
                        loadingTask.promise.then(function(pdf) {{
                            console.log('PDF loaded');
                            
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
                                        document.getElementById('pdf-viewer').appendChild(canvas);
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
