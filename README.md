`OHLC` live `Binance` data processor written in Python: define your own indicators, strategies, trade methods. 

This is definitely not the best way: too expensive - pull data from Binance, convert it to Pandas dataframe, manipulate dataframe, all in async loop based on time intervals defined by user, it runs fine on `t2.micro` AWS instance with a look back of a month (see `terraform` folder for a simple setup).

Get acquanted with `binance.yaml` settings file, ensure you have `Binance` key/secret ready. Entrypoint is `binance_trade.py`. 

 