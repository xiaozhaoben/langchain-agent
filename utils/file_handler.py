import os, hashlib
from utils.logger_handler import logger
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader,TextLoader

def get_file_md5_hex(filepath: str):  # 获取文件的md5的十六进制字符串
    if not os.path.exists(filepath):
        logger.error(f"[md5计算]文件{filepath}不存在")
        return

    if not os.path.isfile(filepath):
        logger.error(f"[md5计算]路径{filepath}不是文件")
        return

    md5_obj = hashlib.md5()

    chunk_size = 4096 #4KB分片

    try:
        with open(filepath, 'rb') as f:  # 必须二进制读取
            while chunk := f.read(chunk_size):
                md5_obj.update(chunk)

            """
            chunk = f.read(chunk_size)
            while chunk:
                md5_obj.update(chunk)
                chunk = f.read(chunk_size)
            """
            md5_hex = md5_obj.hexdigest()
            return md5_hex

    except Exception as e:
        logger.error(f"计算文件{filepath}md5失败, {str(e)}")



def listdir_with_allowed_type(path: str, allowed_types: tuple[str]): # 返回文件夹内的文件列表(允许的文件后缀)
    files = []

    if not os.path.isdir(path):
        logger.error(f"[listdir_with_allowed_type]{path}不是文件夹")
        return allowed_types

    for f in os.listdir(path):
        if f.endswith(allowed_types):
            files.append(os.path.join(path, f))

    return tuple(files)

def pdf_loader(filepath: str, passwd=None) -> list[Document]:
    """
    PDF 文件加载器
    :param filepath: PDF 文件路径
    :param passwd: PDF 密码（可选）
    :return: Document 列表
    """
    try:
        return PyPDFLoader(filepath, passwd).load()
    except Exception as e:
        logger.error(f"[PDF 加载] 加载{filepath}失败，{str(e)}")
        return []

def txt_loader(filepath: str) -> list[Document]:
    """
    TXT 文本文件加载器（UTF-8 编码）
    :param filepath: TXT 文件路径
    :return: Document 列表
    """
    try:
        # 显式指定 UTF-8 编码，并尝试多种错误处理方式
        return TextLoader(filepath, encoding='utf-8', autodetect_encoding=False).load()
    except UnicodeDecodeError:
        # 如果 UTF-8 失败，尝试自动检测编码
        logger.warning(f"[TXT 加载]{filepath}UTF-8 解码失败，尝试自动检测编码")
        try:
            return TextLoader(filepath, autodetect_encoding=True).load()
        except Exception as e:
            logger.error(f"[TXT 加载] 加载{filepath}失败，{str(e)}")
            return []
    except Exception as e:
        logger.error(f"[TXT 加载] 加载{filepath}失败，{str(e)}")
        return []