import os
import tempfile
import uuid

import fitz  # PyMuPDF
from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from db import SessionLocal
from models import User

app = FastAPI()

# ✅ CORS
app.add_middleware(
          CORSMiddleware,
          allow_origins=["*"],  # Change in production
          allow_credentials=True,
          allow_methods=["*"],
          allow_headers=["*"],
)

# ✅ Database Dependency
def get_db():
          db = SessionLocal()
          try:
                    yield db
          finally:
                    db.close()

# ✅ PDF Margin Helper
def set_page_margins(page, margins):
          rect = page.rect
          new_rect = fitz.Rect(
                    rect.x0 - margins[0],
                    rect.y0 - margins[1],
                    rect.x1 + margins[2],
                    rect.y1 + margins[3]
          )
          page.set_mediabox(new_rect)

# ✅ Margin Application Logic
def apply_margins(input_path, output_path, mode, margins, margins_odd=None, margins_even=None,
                  selected_pages=None, group_margins=None):
          doc = fitz.open(input_path)

          if mode == "all":
                    for page in doc:
                              set_page_margins(page, margins)

          elif mode == "odd_even":
                    for i, page in enumerate(doc):
                              if (i + 1) % 2 == 1:
                                        set_page_margins(page, margins_odd)
                              else:
                                        set_page_margins(page, margins_even)

          elif mode == "selected":
                    for i, page in enumerate(doc):
                              if (i + 1) in selected_pages:
                                        set_page_margins(page, margins)

          elif mode == "groups":
                    group_margins_dict = {}
                    for group in group_margins.split(";"):
                              range_part, margin_part = group.split(":")
                              start, end = map(int, range_part.split("-"))
                              margins_tuple = tuple(map(int, margin_part.split(",")))
                              group_margins_dict[(start, end)] = margins_tuple

                    for i, page in enumerate(doc):
                              page_num = i + 1
                              for (start, end), margins_tuple in group_margins_dict.items():
                                        if start <= page_num <= end:
                                                  set_page_margins(page, margins_tuple)

          doc.save(output_path)
          doc.close()

# ✅ Upload Endpoint
@app.post("/upload/")
async def upload_pdf(
          file: UploadFile = File(...),
          mode: str = Form(...),
          margins: str = Form("20,20,20,20"),
          margins_odd: str = Form("20,20,20,20"),
          margins_even: str = Form("20,20,20,20"),
          selected_pages: str = Form(""),
          group_margins: str = Form("")
):
          with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_input:
                    temp_input.write(await file.read())
                    temp_input_path = temp_input.name

          temp_output_path = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name

          try:
                    margins = tuple(map(int, margins.split(",")))
                    margins_odd = tuple(map(int, margins_odd.split(",")))
                    margins_even = tuple(map(int, margins_even.split(",")))
                    selected_pages = list(map(int, selected_pages.split(","))) if selected_pages else []

                    apply_margins(temp_input_path, temp_output_path, mode, margins, margins_odd,
                                  margins_even, selected_pages, group_margins)

                    return StreamingResponse(open(temp_output_path, "rb"), media_type="application/pdf",
                                             headers={
                                                       "Content-Disposition": f"attachment; filename=modified_{file.filename}"})
          finally:
                    os.remove(temp_input_path)
                    os.remove(temp_output_path)

# ✅ Login Endpoint with session control
@app.post("/login")
def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
          user = db.query(User).filter(User.username == username).first()
          if not user or user.password != password:
                    raise HTTPException(status_code=401, detail="Invalid username or password")

          if user.session_token:
                    raise HTTPException(status_code=403, detail="User already logged in on another device")

          session_token = str(uuid.uuid4())
          user.session_token = session_token
          db.commit()

          return {"message": "Login successful", "username": user.username, "token": session_token}

# ✅ Logout Endpoint
@app.post("/logout")
def logout(token: str = Form(...), db: Session = Depends(get_db)):
          user = db.query(User).filter(User.session_token == token).first()
          if not user:
                    raise HTTPException(status_code=401, detail="Invalid session token")

          user.session_token = None
          db.commit()
          return {"message": "Logout successful"}

# ✅ Health Check
@app.get("/")
def home():
          return {"message": "📘 PDF Margin API is running. Use /upload/ to modify a PDF."}
