echo --- TEARING DOWN DATABASE ---

# sql scripts to be ran, in order, to setup completely erase database
SCRIPTS=()

# iterate through each script and apply it to the datbase
for el in "${SCRIPTS[@]}"
do
    :
    envsubst < "$ROOT_DIR/sql/$el.sql" > tmp.sql
    psql -U postgres -d $DATABASE -f tmp.sql
    rm tmp.sql
done

SQL=$(envsubst < $ROOT_DIR/sql/database/drop.sql)
psql -U postgres -c "$SQL"

echo --- TEARING DOWN DATABASE "(END)" ---
