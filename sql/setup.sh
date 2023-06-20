echo --- CREATING DATBASE ---

# initially create database
SQL=$(envsubst < $ROOT_DIR/sql/database/create.sql)
psql -U postgres -c "$SQL"

# sql scripts to be ran, in order, to setup initial database
SCRIPTS=(
    extensions/uuid_ossp
    tables/create/user
    tables/create/organization
    # tables/create/inspection_schedule_configuration
    # tables/create/customer
    # tables/create/property
    # tables/create/inspection
    # tables/create/job
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
