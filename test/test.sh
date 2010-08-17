ab2 -n 1000 -c 20 -p r1.txt -H 'X_REQUESTED_WITH:XMLHttpRequest' http://mirosubs.example.com:8000/widget/rpc/xhr/show_widget
ab2 -n 1000 -c 20 -p r2.txt -H 'X_REQUESTED_WITH:XMLHttpRequest' http://mirosubs.example.com:8000/widget/rpc/xhr/show_widget
ab2 -n 1000 -c 20 -p r3.txt -H 'X_REQUESTED_WITH:XMLHttpRequest' http://mirosubs.example.com:8000/widget/rpc/xhr/fetch_translations