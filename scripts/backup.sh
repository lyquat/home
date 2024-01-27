#!/bin/bash
now="$(date +'%Y-%m-%d')"
mysqldump -ulyquharw_backup -plyquharw_backup_password XXXXX | gzip > $HOME/backups/sql_backup-$now.sql.gz
zip -r $HOME/backups/scripts_$now.zip $HOME/scripts/ -x $HOME/scripts/logs/**\*
zip -r $HOME/backups/lyquat_$now.zip $HOME/lyquat/ -x $HOME/lyquat/__pycache__/**\*
zip -r $HOME/backups/lyquat_queries_$now.zip $HOME/lyquat_queries/ -x $HOME/lyquat_queries/__pycache__/**\*

#delete backups older than 5 days
find $HOME/backups/ -mtime +5 -type f -delete

#delete logs older than 3 days
find $HOME/scripts/logs/ -mtime +3 -type f -delete