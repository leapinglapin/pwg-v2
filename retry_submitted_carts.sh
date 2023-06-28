while true
do
  ./manage.py RetrySubmittedCarts
  date +"%H:%M:%S"
  echo "Waiting 2 hours"
  sleep 2h
done