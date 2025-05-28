# backend/app/api/admin/file_upload.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import os
import uuid
import time
import mimetypes
from datetime import datetime, timedelta
from app.core.database import get_db
from app.models.part import Part
from app.auth.middleware import require_admin
from app.auth.models import User
from app.schemas.part import PartCreate
from pydantic import BaseModel, validator

router = APIRouter()

# 配置常量
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
TEMP_DIR = "static/temp/files"
MAX_BATCH_SIZE = 1000  # 单次最多插入1000条
UPLOAD_RATE_LIMIT = 10  # 每小时最多10个文件
FILE_CLEANUP_HOURS = 24  # 24小时后清理文件（给插件足够时间处理）

# 支持的文件类型
ALLOWED_FILE_TYPES = {
    # 文档格式
    'application/pdf',
    'application/msword',  # .doc
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',  # .docx
    
    # 表格格式
    'application/vnd.ms-excel',  # .xls
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',  # .xlsx
    'text/csv',
    
    # 压缩包
    'application/zip',
    'application/x-rar-compressed',
    'application/x-7z-compressed',
    
    # 文本格式
    'text/plain',
    'application/json',
    'application/xml',
    'text/xml'
}

# 文件扩展名映射（双重验证）
ALLOWED_EXTENSIONS = {
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.csv',
    '.zip', '.rar', '.7z', '.txt', '.json', '.xml'
}

# 文件头魔数验证
FILE_SIGNATURES = {
    b'\x25\x50\x44\x46': 'application/pdf',  # PDF
    b'\xD0\xCF\x11\xE0': 'application/msword',  # DOC/XLS
    b'\x50\x4B\x03\x04': 'application/zip',  # ZIP/DOCX/XLSX
    b'\x52\x61\x72\x21': 'application/x-rar-compressed',  # RAR
}

# 确保临时目录存在
os.makedirs(TEMP_DIR, exist_ok=True)

class FileUploadResponse(BaseModel):
    success: bool
    message: str
    file_id: Optional[str] = None
    filename: Optional[str] = None
    file_size: Optional[int] = None
    content_type: Optional[str] = None
    download_url: Optional[str] = None
    expires_at: Optional[datetime] = None

