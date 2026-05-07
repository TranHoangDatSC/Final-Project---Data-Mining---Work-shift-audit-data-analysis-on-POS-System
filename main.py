from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

# Mount thư mục static để Vercel tìm thấy CSS và Ảnh
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

@app.get("/")
async def home(request: Request):
    # Trả về file HTML của ông ngay lập tức
    return templates.TemplateResponse("index.html", {"request": request})