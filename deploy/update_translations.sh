date && \
git pull && \
cd .. && \
python manage.py makemessages -i deploy\* -i media\js\closure-library\* -i media/js/mirosubs-calcdeps.js.py -a && \
python manage.py makemessages -d djangojs -i deploy\* -i media\js\closure-library\* -i media/js/mirosubs-calcdeps.js.py -a && \
echo "pushing to transifex" && \
tx push --source && \
echo "pulling from transiflex" && \
tx pull &&  echo "compiling messages" && \
python manage.py compilemessages && \
echo "adding to git" && \
git add /locale/*/LC_MESSAGES/django.*o && \
echo "committing to rep" && \
git commit -m "Updated transiflex translations -- through update_translations.sh" && \
echo "pushing to rep" && \
date && \
git push 
# in order for this to work, you must have a ~/.transifexrc file (kept out of source control since it requires a passwords)