class PartData(BaseModel):
    name: str
    category: Optional[str] = None
    description: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None
    image_url: Optional[str] = None
    
    @validator('name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('零件名称不能为空')
        if len(v.strip()) > 255:
            raise ValueError('零件名称长度不能超过255字符')
        return v.strip()
    
    @validator('category')
    def validate_category(cls, v):
        if v and len(v) > 100:
            raise ValueError('类别长度不能超过100字符')
        return v.strip() if v else None
    
    @validator('description')
    def validate_description(cls, v):
        if v and len(v) > 2000:
            raise ValueError('描述长度不能超过2000字符')
        return v.strip() if v else None

class BatchCreateRequest(BaseModel):
    parts: List[PartData]
    
    @validator('parts')
    def validate_parts_count(cls, v):
        if len(v) == 0:
            raise ValueError('零件列表不能为空')
        if len(v) > MAX_BATCH_SIZE:
            raise ValueError(f'单次最多只能创建{MAX_BATCH_SIZE}个零件')
        return v

class BatchCreateResponse(BaseModel):
    success: bool
    message: str
    total_processed: int
    successful_creates: int
    skipped_duplicates: int
    errors: List[Dict[str, Any]]

def validate_file_signature(file_content: bytes, declared_type: str) -> bool:
    """验证文件头部签名"""
    try:
        # 检查文件头
        for signature, expected_type in FILE_SIGNATURES.items():
            if file_content.startswith(signature):
                # PDF和RAR有明确签名
                if expected_type in ['application/pdf', 'application/x-rar-compressed']:
                    return expected_type == declared_type
                # ZIP系列格式需要进一步判断
                elif signature == b'\x50\x4B\x03\x04':
                    zip_based_types = [
                        'application/zip',
                        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                    ]
                    return declared_type in zip_based_types
                # DOC/XLS系列
                elif signature == b'\xD0\xCF\x11\xE0':
                    office_types = [
                        'application/msword',
                        'application/vnd.ms-excel'
                    ]
                    return declared_type in office_types
        
        # 文本类型简单验证
        if declared_type in ['text/plain', 'text/csv', 'application/json', 'application/xml', 'text/xml']:
            try:
                # 尝试解码为文本
                file_content[:1024].decode('utf-8')
                return True
            except UnicodeDecodeError:
                return False
        
        return True  # 其他类型暂时通过
        
    except Exception:
        return False

def is_safe_filename(filename: str) -> bool:
    """检查文件名是否安全"""
    if not filename:
        return False
    
    # 检查危险字符
    dangerous_chars = ['..', '/', '\\', ':', '*', '?', '"', '<', '>', '|']
    for char in dangerous_chars:
        if char in filename:
            return False
    
    # 检查是否为系统文件名
    system_names = ['CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4', 
                   'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2', 
                   'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9']
    
    name_without_ext = os.path.splitext(filename)[0].upper()
    if name_without_ext in system_names:
        return False
    
    return True

def cleanup_old_files():
    """清理过期的临时文件"""
    try:
        current_time = time.time()
        cutoff_time = current_time - (FILE_CLEANUP_HOURS * 3600)
        
        for filename in os.listdir(TEMP_DIR):
            file_path = os.path.join(TEMP_DIR, filename)
            if os.path.isfile(file_path):
                file_mtime = os.path.getmtime(file_path)
                if file_mtime < cutoff_time:
                    try:
                        os.remove(file_path)
                        print(f"清理过期文件: {filename}")
                    except Exception as e:
                        print(f"清理文件失败 {filename}: {e}")
    except Exception as e:
        print(f"清理过程出错: {e}")

@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    上传文件到临时目录供插件处理
    """
    try:
        # 清理过期文件
        cleanup_old_files()
        
        # 1. 基本验证
        if not file.filename:
            raise HTTPException(status_code=400, detail="文件名不能为空")
        
        if not is_safe_filename(file.filename):
            raise HTTPException(status_code=400, detail="文件名包含不安全字符")
        
        # 2. 文件大小验证
        contents = await file.read()
        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400, 
                detail=f"文件大小超过限制 ({MAX_FILE_SIZE // 1024 // 1024}MB)"
            )
        
        if len(contents) == 0:
            raise HTTPException(status_code=400, detail="文件不能为空")
        
        # 3. 文件类型验证
        # 获取MIME类型
        content_type = file.content_type
        if not content_type:
            content_type, _ = mimetypes.guess_type(file.filename)
        
        if not content_type or content_type not in ALLOWED_FILE_TYPES:
            raise HTTPException(
                status_code=400, 
                detail=f"不支持的文件类型: {content_type}"
            )
        
        # 4. 文件扩展名验证
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400, 
                detail=f"不支持的文件扩展名: {file_ext}"
            )
        
        # 5. 文件头部验证
        if not validate_file_signature(contents, content_type):
            raise HTTPException(
                status_code=400, 
                detail="文件内容与声明的类型不匹配"
            )
        
        # 6. 生成安全的文件名
        file_id = uuid.uuid4().hex
        safe_filename = f"{file_id}_{int(time.time())}{file_ext}"
        file_path = os.path.join(TEMP_DIR, safe_filename)
        
        # 7. 保存文件
        with open(file_path, 'wb') as f:
            f.write(contents)
        
        # 8. 生成下载URL和过期时间
        download_url = f"/api/admin/files/{file_id}/download"
        expires_at = datetime.utcnow() + timedelta(hours=FILE_CLEANUP_HOURS)
        
        return FileUploadResponse(
            success=True,
            message="文件上传成功",
            file_id=file_id,
            filename=file.filename,
            file_size=len(contents),
            content_type=content_type,
            download_url=download_url,
            expires_at=expires_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"文件上传过程中出现未预期错误: {e}")
        raise HTTPException(status_code=500, detail="文件上传失败，请稍后重试")

@router.get("/{file_id}/download")
async def download_file(
    file_id: str,
    current_user: User = Depends(require_admin)
):
    """
    下载临时文件（供插件使用）
    """
    try:
        # 查找匹配的文件
        matching_files = [
            f for f in os.listdir(TEMP_DIR) 
            if f.startswith(file_id + '_')
        ]
        
        if not matching_files:
            raise HTTPException(status_code=404, detail="文件未找到或已过期")
        
        file_path = os.path.join(TEMP_DIR, matching_files[0])
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="文件未找到")
        
        # 检查文件是否过期
        file_mtime = os.path.getmtime(file_path)
        current_time = time.time()
        if current_time - file_mtime > (FILE_CLEANUP_HOURS * 3600):
            # 删除过期文件
            try:
                os.remove(file_path)
            except:
                pass
            raise HTTPException(status_code=410, detail="文件已过期")
        
        # 返回文件内容
        from fastapi.responses import FileResponse
        return FileResponse(
            path=file_path,
            filename=matching_files[0],
            media_type='application/octet-stream'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"文件下载过程中出现错误: {e}")
        raise HTTPException(status_code=500, detail="文件下载失败")

@router.delete("/{file_id}")
async def delete_file(
    file_id: str,
    current_user: User = Depends(require_admin)
):
    """
    删除临时文件（插件处理完成后调用）
    """
    try:
        # 查找匹配的文件
        matching_files = [
            f for f in os.listdir(TEMP_DIR) 
            if f.startswith(file_id + '_')
        ]
        
        if not matching_files:
            raise HTTPException(status_code=404, detail="文件未找到")
        
        file_path = os.path.join(TEMP_DIR, matching_files[0])
        
        if os.path.exists(file_path):
            os.remove(file_path)
            return {"success": True, "message": "文件删除成功"}
        else:
            raise HTTPException(status_code=404, detail="文件未找到")
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"文件删除过程中出现错误: {e}")
        raise HTTPException(status_code=500, detail="文件删除失败")

@router.post("/parts/batch-create", response_model=BatchCreateResponse)
async def batch_create_parts(
    request: BatchCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    批量创建零件
    """
    try:
        result = BatchCreateResponse(
            success=True,
            message="批量处理完成",
            total_processed=len(request.parts),
            successful_creates=0,
            skipped_duplicates=0,
            errors=[]
        )
        
        for i, part_data in enumerate(request.parts):
            try:
                # 检查是否已存在相同名称的零件
                existing_part = db.query(Part).filter(Part.name == part_data.name).first()
                if existing_part:
                    result.skipped_duplicates += 1
                    continue
                
                # 创建新零件
                new_part = Part(
                    name=part_data.name,
                    category=part_data.category,
                    description=part_data.description,
                    properties=part_data.properties,
                    image_url=part_data.image_url
                )
                
                db.add(new_part)
                db.commit()
                db.refresh(new_part)
                
                result.successful_creates += 1
                
            except Exception as e:
                db.rollback()
                result.errors.append({
                    "index": i,
                    "name": part_data.name,
                    "error": str(e)
                })
        
        # 如果有错误但也有成功的，仍然返回成功状态
        if result.errors and result.successful_creates == 0:
            result.success = False
            result.message = "批量处理失败"
        elif result.errors:
            result.message = f"批量处理完成，但有 {len(result.errors)} 个错误"
        
        return result
        
    except Exception as e:
        print(f"批量创建零件过程中出现错误: {e}")
        raise HTTPException(status_code=500, detail="批量处理失败，请稍后重试")

@router.get("/stats")
async def get_file_stats(
    current_user: User = Depends(require_admin)
):
    """
    获取临时文件统计信息（调试用）
    """
    try:
        files = []
        total_size = 0
        
        for filename in os.listdir(TEMP_DIR):
            file_path = os.path.join(TEMP_DIR, filename)
            if os.path.isfile(file_path):
                stat = os.stat(file_path)
                files.append({
                    "filename": filename,
                    "size": stat.st_size,
                    "created_at": datetime.fromtimestamp(stat.st_ctime),
                    "modified_at": datetime.fromtimestamp(stat.st_mtime)
                })
                total_size += stat.st_size
        
        return {
            "total_files": len(files),
            "total_size": total_size,
            "total_size_mb": round(total_size / 1024 / 1024, 2),
            "files": files
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")