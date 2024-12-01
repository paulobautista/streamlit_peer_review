### How to Launch Streamlit

1. SSH into the AWS EC2 `ssh -i /Users/paulobautista/Documents/KEYS/streamlit-agent.pem ubuntu@47.129.207.175`
2. Activate the virtual environment with `source myenv/bin/activate`
3. Go to the app directory with `cd agent-streamlit`
3. Launch app `streamlit run app.py --server.port 8501 --server.enableCORS false --server.enableXsrfProtection false --server.address 0.0.0.0`


### Connecting to RDS

this was the Custom MYSQL/Aurora if you need it `sg-000d4a7a82e21805f`


### Creating Tables

`agent_actions`
create_table_query = """
CREATE TABLE agent_actions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    document_id CHAR(36),
    flag_for_review BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    input_text TEXT,
    user_decision ENUM('bad', 'no change needed', 'save changes')
);
"""

`documents`
- id (please generate uuid)
- index (please sequentially make)
- markdown
- file_path
- created_at
-
