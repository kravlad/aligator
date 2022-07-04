from datetime import datetime, timedelta



date = datetime.now() - timedelta(hours=24)
x = date.strftime('%d/%m/%Y')

pass
