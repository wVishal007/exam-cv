from database.db import text,engine

def create_user(name,email,password):
    query = text(
        """
        INSERT INTO users  
        (name,email,password)
        VALUES (:name,:email,:password)

        """
    )
    with engine.begin() as conn:
        conn.execute(query,{
            "name":name,
            "email":email,
            "password":password,
        })

def login_user(email:str):
    query = text(
    '''SELECT user_id,password FROM users WHERE (email = :email)
    '''
    )
    with engine.begin() as conn:
        result = conn.execute(query,{
            'email':email
        })
        return result.fetchone()