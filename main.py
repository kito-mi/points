from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI()

# تركيب المجلد الحالي كمجلد للملفات الثابتة
app.mount("/", StaticFiles(directory="."), name="static")

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    return FileResponse("login.html")

# نقطة نهاية لخدمة جميع الملفات الثابتة
@app.get("/{file_path:path}")
async def serve_static_files(file_path: str):
    return FileResponse(file_path)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=port)
