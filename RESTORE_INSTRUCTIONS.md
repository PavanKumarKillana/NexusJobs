# Database Restore Instructions

If you get a new laptop or your current laptop crashes, don't worry! Your entire codebase and database are backed up in this GitHub repository. 

Follow these exact steps on your new laptop to get everything running exactly as it is right now.

## 1. Setup the Project
1. Install Python and MySQL on your new laptop.
2. Clone this repository:
   ```bash
   git clone git@github.com:PavanKumarKillana/NexusJobs.git
   cd NexusJobs
   ```
3. Set up your virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

## 2. Restore the Database
Your database has been backed up to the file named `nexusjobs_db_backup.sql`.

1. Open MySQL in your terminal:
   ```bash
   mysql -u root -p
   ```
   *(Enter your root password when prompted)*

2. Inside MySQL, create the empty database:
   ```sql
   CREATE DATABASE nexusjobs_db;
   EXIT;
   ```

3. Import the backup data into your newly created database by running this command in your normal terminal (NOT inside MySQL):
   ```bash
   mysql -u root -p nexusjobs_db < nexusjobs_db_backup.sql
   ```

## 3. Run the Server
Now your entire database is fully restored! Just start the server:
```bash
python manage.py runserver
```
Your jobs and categories will all be there!
