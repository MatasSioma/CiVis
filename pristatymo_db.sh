#!/bin/bash
set -e

##
## VISI asmens kodai'ai 11111111111111, 222222222222, 33333333, .... 
## VISI USERIU PASWORDAI - "123"
##

DUMP_FILE="civis_dump_2026-05-27.dump"
CONTAINER="db"
DB_NAME="civis"
DB_USER="civis"

if [ ! -f "$DUMP_FILE" ]; then
    echo "Error: $DUMP_FILE not found in current directory."
    exit 1
fi

echo "Copying dump into container..."
docker cp "$DUMP_FILE" "$CONTAINER:/tmp/$DUMP_FILE"

echo "Dropping and recreating database..."
docker exec "$CONTAINER" psql -U "$DB_USER" -d postgres -c "DROP DATABASE IF EXISTS $DB_NAME;"
docker exec "$CONTAINER" psql -U "$DB_USER" -d postgres -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"

echo "Restoring dump..."
docker exec "$CONTAINER" pg_restore -U "$DB_USER" -d "$DB_NAME" "/tmp/$DUMP_FILE"

echo "Cleaning up..."
docker exec "$CONTAINER" rm "/tmp/$DUMP_FILE"

echo "Done! Database '$DB_NAME' restored successfully."
