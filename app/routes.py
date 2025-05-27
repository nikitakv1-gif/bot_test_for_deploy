import logging
from flask import Blueprint, request, render_template, current_app
import os
from werkzeug.utils import secure_filename
import pandas as pd
import plotly
from .unpack import unpack, list_to_string
from model.predict import predict

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='app.log',
    filemode='a',
    encoding='utf-8')

logger = logging.getLogger(__name__)

bp = Blueprint('routes', __name__)

@bp.route("/", methods=["GET", "POST"])
def upload_file():
    result = None
    graph = None
    plot_div = None

    if request.method == "POST":
        if 'file' not in request.files:
            logger.error("Файл не загружен")
            return render_template("upload.html", result="Файл не загружен", graph=None, plot_div=None)
        
        file = request.files["file"]
        if file.filename == '':
            logger.error("Не выбран файл")
            return render_template("upload.html", result="Не выбран файл", graph=None, plot_div=None)
        
        allowed_extensions = {'.xlsx', '.xls'}
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in allowed_extensions:
            logger.error(f"Неподдерживаемый формат файла: {file_ext}")
            return render_template("upload.html", result="Ошибка: Поддерживаются только Excel файлы (.xlsx, .xls)", graph=None, plot_div=None)
        
        try:
            logger.debug("Начало сохранения файла")
            os.makedirs("uploads", exist_ok=True)
            filename = secure_filename(file.filename)
            logger.debug(f"Имя файла: {filename}")
            file_path = os.path.join("uploads", filename)
            logger.debug(f"Путь для сохранения: {file_path}")
            file.save(file_path)
            logger.debug(f"Файл успешно сохранён: {file_path}")
        except Exception as e:
            logger.error(f"Ошибка сохранения файла: {str(e)}")
            return render_template("upload.html", result=f"Ошибка сохранения файла: {str(e)}", graph=None, plot_div=None)
        
        try:
            logger.debug("Начало обработки файла")
            df = unpack(file_path)
            logger.debug("Файл распакован")
            
            if df is None or not isinstance(df, pd.DataFrame):
                logger.error("Файл не удалось прочитать или он не является DataFrame")
                return render_template("upload.html", result="Не удалось прочитать файл или неверный формат", graph=None, plot_div=None)
            
            logger.debug(f"Колонки в DataFrame: {list(df.columns)}")
            logger.debug(f"Количество строк: {len(df)}")
            
            required_columns = ['text', 'plus', 'minus']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                logger.error(f"Отсутствуют колонки: {missing_columns}")
                return render_template("upload.html", result=f"Ошибка: отсутствуют колонки {missing_columns}", graph=None, plot_div=None)
            
            logger.debug("Преобразование столбца 'plus'")
            plus = df['plus'].fillna('').apply(list_to_string).to_list()
            logger.debug(f"Преобразовано {len(plus)} строк в 'plus'")
            
            logger.debug("Преобразование столбца 'minus'")
            minus = df['minus'].fillna('').apply(list_to_string).to_list()
            logger.debug(f"Преобразовано {len(minus)} строк в 'minus'")
            
            logger.debug("Преобразование столбца 'text'")
            text = df['text'].fillna('').apply(list_to_string).to_list()
            logger.debug(f"Преобразовано {len(text)} строк в 'text'")
            
            logger.debug("Запуск предсказания")
            model = current_app.config["model"]
            tokenizer = current_app.config["tokenizer"]
            model_sent = current_app.config["model_sent"]
            emotion_tokenizer = current_app.config['emotion_tokenizer']
            result, graph = predict(model, tokenizer, model_sent, emotion_tokenizer, text, plus, minus)
            logger.debug(f"Предсказание завершено, result: {type(result)}, graph: {type(graph)}")
            
            logger.debug("Генерация Plotly-графика")
            plot_div = plotly.io.to_html(graph, full_html=False)
            logger.debug("График сгенерирован")
            
            return render_template("upload.html", result=round(result,2), graph=plot_div, plot_div=plot_div)
        
        except Exception as e:
            logger.error(f"Ошибка при обработке файла: {str(e)}")
            return render_template("upload.html", result=f"Ошибка обработки: {str(e)}", graph=None, plot_div=None)
    
    return render_template("upload.html", result=None, graph=None, plot_div=None)

@bp.route('/preview-excel', methods = ['POST'])
def preview_file():
    file = request.files.get('file')

    if not file or not file.filename.endswith(('.xls','.xlsx')):
        return 'Неверный формат файла', 400

    try:
        df = pd.read_excel(file)
        html = df.head(10).to_html(classes='table table-bordered', index=False)
        return html
    except Exception as e:
        return f'Ошибка при чтении файла: {e}', 400