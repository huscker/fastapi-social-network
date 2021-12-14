class Config:
    SECRET_KEY = '8b8a819d4276f27ffa673b45d8fb85bee7272c91549cce9b120ee88a44746d9e'
    ALGORITHM = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES = 5

    DATABASE = "postgres"
    USER = "postgres"
    PASSWORD = "postgres"
    HOST = "127.0.0.1"
    PORT = "5432"

    POSTS_PER_PAGE = 5
