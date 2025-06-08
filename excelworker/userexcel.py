import pandas as pd 
from io import BytesIO

class ExcelWorker:
	def __init__(self):
		self.output = BytesIO()
		self.writer = pd.ExcelWriter(self.output, engine = 'xlsxwriter')

	def user_data(self, data: pd.DataFrame):
		data.to_excel(self.writer, 
					  index = False,
					  sheet_name = "Результаты")
		self.writer.close()
		self.output.seek(0)

		return (
			self.output,
			'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
			'Результат.xlsx')