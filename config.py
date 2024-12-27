class Config:
    # Remplacez les informations suivantes par votre configuration MySQL
    SQLALCHEMY_DATABASE_URI = 'mysql://root:123456@localhost/ocr_auth_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = 'super-secret-key'
    DEBUG = True
