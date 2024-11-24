To develop... 

```
python manage.py run -h 0.0.0.0 -p 5000 --debug
```


For production run 

```
gunicorn -k gevent -w 1 --bind 0.0.0.0:5000 --access-logfile - frontEnd:app
```

