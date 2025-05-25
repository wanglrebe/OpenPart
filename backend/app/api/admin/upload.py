# backend/app/api/admin/upload.py (新文件 - 图片上传API)
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import os
import uuid
from PIL import Image
from app.core.database import get_db
from app.models.part import Part
from app.auth.middleware import require_admin
from app.auth.models import User

router = APIRouter()

# 配置上传目录
UPLOAD_DIR = "static/images/parts"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 允许的图片格式
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}

def validate_image(file: UploadFile) -> bool:
    """验证图片文件"""
    if not file.filename:
        return False
    
    # 检查文件扩展名
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return False
    
    return True

def resize_image(image_path: str, max_size: tuple = (800, 600)) -> None:
    """调整图片大小"""
    try:
        with Image.open(image_path) as img:
            # 检查图片格式
            print(f"原始图片格式: {img.format}, 模式: {img.mode}, 尺寸: {img.size}")
            
            # 如果是RGBA模式，转换为RGB（某些格式需要）
            if img.mode in ('RGBA', 'LA', 'P'):
                # 创建白色背景
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            # 保持宽高比调整大小
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # 保存为JPEG格式（更兼容）
            base_name = os.path.splitext(image_path)[0]
            new_path = f"{base_name}.jpg"
            img.save(new_path, 'JPEG', optimize=True, quality=85)
            
            # 如果文件名改变了，删除原文件
            if new_path != image_path:
                os.remove(image_path)
                
            print(f"图片处理完成: {new_path}")
            return new_path
            
    except Exception as e:
        print(f"图片处理失败: {e}")
        return image_path

@router.post("/upload/{part_id}")
async def upload_part_image(
    part_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """为指定零件上传图片"""
    
    # 验证零件是否存在
    part = db.query(Part).filter(Part.id == part_id).first()
    if not part:
        raise HTTPException(status_code=404, detail="零件未找到")
    
    # 验证图片文件
    if not validate_image(file):
        raise HTTPException(
            status_code=400, 
            detail="不支持的文件格式，请使用 JPG、PNG、GIF 或 WebP 格式"
        )
    
    try:
        # 生成唯一文件名 - 统一使用 .jpg
        filename = f"part_{part_id}_{uuid.uuid4().hex}.jpg"
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        # 保存原始文件
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        print(f"文件已保存: {file_path}, 大小: {len(content)} bytes")
        
        # 调整图片大小并处理格式
        processed_path = resize_image(file_path)
        
        # 更新文件名（如果被处理了）
        if processed_path != file_path:
            filename = os.path.basename(processed_path)
        
        # 更新数据库中的图片URL
        image_url = f"/static/images/parts/{filename}"
        part.image_url = image_url
        db.commit()
        
        print(f"图片URL已更新: {image_url}")
        
        return {
            "message": "图片上传成功",
            "image_url": image_url,
            "filename": filename
        }
        
    except Exception as e:
        print(f"上传失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")

@router.delete("/delete/{part_id}")
async def delete_part_image(
    part_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """删除零件图片"""
    
    part = db.query(Part).filter(Part.id == part_id).first()
    if not part:
        raise HTTPException(status_code=404, detail="零件未找到")
    
    if not part.image_url:
        raise HTTPException(status_code=400, detail="该零件没有图片")
    
    try:
        # 删除文件
        if part.image_url.startswith("/static/"):
            file_path = part.image_url[1:]  # 移除开头的 /
            if os.path.exists(file_path):
                os.remove(file_path)
        
        # 清空数据库中的图片URL
        part.image_url = None
        db.commit()
        
        return {"message": "图片删除成功"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")