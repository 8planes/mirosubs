cd .. && tx push --source --translations && tx pull &&  python manage.py compilemessages && git add ../locale/*/LC_MESSAGES/django.*o && git commit -m "Updated transiflex translations" && git push
