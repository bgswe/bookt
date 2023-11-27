echo --- TEARING DOWN DATABASE ---

SQL=$(envsubst < $ROOT_DIR/sql/scripts/drop_event_store_database.sql)
psql -U postgres -c "$SQL"

SQL=$(envsubst < $ROOT_DIR/sql/scripts/drop_message_outbox_database.sql)
psql -U postgres -c "$SQL"

echo --- TEARING DOWN DATABASE "(END)" ---
