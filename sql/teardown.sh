echo --- TEARING DOWN DATABASE ---

SQL=$(envsubst < $ROOT_DIR/sql/scripts/drop_database.sql)
psql -U postgres -c "$SQL"

echo --- TEARING DOWN DATABASE "(END)" ---
