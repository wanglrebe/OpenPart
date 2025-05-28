# backend/app/api/admin/image_download.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
import os
import uuid
import aiohttp
import asyncio
from urllib.parse import urlparse
import ipaddress
from PIL import Image
import io
from app.core.database import get_db
from app.models.part import Part
from app.auth.middleware import require_admin
from app.auth.models import User
from pydantic import BaseModel, HttpUrl

router = APIRouter()

# 配置常量
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
UPLOAD_DIR = "static/images/parts"
ALLOWED_CONTENT_TYPES = {
    'image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'
}
ALLOWED_PORTS = {80, 443, 8080, 8443}
REQUEST_TIMEOUT = 30  # 30秒超时

# 私有网络黑名单
BLOCKED_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),    # localhost
    ipaddress.ip_network("10.0.0.0/8"),     # 私有网络
    ipaddress.ip_network("172.16.0.0/12"),  # 私有网络
    ipaddress.ip_network("192.168.0.0/16"), # 私有网络
    ipaddress.ip_network("169.254.0.0/16"), # 链路本地
    ipaddress.ip_network("224.0.0.0/4"),    # 多播
    ipaddress.ip_network("240.0.0.0/4"),    # 保留
]

# 确保上传目录存在
os.makedirs(UPLOAD_DIR, exist_ok=True)

class ImageDownloadRequest(BaseModel):
    part_id: int
    image_url: HttpUrl
    replace_existing: bool = True

class ImageDownloadResponse(BaseModel):
    success: bool
    message: str
    image_url: Optional[str] = None
    file_size: Optional[int] = None
    content_type: Optional[str] = None
    replaced_existing: bool = False
    old_image_url: Optional[str] = None

def is_url_safe(url: str) -> tuple[bool, str]:
    """
    检查URL是否安全
    返回: (is_safe: bool, error_message: str)
    """
    try:
        parsed = urlparse(url)
        
        # 1. 检查协议
        if parsed.scheme not in ('http', 'https'):
            return False, "只支持 HTTP 和 HTTPS 协议"
        
        # 2. 检查端口
        port = parsed.port
        if port is not None and port not in ALLOWED_PORTS:
            return False, f"不允许的端口: {port}"
        
        # 3. 检查主机名
        hostname = parsed.hostname
        if not hostname:
            return False, "无效的主机名"
        
        # 4. 尝试解析IP地址
        try:
            ip = ipaddress.ip_address(hostname)
            # 检查是否为私有/本地地址
            for blocked_network in BLOCKED_NETWORKS:
                if ip in blocked_network:
                    return False, f"不允许访问的IP地址: {ip}"
        except ipaddress.AddressValueError:
            # 不是IP地址，是域名，进行域名检查
            if hostname.lower() in ['localhost', 'localhost.localdomain']:
                return False, "不允许访问 localhost"
            
            # 检查域名格式
            if '..' in hostname or hostname.startswith('.') or hostname.endswith('.'):
                return False, "无效的域名格式"
        
        return True, ""
        
    except Exception as e:
        return False, f"URL 解析错误: {str(e)}"

def validate_image_content(content: bytes, content_type: str) -> tuple[bool, str]:
    """
    验证图片内容
    返回: (is_valid: bool, error_message: str)
    """
    try:
        # 检查文件大小
        if len(content) > MAX_IMAGE_SIZE:
            return False, f"文件大小超过限制 ({MAX_IMAGE_SIZE // 1024 // 1024}MB)"
        
        # 检查内容类型
        if content_type.lower() not in ALLOWED_CONTENT_TYPES:
            return False, f"不支持的图片格式: {content_type}"
        
        # 验证图片文件头部
        try:
            with Image.open(io.BytesIO(content)) as img:
                # 验证图片可以正常打开
                img.verify()
                
                # 检查图片尺寸（可选）
                if hasattr(img, 'size'):
                    width, height = img.size
                    if width > 4000 or height > 4000:
                        return False, "图片尺寸过大"
                
        except Exception as e:
            return False, f"无效的图片文件: {str(e)}"
        
        return True, ""
        
    except Exception as e:
        return False, f"图片验证错误: {str(e)}"

