# DataStreamHandler
 
## Project Description 
This project DataStreamHandler is a management system for databases receiving JSON files.
It receives and stores JSON files. When the files have any values missing, the proccess of 
uploading a CSV file is needed. After uploading the correct CSV file with the correct values
then the system will automatically update the database with the correct information.

## Required Libraries
To run this project, it is required that you install the following libraries:

```python
pip install flask
```
```python
pip install Flask-SQLAlchemy
```
```python
pip install pandas
```
```python
pip install mysql-connector-python
```
```python
pip install plotly
```
## Database Connection Instructions

1. Make sure that you have MYSQL installed in your machine. If needed it can be downloaded at 
the official MySQL website.

2. If MYSQL is installed in your machine then open you command prompt or terminal and connect to MYSQL through the following command:

```python
mysql -u root -p
```
Enter your password when asked to in order to access the database.

3. Following, execute these SQL commands in order to create a new user and grant privileges:

```python
CREATE USER IF NOT EXISTS 'adm_radix'@'localhost' IDENTIFIED BY 'radix';
GRANT ALL PRIVILEGES ON * . * TO 'adm_radix'@'localhost';
FLUSH PRIVILEGES;
```
After running these commands, you will have established a user to
complete the connection.

4. Now to create the database run the following SQL commands:

```python
CREATE SCHEMA IF NOT EXISTS `dbDataStreamHandler` DEFAULT CHARACTER SET utf8;
USE `dbDataStreamHandler`;
```
Now you are ready to run the project.
