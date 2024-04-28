import sqlite3


class Logger:
    def __init__(self, db_name='logs/log.db'):
        self.con = sqlite3.connect(db_name)
        self.executor = self.con.cursor()

    def __del__(self):
        self.con.commit()
        self.con.close()

    def log(self, data):
        self.executor.execute(f'''
        INSERT INTO log 
        (user_id, user_name, img_path, req_dtm) 
        VALUES ({data[0]}, '{data[1]}', '{data[2]}', '{data[3]}');
        ''')
        self.con.commit()

    @staticmethod
    def create_table(db_name='logs/log.db'):
        con = sqlite3.connect(db_name)
        executor = con.cursor()
        executor.execute('''
        CREATE TABLE IF NOT EXISTS log
        (
            id INTEGER PRIMARY KEY AUTOINCREMENT
            , user_id INTEGER
            , user_name TEXT
            , img_path TEXT
            , req_dtm TEXT
        );
        ''')
        con.commit()
        con.close()


if __name__ == '__main__':
    Logger.create_table()
    # logger = Logger()
    # data = []
    # logger.log(data=data)