async def download_image_from_url(url: str) -> tuple[bool, bytes, str, str]:
    """
    从URL下载图片
    返回: (success: bool, content: bytes, content_type: str, error_message: str)
    """
    try:
        timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, allow_redirects=True, max_redirects=5) as response:
                # 检查HTTP状态码
                if response.status != 200:
                    return False, b'', '', f"HTTP错误: {response.status}"
                
                # 检查内容类型
                content_type = response.headers.get('content-type', '').lower()
                if not any(allowed_type in content_type for allowed_type in ALLOWED_CONTENT_TYPES):
                    return False, b'', '', f"不支持的内容类型: {content_type}"
                
                # 检查内容长度
                content_length = response.headers.get('content-length')
                if content_length and int(content_length) > MAX_IMAGE_SIZE:
                    return False, b'', '', "文件大小超过限制"
                
                # 读取内容
                content = await response.read()
                
                return True, content, content_type, ""
                
    except asyncio.TimeoutError:
        return False, b'', '', "下载超时"
    except Exception as e:
        return False, b'', '', f"下载失败: {str(e)}"

def resize_and_save_image(content: bytes, file_path: str) -> tuple[bool, str]:
    """
    调整图片大小并保存
    返回: (success: bool, error_message: str)
    """
    try:
        with Image.open(io.BytesIO(content)) as img:
            # 转换RGBA到RGB（如果需要）
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                if img.mode in ('RGBA', 'LA'):
                    background.paste(img, mask=img.split()[-1])
                img = background
            
            # 调整大小（保持宽高比）
            img.thumbnail((800, 600), Image.Resampling.LANCZOS)
            
            # 保存为JPEG格式
            img.save(file_path, 'JPEG', optimize=True, quality=85)
            
        return True, ""
        
    except Exception as e:
        return False, f"图片处理失败: {str(e)}"

@router.post("/download", response_model=ImageDownloadResponse)
async def download_image(
    request: ImageDownloadRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    为指定零件下载图片
    """
    try:
        # 1. 验证零件是否存在
        part = db.query(Part).filter(Part.id == request.part_id).first()
        if not part:
            raise HTTPException(status_code=404, detail="零件未找到")
        
        # 2. 检查URL安全性
        is_safe, safety_error = is_url_safe(str(request.image_url))
        if not is_safe:
            raise HTTPException(status_code=400, detail=f"URL安全检查失败: {safety_error}")
        
        # 3. 检查是否已有图片
        old_image_url = None
        replaced_existing = False
        if part.image_url and not request.replace_existing:
            raise HTTPException(
                status_code=409, 
                detail="零件已有图片，如需替换请设置 replace_existing=true"
            )
        elif part.image_url:
            old_image_url = part.image_url
            replaced_existing = True
        
        # 4. 下载图片
        success, content, content_type, download_error = await download_image_from_url(str(request.image_url))
        if not success:
            raise HTTPException(status_code=400, detail=f"图片下载失败: {download_error}")
        
        # 5. 验证图片内容
        is_valid, validation_error = validate_image_content(content, content_type)
        if not is_valid:
            raise HTTPException(status_code=400, detail=f"图片验证失败: {validation_error}")
        
        # 6. 生成文件名和路径
        file_extension = ".jpg"  # 统一保存为JPEG
        filename = f"part_{request.part_id}_{uuid.uuid4().hex}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        # 7. 处理并保存图片
        save_success, save_error = resize_and_save_image(content, file_path)
        if not save_success:
            raise HTTPException(status_code=500, detail=f"图片保存失败: {save_error}")
        
        # 8. 删除旧图片文件（如果存在）
        if replaced_existing and old_image_url:
            try:
                old_file_path = old_image_url.lstrip('/')
                if os.path.exists(old_file_path):
                    os.remove(old_file_path)
            except Exception as e:
                print(f"删除旧图片失败: {e}")  # 记录日志但不影响主流程
        
        # 9. 更新数据库
        new_image_url = f"/static/images/parts/{filename}"
        part.image_url = new_image_url
        db.commit()
        db.refresh(part)
        
        # 10. 获取文件信息
        file_size = os.path.getsize(file_path)
        
        return ImageDownloadResponse(
            success=True,
            message="图片下载成功",
            image_url=new_image_url,
            file_size=file_size,
            content_type="image/jpeg",
            replaced_existing=replaced_existing,
            old_image_url=old_image_url
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"图片下载过程中出现未预期错误: {e}")
        raise HTTPException(status_code=500, detail="图片下载失败，请稍后重试")

@router.get("/download/test")
async def test_url_safety(
    url: str,
    current_user: User = Depends(require_admin)
):
    """
    测试URL是否安全（调试用）
    """
    is_safe, error_message = is_url_safe(url)
    return {
        "url": url,
        "is_safe": is_safe,
        "error_message": error_message if not is_safe else None
    }