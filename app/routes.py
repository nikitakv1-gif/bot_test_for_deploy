import logging
from flask import Blueprint, request, render_template, current_app, send_file
import os
from werkzeug.utils import secure_filename
import pandas as pd
import plotly
from .unpack import unpack, list_to_string
from model.predict import predict
from database.db import DataBase
from io import BytesIO

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
    db = DataBase('reviews_nps')

    model = current_app.config["model"]
    tokenizer = current_app.config["tokenizer"]
    model_sent = current_app.config["model_sent"]
    emotion_tokenizer = current_app.config['emotion_tokenizer']
    excel_work = current_app.config['excel_work']

    if request.method == 'POST':
        if 'submit_score' in request.form:
            user_score = request.form.get("user_score")
            text = request.form.get('commentText')
            plus = request.form.get('prosText')
            minus = request.form.get('consText')
            result = float(request.form.get('result', 0))

            db.append_table(text, plus, minus, result, user_score)
            logger.info(f"Получен пользовательский NPS: {user_score}")
            return render_template("upload.html", selected_input_type='text', result="Спасибо за вашу оценку!")

    if request.method == "POST":
        input_type = request.form.get("inputType")
        if input_type == "file":
            if 'file' not in request.files:
                logger.error("Файл не загружен")
                return render_template("upload.html", result="Файл не загружен", selected_input_type='file', graph=None, plot_div=None)
            
            file = request.files["file"]
            if file.filename == '':
                logger.error("Не выбран файл")
                return render_template("upload.html", result="Не выбран файл", selected_input_type='file', graph=None, plot_div=None)
            
            allowed_extensions = {'.xlsx', '.xls'}
            file_ext = os.path.splitext(file.filename)[1].lower()
            if file_ext not in allowed_extensions:
                logger.error(f"Неподдерживаемый формат файла: {file_ext}")
                return render_template("upload.html", result="Ошибка: Поддерживаются только Excel файлы (.xlsx, .xls)", selected_input_type='file', graph=None, plot_div=None)
            
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
                return render_template("upload.html", result=f"Ошибка сохранения файла: {str(e)}", selected_input_type='file', graph=None, plot_div=None)
            
            try:
                logger.debug("Начало обработки файла")
                df = unpack(file_path)
                logger.debug("Файл распакован")
                
                if df is None or not isinstance(df, pd.DataFrame):
                    logger.error("Файл не удалось прочитать или он не является DataFrame")
                    return render_template("upload.html", result="Не удалось прочитать файл или неверный формат", selected_input_type='file', graph=None, plot_div=None)
                
                logger.debug(f"Колонки в DataFrame: {list(df.columns)}")
                logger.debug(f"Количество строк: {len(df)}")
                
                required_columns = ['text', 'plus', 'minus']
                missing_columns = [col for col in required_columns if col not in df.columns]
                if missing_columns:
                    logger.error(f"Отсутствуют колонки: {missing_columns}")
                    return render_template("upload.html", result=f"Ошибка: отсутствуют колонки {missing_columns}", selected_input_type='file', graph=None, plot_div=None)
                
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
                result, graph, f = predict(model, tokenizer, model_sent, emotion_tokenizer, excel_work, text, plus, minus)
                logger.debug(f"Предсказание завершено, result: {type(result)}, graph: {type(graph)}")
                
                logger.debug("Генерация Plotly-графика")
                plot_div = plotly.io.to_html(graph, full_html=False)
                logger.debug("График сгенерирован")



                current_app.config['data'] = {
                "data": f[0].getvalue(),
                "mimetype":f[1],
                "filename" : filename}
                
                return render_template("upload.html", 
                                        selected_input_type='file', 
                                        result=round(result,2), 
                                        graph=plot_div, 
                                        file_avaliable = True)
            
            except Exception as e:
                logger.error(f"Ошибка при обработке файла: {str(e)}")
                return render_template("upload.html", selected_input_type='file', result=f"Ошибка обработки: {str(e)}", graph=None, plot_div=None)
        else:
            text = [request.form.get('commentText', '')]
            plus = [request.form.get('prosText', '')]
            minus = [request.form.get('consText', '')]
            result = predict(model, tokenizer, model_sent, emotion_tokenizer, texts= text, plus_texts= plus, minus_texts=minus)

            
            return render_template("upload.html", 
                                    selected_input_type='text', 
                                    result=result,
                                    commentText=text,
                                    prosText=plus,
                                    consText=minus)
    
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

@bp.route('/download_excel')

def download_excel():
    excel_data = current_app.config.get('data')

    if not excel_data:
        return "Мы не нашли файл", 404

    return send_file(
        BytesIO(excel_data['data']),
        mimetype = excel_data['mimetype'],
        as_attachment = True,
        download_name = excel_data['filename'])
