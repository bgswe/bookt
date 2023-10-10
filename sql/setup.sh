echo --- CREATING DATBASE ---

# initially create database
SQL=$(envsubst < $ROOT_DIR/sql/database/create.sql)
psql -U postgres -c "$SQL"

# sql scripts to be ran, in order, to setup initial database
SCRIPTS=(
    extensions/uuid_ossp
    tables/create/event
    tables/create/message_outbox
    tables/create/processed_messages
)

# iterate through each script and apply it to the database
for el in "${SCRIPTS[@]}"
do
    :
    envsubst < "$ROOT_DIR/sql/$el.sql" > tmp.sql
    psql -U postgres -d $DATABASE -f tmp.sql
    rm tmp.sql
done

echo --- CREATING DATABASE "(END)" ---
