from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

#app = Flask(__name__)
#db = SQLAlchemy(app)

#connect to docker postgres db 
engine = create_engine('postgresql://postgres:1234@database:5432/postgres') # <-- For Container
# engine = create_engine('postgresql://postgres:1234@localhost:5432/postgres')

Session = sessionmaker(bind=engine)

session = Session()

#init db; Fill with data dump if empty
# try:
#     # test = engine.execute('SELECT * FROM CURRENT_STATUS;').fetchall()
#     # if len(test) > 0:
#     #     print("Test successful:",test)
#     # else:
#     sql_statement = open("./db/init.sql", "r").read()
#     engine.execute(sql_statement)
# except:
#     sql_statement = open("./db/init.sql", "r").read()
#     engine.execute(sql_statement)

from app import receiver