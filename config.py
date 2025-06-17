# config.py

class Config:
    SQLALCHEMY_DATABASE_URI = (
        'mssql+pyodbc://nger:S3duc2025@10.112.2.56:31433/spo'
        '?driver=ODBC+Driver+18+for+SQL+Server'
        '&Encrypt=no'  # ou 'yes' se exigido pelo servidor
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'pta2026_super_seguro'
