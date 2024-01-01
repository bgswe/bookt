echo --- CREATING DATBASE ---

# initially create databases
SQL=$(envsubst < ${ROOT_DIR}/sql/scripts/create_database.sql)
psql -U postgres -c "$SQL"

psql -U postgres -d ${APPLICATION} -f ${ROOT_DIR}/sql/scripts/create_event_table.sql
psql -U postgres -d ${APPLICATION} -f ${ROOT_DIR}/sql/scripts/create_processed_message_table.sql
psql -U postgres -d ${APPLICATION} -f ${ROOT_DIR}/sql/scripts/create_message_outbox_table.sql

echo --- CREATING DATABASE "(END)" ---
