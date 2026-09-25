from database.tables.resume_analysis_table import create_resume_analysis_table
from database.tables.resume_table import create_resume_table
from database.tables.user_table import create_users_table
from database.tables.resume_version_table import create_resume_version_table
from database.tables.generated_resume_table import create__generated_resume_table
def start_db():
    create_users_table()
    create_resume_table()
    create_resume_analysis_table()
    create_resume_version_table()
    create__generated_resume_table()

    print("db started")
    # return