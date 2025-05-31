import os
import pandas as pd 
import logging

import pandas as pd
from io import StringIO
logger = logging.getLogger(__name__)

def unpack(file_path):
    """Функция для чтения Excel файлов"""
    try:
        # Пробуем прочитать файл с помощью openpyxl (для .xlsx)
        try:
            df = pd.read_excel(file_path, engine='openpyxl')
            logger.debug("[DEBUG] Read like Excel (.xlsx)")
            return df
        except:
            # Пробуем прочитать с помощью xlrd (для старых .xls)
            try:
                df = pd.read_excel(file_path, engine='xlrd')
                logger.debug("[DEBUG] Read like Excel (.xls)")
                return df
            except Exception as e:
                logger.error(f"[DEBUG] Error reading excel: {str(e)}")
                return None
    except Exception as e:
        logger.error(f"[DEBUG] Error in unpack_excel(): {str(e)}")
        return None
def list_to_string(texts):
    # # Проверка на None или пустые значения
    # if tokens is None:
    #     return ""
    
    # # Если уже строка - возвращаем как есть
    # if isinstance(tokens, str):
    #     return tokens.strip() if tokens else ""
    
    # # Если это список или другой итерируемый объект
    # try:
    #     # Фильтруем None и пустые строки
    #     filtered_tokens = [str(item).strip() for item in tokens if item is not None and str(item).strip()]
        
    #     # Если после фильтрации ничего не осталось
    #     if not filtered_tokens:
    #         return ""
            
    #     # Объединяем через пробел
    #     return ' '.join(filtered_tokens)
        
    # except (TypeError, AttributeError):
    #     # Если не итерируемый объект - просто преобразуем в строку
    #     return str(tokens).strip() if tokens is not None else ""
    """Преобразует Series в правильный формат для модели"""
    # Преобразуем в список строк, фильтруем None и пустые значения
    if isinstance(texts, str):
        return texts
    
    # Если передан список
    if isinstance(texts, (list, tuple, pd.Series)):
        # Фильтрация None и нестроковых значений
        return " ".join(texts)
    # Для других типов (числа, даты и т.д.)
    return str(texts)
